from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from services.customer_service import CustomerService
from schemas.customer import CreateCustomerInput, AddressInput
from repositories.customer_repository import CustomerRepository
from typing import Optional


def register(mcp: FastMCP):

    @mcp.tool(name="register_customer", description="Cadastra novo cliente com email e senha.")
    def register_customer(
        full_name: str, email: str, password: str,
        phone: Optional[str] = None, birth_date: Optional[str] = None,
        marketing_consent: bool = False,
    ) -> dict:
        data = CreateCustomerInput(
            full_name=full_name, email=email, password=password,
            phone=phone, birth_date=birth_date, marketing_consent=marketing_consent,
        )
        with get_db() as db:
            svc = CustomerService(db)
            profile, err = svc.register(data)
            if err:
                return {"error": err}
            return {"success": True, "customer_id": profile.id, "user_id": profile.user_id}

    @mcp.tool(name="get_customer", description="Retorna perfil completo do cliente.")
    def get_customer(customer_id: int) -> dict:
        with get_db() as db:
            repo = CustomerRepository(db)
            c = repo.get_by_id(customer_id)
            if not c:
                return {"error": "Cliente nao encontrado."}
            return {
                "id": c.id,
                "full_name": c.user.full_name,
                "email": c.user.email,
                "phone": c.phone,
                "marketing_consent": c.marketing_consent,
                "addresses": [
                    {"id": a.id, "label": a.label, "city": a.city,
                     "state": a.state, "is_default": a.is_default}
                    for a in c.addresses
                ],
            }

    @mcp.tool(name="add_customer_address", description="Adiciona endereco de entrega ao cliente.")
    def add_customer_address(
        customer_id: int, street: str, number: str, neighborhood: str,
        city: str, state: str, zip_code: str, label: str = "Principal",
        complement: Optional[str] = None, is_default: bool = False,
    ) -> dict:
        data = AddressInput(
            label=label, street=street, number=number, complement=complement,
            neighborhood=neighborhood, city=city, state=state,
            zip_code=zip_code, is_default=is_default,
        )
        with get_db() as db:
            svc = CustomerService(db)
            addr, err = svc.add_address(customer_id, data)
            if err:
                return {"error": err}
            return {"success": True, "address_id": addr.id}
