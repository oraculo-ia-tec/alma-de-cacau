from sqlalchemy.orm import Session, joinedload
from database.models import CustomerProfile, User, Address
from typing import Optional, List


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, customer_id: int) -> Optional[CustomerProfile]:
        return (
            self.db.query(CustomerProfile)
            .options(
                joinedload(CustomerProfile.user),
                joinedload(CustomerProfile.addresses),
                joinedload(CustomerProfile.allergen_alerts),
                joinedload(CustomerProfile.flavor_preferences),
                joinedload(CustomerProfile.notification_preferences),
            )
            .filter_by(id=customer_id)
            .first()
        )

    def get_by_user_id(self, user_id: int) -> Optional[CustomerProfile]:
        return self.db.query(CustomerProfile).filter_by(user_id=user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter_by(email=email.lower()).first()

    def list_all(self, page: int = 1, page_size: int = 20) -> List[CustomerProfile]:
        return (
            self.db.query(CustomerProfile)
            .options(joinedload(CustomerProfile.user))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def count_all(self) -> int:
        return self.db.query(CustomerProfile).count()

    def get_default_address(self, customer_id: int) -> Optional[Address]:
        return (
            self.db.query(Address)
            .filter_by(customer_id=customer_id, is_default=True)
            .first()
        )
