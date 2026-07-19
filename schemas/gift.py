from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List
from database.models import OccasionType


class GiftBoxItemInput(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, default=1)


class PersonalizedCardInput(BaseModel):
    sender_name: str = Field(min_length=2)
    recipient_name: str = Field(min_length=2)
    message: str = Field(min_length=5, max_length=500)
    occasion: Optional[OccasionType] = None


class CreateGiftBoxInput(BaseModel):
    name: str = Field(min_length=3)
    description: Optional[str] = None
    occasion: Optional[OccasionType] = None
    packaging_type: str = "standard"
    items: List[GiftBoxItemInput] = Field(min_length=1)
    card: Optional[PersonalizedCardInput] = None


class GiftBoxOut(BaseModel):
    id: int
    name: str
    occasion: Optional[OccasionType] = None
    packaging_price: Decimal
    is_active: bool
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}
