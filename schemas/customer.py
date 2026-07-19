from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
import re


class CreateCustomerInput(BaseModel):
    full_name: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=8)
    phone: Optional[str] = None
    birth_date: Optional[str] = None  # ISO date YYYY-MM-DD
    marketing_consent: bool = False

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v:
            raise ValueError("E-mail inválido.")
        return v.lower().strip()


class AddressInput(BaseModel):
    label: str = "Principal"
    street: str = Field(min_length=3)
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str = Field(min_length=2, max_length=2)
    zip_code: str
    is_default: bool = False

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) != 8:
            raise ValueError("CEP deve ter 8 dígitos.")
        return f"{cleaned[:5]}-{cleaned[5:]}"


class CustomerOut(BaseModel):
    id: int
    user_id: int
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    marketing_consent: bool

    model_config = {"from_attributes": True}


class CustomerPreferenceInput(BaseModel):
    customer_id: int
    flavor_ids: List[int] = []
    allergen_ids: List[int] = []
