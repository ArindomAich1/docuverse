from fastapi import APIRouter

router = APIRouter(prefix="/hello")

@router.get("/")
def hello():
    return "DocuVerse is LIVE!"