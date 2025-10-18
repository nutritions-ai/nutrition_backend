from openai import OpenAI
import tool_functions
import json
from tool_functions import *

client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key="sk-e33XdbP5qVj57ONqvLnrpw"
)

SYSTEM_PROMPT = """
Bạn là một Trợ lý Xác thực Dữ liệu Y tế và Lập Kế hoạch Sức khỏe cá nhân.

🎯 Nhiệm vụ của bạn:
1. Giới thiệu bản thân ngắn gọn, thân thiện.
   - Giải thích rằng bạn sẽ thu thập và kiểm tra thông tin sức khỏe của người dùng để tạo kế hoạch ăn uống cá nhân hóa.

2. Lần lượt hỏi người dùng từng thông tin sức khỏe.

Thông tin cần thu thập:
- Giới tính: bắt buộc
- Tuổi: tùy chọn
- Chiều cao: bắt buộc
- Cân nặng: bắt buộc

3. Khi đã thu thập đầy đủ dữ liệu bắt buộc:
   - Tính chỉ số BMI
   - Sau đó lập kế hoạch ăn uống trong 1 ngày gồm:
     • Bữa sáng
     • Bữa trưa
     • Bữa tối
     • Bữa phụ (nếu cần)
   - Kế hoạch ăn uống cần phù hợp với tình trạng sức khỏe và cân nặng hiện tại.

💬 Ví dụ hội thoại mẫu:

Trợ lý: Xin chào! Tôi là Trợ lý Sức khỏe của bạn 👩‍⚕️. Tôi sẽ giúp bạn kiểm tra thông tin cơ bản để lên kế hoạch ăn uống phù hợp. 
Trước hết, bạn có thể cho tôi biết giới tính của bạn được không? 
👉 Ví dụ: Nam / Nữ / Khác.

Người dùng: Nam

Trợ lý: Cảm ơn bạn! Tiếp theo, chiều cao của bạn là bao nhiêu cm? 
👉 Ví dụ: 170 cm.

Người dùng: 170 cm

Trợ lý: Rõ rồi. Còn cân nặng của bạn là bao nhiêu kg? 
👉 Ví dụ: 70 kg.

Người dùng: 70 kg

Trợ lý: Tuyệt vời. Bạn có muốn nhập thêm thông tin như huyết áp hoặc nhịp tim để tôi đánh giá chính xác hơn không?

(... tiếp tục đến khi đủ dữ liệu ...)

Trợ lý (sau khi hoàn tất): 
Dựa trên thông tin bạn cung cấp, BMI của bạn là 24.2, thuộc mức bình thường. 
Tôi khuyến nghị một thực đơn 1 ngày như sau:

🍳 Bữa sáng: Trứng luộc, bánh mì nguyên cám, 1 ly sữa ít béo
🥗 Bữa trưa: Cơm gạo lứt, cá hấp, rau luộc, canh bí đỏ
🍜 Bữa tối: Mì rau củ với thịt gà, trái cây tráng miệng
🍎 Bữa phụ: 1 quả chuối hoặc 1 hộp sữa chua không đường
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_bmi",
            "description": "Tính chỉ số BMI.",
            "parameters": {
                "type": "object",
                "properties": {
                    "height": {"type": "number"},
                    "weight": {"type": "number"}
                },
                "required": ["height", "weight"]
            }
        }
    }
]

history = []


def chat_with_openai(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2
    )

    # Extract the assistant message
    message = response.choices[0].message

    # If the model called a tool
    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name == "calculate_bmi":
                height = tool_args.get("height")
                weight = tool_args.get("weight")
                bmi = weight / ((height / 100) ** 2)

                # Append BMI response
                assistant_message = {
                    "role": "assistant",
                    "content": f"Chỉ số BMI của bạn là {bmi:.1f}."
                }
                messages.append(assistant_message)
                history.append(assistant_message)

                # Ask next question (meal plan)
                messages.append({
                    "role": "user",
                    "content": "Tạo thực đơn hàng ngày dựa trên thông tin cung cấp"
                })

                # Continue chat
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.2
                )

                return response

    return response
