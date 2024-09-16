from typing import List, Optional
from pydantic import BaseModel
from backend.app.services.part_service import PartService
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.models.base import get_db

router = APIRouter()


class OptionSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        orm_mode = True


class PartSchema(BaseModel):
    id: int
    name: str
    price: Optional[float] = None
    product_id: int
    options: List[OptionSchema]

    class Config:
        orm_mode = True


class PartList(BaseModel):
    __root__: List[PartSchema]


@router.get("/parts", response_model=PartList)
def read_parts(
    product_id: int = Query(..., description="ID of the product"),
    db: Session = Depends(get_db),
):
    part_service = PartService(db)
    parts = part_service.get_parts(product_id)
    return PartList(__root__=[PartSchema.from_orm(part) for part in parts])
