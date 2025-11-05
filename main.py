import asyncio
from contextlib import asynccontextmanager
from dataclasses import *
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from starlette.responses import JSONResponse

from models_sql import *
from database import init_db, get_session
from openai_client import *
from models import *
from mock import *
import uvicorn
import service as crud
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # If init_db is synchronous, run it in a separate thread and await completion
    await asyncio.to_thread(init_db)
    # If init_db is asynchronous, use: await init_db()
    yield
app = FastAPI(title="Health Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
def chat_with_user(request: ChatMessage):
    user_message = request.message

    history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    response = chat_with_openai(messages)

    assistant_message = response.choices[0].message
    history.append({"role": "assistant", "content": assistant_message.content})

    return {
        "response": {
            "role": assistant_message.role,
            "content": assistant_message.content
        }
    }

@app.post("/profiles")
def create_profile(data: UserProfileCreate, session: Session = Depends(get_session)):
    return crud.create_user_profile(session, data)

@app.get("/profiles/{user_id}")
def read_profile(user_id: str, session: Session = Depends(get_session)):
    return crud.get_user_profile(session, user_id)

@app.get("/profiles")
def list_profiles(session: Session = Depends(get_session)):
    return crud.get_all_profiles(session)

@app.put("/profiles/{user_id}")
def update_profile(user_id: str, updates: UserProfileUpdate, session: Session = Depends(get_session)):
    return crud.update_user_profile(session, user_id, updates)

@app.delete("/profiles/{user_id}")
def delete_profile(user_id: str, session: Session = Depends(get_session)):
    return crud.delete_user_profile(session, user_id)

@app.get("/users/{user_id}/meal-plans", response_model=List[MealPlanData])
def get_meal_plans(user_id: str, session: Session = Depends(get_session)):
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
    return [mp.get_data() for mp in user_profile.meal_plans]

@app.post("/users/{user_id}/meal-plans", response_model=MealPlanData)
def create_meal_plan(user_id: str, user_options: dict, session: Session = Depends(get_session)):
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    new_plan = create_meal(user_profile, user_options)
    crud.add_meal_plan(session, user_profile, MealPlanData(**new_plan))
    return new_plan

mockMessages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Nam"},
    {"role": "assistant", "content": "Nhập chiều cao"},
    {"role": "user", "content": "212"},
    {"role": "user", "content": "Nhập cân nặng"},
    {"role": "user", "content": "70"},
]

@app.get("/chat")
def chat_with_user():
    return {"response": create_meal(HEALTH_DATA, USER_OPTIONS)}

@app.get("/chat/user_summary")
def chat_user_summary():
    return {"response": summary_user_chat()}

@app.post("/analyze-result")
def analyze_result(data: UserProfileCreate, session: Session = Depends(get_session)):
    crud.upsert_user_profile(session, data)
    result = analyze_health(data.model_dump_json())
    return {"response": result}

@app.post("/analyze_image")
async def analyze(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        # result_json = analyze_image(image_bytes)
        # print("OpenAI response:", result_json)
        # result = json.loads(result_json)
        result = analyze_image(image_bytes)
        return JSONResponse(content={"result": result})
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Không thể phân tích kết quả từ OpenAI"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# result_analyze_image
# [
#   {
#     "name": "Pizza",
#     "calories": 285,
#     "bounding_box": [120, 80, 300, 250] - [xmin, ymin, xmax, ymax]
#   }
# ]

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
