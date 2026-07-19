from mcp.server.fastmcp import FastMCP
from mcp_server.tools import (
    catalog_tools,
    customer_tools,
    order_tools,
    gift_tools,
    payment_tools,
    notification_tools,
    inventory_tools,
    coupon_tools,
    ai_tools,
    report_tools,
)

mcp = FastMCP(
    name="alma-de-cacau",
    description="Plataforma Alma de Cacau — Ferramentas para catálogo, pedidos, presentes, clientes e assistente.",
)

# Registrar todas as ferramentas
catalog_tools.register(mcp)
customer_tools.register(mcp)
order_tools.register(mcp)
gift_tools.register(mcp)
payment_tools.register(mcp)
notification_tools.register(mcp)
inventory_tools.register(mcp)
coupon_tools.register(mcp)
ai_tools.register(mcp)
report_tools.register(mcp)

if __name__ == "__main__":
    mcp.run()
