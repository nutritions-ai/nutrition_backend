from sqlmodel import SQLModel, Field, Session, select, Relationship
from datetime import datetime
from typing import Optional

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from models import *
import json

class MealPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="userprofile.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meal_data_json: str  # store the AI meal plan as JSON text
    # user: Optional[UserProfile] = Relationship(back_populates="meal_plans")

    def get_data(self) -> MealPlanData:
        """Convert stored JSON string → Pydantic model"""
        return MealPlanData(**json.loads(self.meal_data_json))

class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, unique=True)
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    preferences_json: Optional[str] = None
    blood_test: Optional[str] = None
    urine_test: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    meal_plans: List[MealPlan] = Relationship(back_populates="user")

MealPlan.user = Relationship(back_populates="meal_plans")


# Request/Response models (for better API separation)
class UserProfileCreate(SQLModel):
    user_id: str
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    preferences_json: Optional[str] = None
    blood_test: Optional[str] = None
    urine_test: Optional[str] = None


class UserProfileUpdate(SQLModel):
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    preferences_json: Optional[str] = None
    blood_test: Optional[str] = None
    urine_test: Optional[str] = None
