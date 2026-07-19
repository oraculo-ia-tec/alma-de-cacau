from __future__ import annotations
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Boolean, Text, Numeric, Date, DateTime,
    ForeignKey, Enum as SAEnum, UniqueConstraint, Index, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.engine import Base
import enum


# ──────────────────────────────────────────────
# ENUMS
# ──────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin = "admin"
    operator = "operator"
    customer = "customer"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    in_production = "in_production"
    ready = "ready"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    refused = "refused"
    refunded = "refunded"
    cancelled = "cancelled"


class PaymentMethod(str, enum.Enum):
    asaas = "asaas"           # cartão, PIX ou boleto via Asaas
    pix = "pix"               # PIX gerado via Asaas
    boleto = "boleto"         # Boleto gerado via Asaas
    cash_on_pickup = "cash_on_pickup"
    card_on_pickup = "card_on_pickup"


class DeliveryType(str, enum.Enum):
    pickup = "pickup"
    delivery = "delivery"


class NotificationChannel(str, enum.Enum):
    email = "email"
    telegram = "telegram"


class OccasionType(str, enum.Enum):
    birthday = "birthday"
    wedding = "wedding"
    thanks = "thanks"
    corporate = "corporate"
    easter = "easter"
    mothers_day = "mothers_day"
    christmas = "christmas"
    valentines = "valentines"
    other = "other"


# ──────────────────────────────────────────────
# MIXINS
# ──────────────────────────────────────────────

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                  onupdate=datetime.utcnow, nullable=False)


# ──────────────────────────────────────────────
# USUÁRIOS E PERMISSÕES
# ──────────────────────────────────────────────

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.customer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    customer_profile: Mapped[Optional["CustomerProfile"]] = relationship(back_populates="user", uselist=False)
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="user")


# ──────────────────────────────────────────────
# CLIENTES
# ──────────────────────────────────────────────

