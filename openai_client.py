import base64
import io
import json

import openai
from PIL import Image
from openai import OpenAI, APIError, RateLimitError, Timeout
from openai.types import Image
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

from constants import *
from models import *
from models_sql import UserProfile

client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key="sk-e33XdbP5qVj57ONqvLnrpw"
)

history = []


def analyze_health(health_data: dict) -> dict:
    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_content_analyst},
            {"role": "user", "content": f"Đây là dữ liệu người dùng: {health_data}"},
        ],
        response_format=HealthAnalysis,
        temperature=0.2
    )
    return json.loads(response.choices[0].message.content)


def create_meal(user_profile: UserProfile, user_options: dict) -> dict:
    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_MEAL_PLAN},
            {"role": "user",
             "content": f"Đây là dữ liệu người dùng: {user_profile.model_dump_json()}, options: {user_options}"},
        ],
        temperature=0.6,
        response_format=MealPlanData
    )
    return json.loads(response.choices[0].message.content)


@retry(
    retry=retry_if_exception_type((APIError, RateLimitError, Timeout, ConnectionError)),
    wait=wait_random_exponential(multiplier=1, max=20),
    stop=stop_after_attempt(3),
    reraise=True
)
def chat_with_openai(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2
        )

        message = response.choices[0].message

        # If model calls a tool
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                if tool_name == "calculate_bmi":
                    height = tool_args.get("height")
                    weight = tool_args.get("weight")

                    if not height or not weight:
                        raise ValueError("Missing height or weight for BMI calculation.")

                    bmi = weight / ((height / 100) ** 2)

                    assistant_message = {
                        "role": "assistant",
                        "content": f"Chỉ số BMI của bạn là {bmi:.1f}."
                    }
                    messages.append(assistant_message)
                    history.append(assistant_message)

                    messages.append({
                        "role": "user",
                        "content": "Tạo thực đơn hàng ngày dựa trên thông tin cung cấp"
                    })

                    # Continue chat
                    followup = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.2
                    )
                    return followup

        return response

    except (APIError, RateLimitError, Timeout) as e:
        print(f"OpenAI API error: {e}. Retrying...")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "error": str(e),
            "message": "Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau."
        }


def summary_user_chat():
    """
    Tóm tắt các câu hỏi của user trong đoạn hội thoại, gom nhóm theo chủ đề.
    Trả về danh sách JSON gồm các phần tử: {"summary_sentence": ..., "source_index": ...}
    """

    # Lọc ra các câu hỏi của user
    user_questions = [
        {"index": i, "content": msg["content"]}
        for i, msg in enumerate(history)
        if msg["role"] == "user"
    ]

    # Tạo prompt yêu cầu tóm tắt
    prompt = (
        "Hãy tóm tắt ngắn gọn các câu hỏi của người dùng trong đoạn hội thoại.\n"
        "Nếu nhiều câu hỏi cùng chủ đề, hãy gộp thành 1-2 câu summary.\n"
        "Mỗi summary phải gắn source_index tới câu hỏi gốc gần nghĩa nhất.\n"
        "Mỗi summary phải giống như đang trả lời trực tiếp trong hội thoại, "
        "không dùng 'người dùng hỏi' hay 'trợ lý trả lời'.\n"
        "Chỉ tóm tắt câu hỏi của user, không tóm tắt câu trả lời của assistant.\n"
        "Trả lời dưới dạng JSON list với các trường: summary_sentence, source_index.\n\n"
        f"Các câu hỏi của user:\n{user_questions}\n"
        "Chỉ trả lời về JSON, không giải thích thêm."
    )

    # Gọi OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    # Trích xuất và chuyển đổi JSON
    content = response['choices'][0]['message']['content']
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("❌ Lỗi định dạng JSON từ phản hồi.")
        return []


def build_prompt():
    return """
Bạn là trợ lý nhận diện món ăn. Khi được cung cấp một hình ảnh, hãy xác định tất cả các món ăn có thể nhìn thấy.

Với mỗi món ăn, hãy trả về:
- Tên món ăn
- Lượng calo ước tính (gần đúng)
- Tọa độ khung bao (bounding box) theo định dạng [x_min, y_min, x_max, y_max]

Trả lời bằng định dạng JSON như sau:
[
  {
    "name": "cơm",
    "estimated_weight": 150,
    "calories": 200,
    "bounding_box": [120, 80, 300, 250]
  },
  {
    "name": "thịt gà",
    "estimated_weight": 153,
    "calories": 212,
    "bounding_box": [320, 103, 450, 256]
  }
]

Chỉ bao gồm các món ăn. Không bao gồm các vật thể nền hoặc con người.
"""


def analyze_image(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    prompt = build_prompt()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia dinh dưỡng."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
            ]}
        ]
    )
    return response.choices[0].message.content
