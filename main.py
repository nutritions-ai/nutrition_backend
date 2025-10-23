from fastapi import FastAPI
from openai_client import *
from models import *
from mock import *
import uvicorn
app = FastAPI(title="Health Chatbot API")

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
    return {"response":create_meal(health_data, user_options)}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


