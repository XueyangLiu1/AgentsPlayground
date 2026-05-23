from fastapi import APIRouter
from ..presets import PRESETS
from ..schemas import PresetCard

router = APIRouter(prefix="/presets", tags=["presets"])


@router.get("/cards", response_model=list[PresetCard])
def list_card_presets():
    return PRESETS
