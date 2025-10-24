from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    message: str


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