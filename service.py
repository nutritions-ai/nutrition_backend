from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session, select
from models_sql import *
import json

def add_meal_plan(session: Session, user_profile: UserProfile, meal_plan: MealPlanData):
    meal_json = meal_plan.model_dump_json()
    new_plan = MealPlan(user_id=user_profile.id, meal_data_json=meal_json)
    session.add(new_plan)
    session.commit()
    session.refresh(new_plan)
    return new_plan

def create_user_profile(session: Session, profile_data: UserProfileCreate) -> UserProfile:
    existing = session.exec(select(UserProfile).where(UserProfile.user_id == profile_data.user_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="UserProfile with this user_id already exists.")
    new_profile = UserProfile(**profile_data.model_dump())
    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)
    return new_profile


def get_user_profile(session: Session, user_id: str) -> UserProfile:
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="UserProfile not found.")
    return profile


def get_all_profiles(session: Session) -> list[UserProfile]:
    return session.exec(select(UserProfile)).all()


def update_user_profile(session: Session, user_id: str, updates: UserProfileUpdate) -> UserProfile:
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="UserProfile not found.")
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    profile.last_updated = datetime.utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def delete_user_profile(session: Session, user_id: str):
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="UserProfile not found.")
    session.delete(profile)
    session.commit()
    return {"message": "UserProfile deleted successfully"}

def upsert_user_profile(session: Session, profile_data: UserProfileCreate) -> UserProfile:
    """
    If a UserProfile with the same user_id exists -> update it (only provided fields).
    If not -> create and return the new UserProfile.
    """
    existing = session.exec(select(UserProfile).where(UserProfile.user_id == profile_data.user_id)).first()
    if existing:
        update_data = profile_data.model_dump(exclude_unset=True)
        # avoid overwriting user_id accidentally
        update_data.pop("user_id", None)
        for key, value in update_data.items():
            setattr(existing, key, value)
        existing.last_updated = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    else:
        new_profile = UserProfile(**profile_data.model_dump())
        session.add(new_profile)
        session.commit()
        session.refresh(new_profile)
        return new_profile