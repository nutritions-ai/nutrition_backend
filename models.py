from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatHistory(BaseModel):
    user_id: str
    messages: List[ChatMessage]
    message_count: int


class Dish(BaseModel):
    name: str
    portion: str

class Meal(BaseModel):
    name: str
    dishes: List[Dish]

class DailyMealResponse(BaseModel):
    meals: List[Meal]

class UserProfile(BaseModel):
    name: str
    age: str
    weight: str
    height: str

class BMI(BaseModel):
    value: str
    status: str
    comment: str

class Indicator(BaseModel):
    name: str
    value: str
    unit: Optional[str]
    normal_range: str
    status: str
    comment: str

class AnalyzeResult(BaseModel):
    bmi: BMI
    indicators: List[Indicator]
    general_evaluation: str
    details: str
    potential_risks: List[str]
    advice: str

class DailyMealRequest(BaseModel):
    user_profile: UserProfile
    analyze_result: str