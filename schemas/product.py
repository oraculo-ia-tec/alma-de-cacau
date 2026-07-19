from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List


class ProductFilterInput(BaseModel):
    flavor_name: Optional[str] = None
    max_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    only_featured: bool = False
    only_seasonal: bool = False
    only_best_sellers: bool = False
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=12, ge=1, le=50)


class AllergenOut(BaseModel):
    name: str
    icon: Optional[str] = None
    is_trace: bool = False

    model_config = {"from_attributes": True}


class FlavorOut(BaseModel):
    name: str
    tagline: Optional[str] = None
    description: str
    tasting_note: Optional[str] = None
    pairing_suggestion: Optional[str] = None
    emotional_context: Optional[str] = None

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    price: Decimal
    unit_label: str
    is_featured: bool
    is_best_seller: bool
    is_seasonal: bool
    available_quantity: int
    flavor: Optional[FlavorOut] = None
    allergens: List[AllergenOut] = []
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class CreateProductInput(BaseModel):
    sku: str
    name: str
    flavor_id: Optional[int] = None
    category_id: Optional[int] = None
    description: str
    price: Decimal = Field(gt=0)
    unit_label: str = "unidade"
    weight_grams: Optional[int] = None
    image_url: Optional[str] = None
    available_quantity: int = Field(ge=0, default=0)
    is_active: bool = True
    is_featured: bool = False
    is_seasonal: bool = False
    is_best_seller: bool = False
