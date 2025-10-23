from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    message: str


class MealItem(BaseModel):
    dish_name: str
    main_ingredients: List[str]
    portion: str
    health_reason: str

class MealPlan(BaseModel):
    breakfast: List[MealItem]
    lunch: List[MealItem]
    dinner: List[MealItem]
    snacks: List[MealItem]
    summary: str