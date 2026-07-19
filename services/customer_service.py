import hashlib
from sqlalchemy.orm import Session
from database.models import User, CustomerProfile, UserRole, Address
from schemas.customer import CreateCustomerInput, AddressInput
from typing import Optional, Tuple
from datetime import date


def _hash_password(password: str) -> str:
    salt = "alma_de_cacau_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: CreateCustomerInput) -> Tuple[Optional[CustomerProfile], Optional[str]]:
        existing = self.db.query(User).filter_by(email=data.email.lower()).first()
        if existing:
            return None, "E-mail ja cadastrado."
        user = User(
            email=data.email.lower(),
            hashed_password=_hash_password(data.password),
            full_name=data.full_name,
            role=UserRole.customer,
        )
        self.db.add(user)
        self.db.flush()
        birth = None
        if data.birth_date:
            try:
                birth = date.fromisoformat(data.birth_date)
            except ValueError:
                return None, "Data de nascimento invalida. Use YYYY-MM-DD."
        profile = CustomerProfile(
            user_id=user.id,
            phone=data.phone,
            birth_date=birth,
            marketing_consent=data.marketing_consent,
        )
        self.db.add(profile)
        return profile, None

    def authenticate(self, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        user = self.db.query(User).filter_by(email=email.lower(), is_active=True).first()
        if not user or user.hashed_password != _hash_password(password):
            return None, "E-mail ou senha invalidos."
        return user, None

    def add_address(self, customer_id: int, data: AddressInput) -> Tuple[Optional[Address], Optional[str]]:
        if data.is_default:
            self.db.query(Address).filter_by(customer_id=customer_id).update({"is_default": False})
        addr = Address(customer_id=customer_id, **data.model_dump())
        self.db.add(addr)
        return addr, None
