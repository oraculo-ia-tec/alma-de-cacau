from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from repositories.inventory_repository import InventoryRepository
from decimal import Decimal


def register(mcp: FastMCP):

    @mcp.tool(name="list_inventory", description="Lista todos os itens de estoque de ingredientes.")
    def list_inventory() -> dict:
        with get_db() as db:
            repo = InventoryRepository(db)
            items = repo.list_all()
            return {
                "items": [
                    {
                        "id": i.id,
                        "name": i.name,
                        "unit": i.unit,
                        "quantity": float(i.quantity),
                        "min_quantity": float(i.min_quantity),
                        "is_low": i.quantity <= i.min_quantity,
                        "cost_per_unit": float(i.cost_per_unit),
                    }
                    for i in items
                ],
                "total": len(items),
            }

    @mcp.tool(name="get_low_stock_alerts", description="Retorna itens abaixo do estoque minimo.")
    def get_low_stock_alerts() -> dict:
        with get_db() as db:
            repo = InventoryRepository(db)
            items = repo.get_low_stock()
            alerts = [
                {"id": i.id, "name": i.name, "unit": i.unit,
                 "quantity": float(i.quantity), "min_quantity": float(i.min_quantity)}
                for i in items
            ]
            return {"alerts": alerts, "count": len(alerts)}

    @mcp.tool(name="adjust_inventory",
              description="Ajusta quantidade de um item de estoque (delta positivo = entrada, negativo = saida).")
    def adjust_inventory(item_id: int, delta: float) -> dict:
        with get_db() as db:
            repo = InventoryRepository(db)
            ok, err = repo.adjust_quantity(item_id, Decimal(str(delta)))
            if err:
                return {"error": err}
            return {"success": True, "item_id": item_id, "delta": delta}
