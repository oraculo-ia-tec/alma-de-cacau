from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from database.models import Order, OrderStatus, OrderItem
from typing import Optional, List


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.items).joinedload(OrderItem.gift_box),
                joinedload(Order.status_history),
                joinedload(Order.payment),
                joinedload(Order.customer),
            )
            .filter_by(id=order_id)
            .first()
        )

    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.items),
                joinedload(Order.status_history),
                joinedload(Order.payment),
            )
            .filter_by(order_number=order_number)
            .first()
        )

    def list_by_customer(self, customer_id: int, page: int = 1, page_size: int = 10) -> List[Order]:
        return (
            self.db.query(Order)
            .filter_by(customer_id=customer_id)
            .order_by(desc(Order.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def list_by_status(self, status: OrderStatus, page: int = 1, page_size: int = 20) -> List[Order]:
        return (
            self.db.query(Order)
            .filter_by(status=status)
            .options(joinedload(Order.customer))
            .order_by(desc(Order.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def list_all(self, page: int = 1, page_size: int = 20) -> List[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.customer))
            .order_by(desc(Order.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def count_by_status(self, status: OrderStatus) -> int:
        return self.db.query(Order).filter_by(status=status).count()
