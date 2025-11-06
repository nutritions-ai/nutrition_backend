from pydantic import BaseModel
from typing import List, Optional

class MealItem(BaseModel):
    dish_name: str
    main_ingredients: List[str]
    portion: str
    health_reason: str

class MealPlanData(BaseModel):
    breakfast: List[MealItem]
    lunch: List[MealItem]
    dinner: List[MealItem]
    snacks: List[MealItem]
    summary: str

class AbnormalIndicator(BaseModel):
    name: str
    level: str
    explanation: str

class Recommendations(BaseModel):
    diet: str
    exercise: str
    lifestyle: str

class HealthAnalysis(BaseModel):
    overview: str
    normal_indicators: list[str]
    abnormal_indicators: list[AbnormalIndicator]
    recommendations: Recommendations
    summary: str

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

class UserProfileForAnalyze(BaseModel):
    name: str
    weight: str
    height: str

class DailyMealRequest(BaseModel):
    user_profile: UserProfileForAnalyze
    summary_result: str

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