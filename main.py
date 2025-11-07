import base64
import re
from fastapi import Form, File, UploadFile
from fastapi import FastAPI, Depends, HTTPException
from openai_client import *
from models import *
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Health Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    user_input: str


@app.post("/chat/{user_id}")
def chat_with_user(user_id: str, request: ChatRequest):
    content = chat_with_open_ai(user_id, request.user_input)
    return {"role": "assistant", "content": content}


@app.get("/chat_history/{user_id}", response_model=ChatHistory)
async def get_chat_history(user_id: str) -> ChatHistory:
    history = SQLChatMessageHistory(connection_string=DATABASE_URL, session_id=user_id)
    messages = history.messages

    chat_log: List[ChatMessage] = []
    for msg in messages:
        clean_message = re.sub(r'#thamkhao.*?#thamkhao', '', msg.content, flags=re.DOTALL)
        chat_log.append(
            ChatMessage(
                role=msg.type,
                content=clean_message.strip(),
                timestamp=getattr(msg, "timestamp", None),
            )
        )

    return ChatHistory(user_id=user_id, messages=chat_log, message_count=len(chat_log))


@app.post("/reset_chat/{user_id}")
async def reset_chat(user_id: str):
    history = SQLChatMessageHistory(connection_string=DATABASE_URL, session_id=user_id)
    history.clear()
    return {"message": f"Chat history for {user_id} cleared."}


@app.post("/daily-meal", response_model=DailyMealResponse)
def generate_daily_meal(request: DailyMealRequest):
    """
    Generate a personalized daily meal plan using OpenAI,
    structured and validated with the DailyMealResponse model.
    """
    prompt = f"""
    Based on this user's profile and summary:
    Name: {request.user_profile.name}
    Age: {request.user_profile.age}
    Weight: {request.user_profile.weight} kg
    Height: {request.user_profile.height} cm
    Summary: {request.analyze_result}
    """

    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": daily_meal_system},
            {"role": "user", "content": prompt}
        ],
        response_format=DailyMealResponse  # 👈 auto-parse to model
    )
    data = json.loads(response.choices[0].message.content)
    return DailyMealResponse(**data)


@app.get("/chat/user_summary")
def chat_user_summary():
    return {"response": summary_user_chat()}


@app.post("/analyze-health", response_model=AnalyzeResult)
async def analyze_health(
        name: str = Form(...),
        age: int = Form(...),
        weight: str = Form(...),
        height: str = Form(...),
        blood_test: Optional[UploadFile] = File(None),
        urine_test: Optional[UploadFile] = File(None)
):
    def file_to_base64(file: Optional[UploadFile]) -> Optional[str]:
        """Convert uploaded file to base64 string."""
        if not file:
            return None
        contents = file.file.read()
        return base64.b64encode(contents).decode("utf-8")

    print("Received:", name, weight, height, blood_test, urine_test)
    blood_b64 = file_to_base64(blood_test)
    urine_b64 = file_to_base64(urine_test)

    content = [{"type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{blood_b64}"}
                },
               # {"type": "image_url",
               #  "image_url": {"url": f"data:image/jpeg;base64,{urine_b64}"}
               #  }
               ]
    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": analyze_system},
            {"role": "user",
             "content": f"Tên: {name}, Cân nặng: {weight}, Chiều cao: {height}, Tuổi: {age}"},
            # {"role": "user", "content": content},
        ],
        response_format=AnalyzeResult,
        temperature=0.2
    )
    data = json.loads(response.choices[0].message.content)
    print(data)
    return AnalyzeResult(**data)


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