class CustomerProfile(TimestampMixin, Base):
    __tablename__ = "customer_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    cpf_hash: Mapped[Optional[str]] = mapped_column(String(64))  # SHA-256 hash, nunca raw
    notes: Mapped[Optional[str]] = mapped_column(Text)
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="customer_profile")
    addresses: Mapped[List["Address"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship(back_populates="customer")
    flavor_preferences: Mapped[List["CustomerFlavorPreference"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    allergen_alerts: Mapped[List["CustomerAllergenAlert"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    notification_preferences: Mapped[List["NotificationPreference"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    special_dates: Mapped[List["CustomerSpecialDate"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )


class Address(TimestampMixin, Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(50), default="Principal")
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    number: Mapped[str] = mapped_column(String(20), nullable=False)
    complement: Mapped[Optional[str]] = mapped_column(String(100))
    neighborhood: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(9), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    customer: Mapped["CustomerProfile"] = relationship(back_populates="addresses")
    orders: Mapped[List["Order"]] = relationship(back_populates="delivery_address")


class CustomerFlavorPreference(Base):
    __tablename__ = "customer_flavor_preferences"
    __table_args__ = (UniqueConstraint("customer_id", "flavor_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False)
    flavor_id: Mapped[int] = mapped_column(ForeignKey("flavors.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5

    customer: Mapped["CustomerProfile"] = relationship(back_populates="flavor_preferences")
    flavor: Mapped["Flavor"] = relationship()


class CustomerAllergenAlert(Base):
    __tablename__ = "customer_allergen_alerts"
    __table_args__ = (UniqueConstraint("customer_id", "allergen_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False)
    allergen_id: Mapped[int] = mapped_column(ForeignKey("allergens.id", ondelete="CASCADE"), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="moderate")  # mild, moderate, severe

    customer: Mapped["CustomerProfile"] = relationship(back_populates="allergen_alerts")
    allergen: Mapped["Allergen"] = relationship()


class CustomerSpecialDate(Base):
    __tablename__ = "customer_special_dates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    date_value: Mapped[date] = mapped_column(Date, nullable=False)
    notify_before_days: Mapped[int] = mapped_column(Integer, default=3)

    customer: Mapped["CustomerProfile"] = relationship(back_populates="special_dates")


# ──────────────────────────────────────────────
# PRODUTOS E CATÁLOGO
# ──────────────────────────────────────────────

class ProductCategory(TimestampMixin, Base):
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    products: Mapped[List["Product"]] = relationship(back_populates="category")


class Allergen(Base):
    __tablename__ = "allergens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(10))  # emoji

    product_allergens: Mapped[List["ProductAllergen"]] = relationship(back_populates="allergen")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    product_ingredients: Mapped[List["ProductIngredient"]] = relationship(back_populates="ingredient")
    inventory_items: Mapped[List["InventoryItem"]] = relationship(back_populates="ingredient")


class Flavor(TimestampMixin, Base):
    __tablename__ = "flavors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(200))  # ex: "equilíbrio e intensidade"
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tasting_note: Mapped[Optional[str]] = mapped_column(Text)     # como degustar
    pairing_suggestion: Mapped[Optional[str]] = mapped_column(Text)  # harmonização
    emotional_context: Mapped[Optional[str]] = mapped_column(Text)   # contexto emocional

    products: Mapped[List["Product"]] = relationship(back_populates="flavor")


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_active_flavor", "is_active", "flavor_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    flavor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("flavors.id", ondelete="SET NULL"))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_categories.id", ondelete="SET NULL"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit_label: Mapped[str] = mapped_column(String(30), default="unidade")  # ex: "caixa de 9", "unidade"
    weight_grams: Mapped[Optional[int]] = mapped_column(Integer)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_seasonal: Mapped[bool] = mapped_column(Boolean, default=False)
    is_best_seller: Mapped[bool] = mapped_column(Boolean, default=False)
    available_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_order_quantity: Mapped[int] = mapped_column(Integer, default=1)
    max_order_quantity: Mapped[Optional[int]] = mapped_column(Integer)

    flavor: Mapped[Optional["Flavor"]] = relationship(back_populates="products")
    category: Mapped[Optional["ProductCategory"]] = relationship(back_populates="products")
    ingredients: Mapped[List["ProductIngredient"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    allergens: Mapped[List["ProductAllergen"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")
    gift_box_items: Mapped[List["GiftBoxItem"]] = relationship(back_populates="product")
    seasonal_collections: Mapped[List["SeasonalCollectionProduct"]] = relationship(back_populates="product")


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"
    __table_args__ = (UniqueConstraint("product_id", "ingredient_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped["Product"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="product_ingredients")


class ProductAllergen(Base):
    __tablename__ = "product_allergens"
    __table_args__ = (UniqueConstraint("product_id", "allergen_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    allergen_id: Mapped[int] = mapped_column(ForeignKey("allergens.id", ondelete="RESTRICT"), nullable=False)
    is_trace: Mapped[bool] = mapped_column(Boolean, default=False)  # "pode conter"

    product: Mapped["Product"] = relationship(back_populates="allergens")
    allergen: Mapped["Allergen"] = relationship(back_populates="product_allergens")


# ──────────────────────────────────────────────
# ESTOQUE
# ──────────────────────────────────────────────

class InventoryItem(TimestampMixin, Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ingredient_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ingredients.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # g, kg, un, ml, l
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0"), nullable=False)
    min_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0"), nullable=False)
    cost_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("0"), nullable=False)

    ingredient: Mapped[Optional["Ingredient"]] = relationship(back_populates="inventory_items")


# ──────────────────────────────────────────────
# CAIXAS DE PRESENTE
# ──────────────────────────────────────────────

class GiftBox(TimestampMixin, Base):
    __tablename__ = "gift_boxes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    occasion: Mapped[Optional[OccasionType]] = mapped_column(SAEnum(OccasionType))
    packaging_type: Mapped[str] = mapped_column(String(100), default="standard")
    packaging_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"), nullable=False)
    max_items: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    items: Mapped[List["GiftBoxItem"]] = relationship(back_populates="gift_box", cascade="all, delete-orphan")
    personalized_card: Mapped[Optional["PersonalizedCard"]] = relationship(
        back_populates="gift_box", uselist=False, cascade="all, delete-orphan"
    )
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="gift_box")


class GiftBoxItem(Base):
    __tablename__ = "gift_box_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gift_box_id: Mapped[int] = mapped_column(ForeignKey("gift_boxes.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    gift_box: Mapped["GiftBox"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="gift_box_items")


class PersonalizedCard(TimestampMixin, Base):
    __tablename__ = "personalized_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gift_box_id: Mapped[int] = mapped_column(ForeignKey("gift_boxes.id", ondelete="CASCADE"), unique=True)
    sender_name: Mapped[str] = mapped_column(String(150), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    occasion: Mapped[Optional[OccasionType]] = mapped_column(SAEnum(OccasionType))

    gift_box: Mapped["GiftBox"] = relationship(back_populates="personalized_card")


# ──────────────────────────────────────────────
# PEDIDOS
# ──────────────────────────────────────────────

class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_customer_status", "customer_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_profiles.id", ondelete="RESTRICT"), nullable=False)
    delivery_type: Mapped[DeliveryType] = mapped_column(SAEnum(DeliveryType), default=DeliveryType.pickup)
    delivery_address_id: Mapped[Optional[int]] = mapped_column(ForeignKey("addresses.id", ondelete="SET NULL"))
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.pending, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"), nullable=False)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    coupon_id: Mapped[Optional[int]] = mapped_column(ForeignKey("coupons.id", ondelete="SET NULL"))
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)
    customer_notes: Mapped[Optional[str]] = mapped_column(Text)
    desired_delivery_date: Mapped[Optional[date]] = mapped_column(Date)

    customer: Mapped["CustomerProfile"] = relationship(back_populates="orders")
    delivery_address: Mapped[Optional["Address"]] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    status_history: Mapped[List["OrderStatusHistory"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    payment: Mapped[Optional["Payment"]] = relationship(back_populates="order", uselist=False)
    coupon: Mapped[Optional["Coupon"]] = relationship(back_populates="orders")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"))
    gift_box_id: Mapped[Optional[int]] = mapped_column(ForeignKey("gift_boxes.id", ondelete="RESTRICT"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    item_notes: Mapped[Optional[str]] = mapped_column(Text)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped[Optional["Product"]] = relationship(back_populates="order_items")
    gift_box: Mapped[Optional["GiftBox"]] = relationship(back_populates="order_items")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    previous_status: Mapped[Optional[OrderStatus]] = mapped_column(SAEnum(OrderStatus))
    new_status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), nullable=False)
    changed_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    order: Mapped["Order"] = relationship(back_populates="status_history")


# ──────────────────────────────────────────────
# PAGAMENTOS
# ──────────────────────────────────────────────

class Payment(TimestampMixin, Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="RESTRICT"), unique=True, nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    # Referências externas — nunca dados de cartão
    provider_reference: Mapped[Optional[str]] = mapped_column(String(255))  # Stripe PaymentIntent ID
    provider_status: Mapped[Optional[str]] = mapped_column(String(100))
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)

    order: Mapped["Order"] = relationship(back_populates="payment")


# ──────────────────────────────────────────────
# CUPONS
# ──────────────────────────────────────────────

class Coupon(TimestampMixin, Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    discount_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    discount_fixed: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    min_order_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    max_uses: Mapped[Optional[int]] = mapped_column(Integer)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    orders: Mapped[List["Order"]] = relationship(back_populates="coupon")


# ──────────────────────────────────────────────
# NOTIFICAÇÕES
# ──────────────────────────────────────────────

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    __table_args__ = (UniqueConstraint("customer_id", "channel"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(SAEnum(NotificationChannel), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    channel_address: Mapped[Optional[str]] = mapped_column(String(255))  # email ou telegram chat_id

    customer: Mapped["CustomerProfile"] = relationship(back_populates="notification_preferences")


class NotificationLog(TimestampMixin, Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customer_profiles.id", ondelete="SET NULL"))
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"))
    channel: Mapped[NotificationChannel] = mapped_column(SAEnum(NotificationChannel), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(255))
    body_preview: Mapped[Optional[str]] = mapped_column(String(500))
    was_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


# ──────────────────────────────────────────────
# COLEÇÕES SAZONAIS
# ──────────────────────────────────────────────

class SeasonalCollection(TimestampMixin, Base):
    __tablename__ = "seasonal_collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    occasion: Mapped[Optional[OccasionType]] = mapped_column(SAEnum(OccasionType))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    banner_url: Mapped[Optional[str]] = mapped_column(String(500))

    products: Mapped[List["SeasonalCollectionProduct"]] = relationship(
        back_populates="collection", cascade="all, delete-orphan"
    )


class SeasonalCollectionProduct(Base):
    __tablename__ = "seasonal_collection_products"
    __table_args__ = (UniqueConstraint("collection_id", "product_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("seasonal_collections.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    collection: Mapped["SeasonalCollection"] = relationship(back_populates="products")
    product: Mapped["Product"] = relationship(back_populates="seasonal_collections")


# ──────────────────────────────────────────────
# AUDITORIA
# ──────────────────────────────────────────────

class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # ex: "order.cancel", "payment.approve"
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer)
    before_state: Mapped[Optional[dict]] = mapped_column(JSON)
    after_state: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")
