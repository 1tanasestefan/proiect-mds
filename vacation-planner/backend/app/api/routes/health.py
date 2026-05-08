from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "AI Travel Planner - Zero-Cost API Backend is running"}
