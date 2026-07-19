"""
FERRAMENTAS MCP — CATÁLOGO DE PRODUTOS
"""
from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from repositories.product_repository import ProductRepository
from schemas.product import ProductFilterInput
from typing import Optional
from decimal import Decimal


def register(mcp: FastMCP):

    @mcp.tool(
        name="list_products",
        description="""
        Lista os produtos ativos do catálogo Alma de Cacau com filtros opcionais.

        ENTRADA:
        - flavor_name (str, opcional): filtro por nome do sabor
        - max_price (Decimal, opcional): preço máximo
        - min_price (Decimal, opcional): preço mínimo
        - only_featured (bool): apenas destaques
        - only_seasonal (bool): apenas sazonais
        - only_best_sellers (bool): apenas mais vendidos
        - page (int): página (padrão 1)
        - page_size (int): itens por página (padrão 12, máx 50)

        SAÍDA: Lista de produtos com id, nome, preço, sabor, alergênicos, estoque e destaque.

        REGRAS:
        - Retorna apenas produtos is_active=True.
        - Alergênicos são sempre incluídos na resposta.
        - Preço nunca é estimado — é o valor real do banco.

        ERROS:
        - Banco indisponível: retorna erro interno.
        """,
    )
    def list_products(
        flavor_name: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        only_featured: bool = False,
        only_seasonal: bool = False,
        only_best_sellers: bool = False,
        page: int = 1,
        page_size: int = 12,
    ) -> dict:
        filters = ProductFilterInput(
            flavor_name=flavor_name,
            max_price=Decimal(str(max_price)) if max_price else None,
            min_price=Decimal(str(min_price)) if min_price else None,
            only_featured=only_featured,
            only_seasonal=only_seasonal,
            only_best_sellers=only_best_sellers,
            page=page,
            page_size=page_size,
        )
        with get_db() as db:
            repo = ProductRepository(db)
            products = repo.list_products(filters)
            result = []
            for p in products:
                result.append({
                    "id": p.id,
                    "sku": p.sku,
                    "name": p.name,
                    "price": float(p.price),
                    "unit_label": p.unit_label,
                    "is_featured": p.is_featured,
                    "is_best_seller": p.is_best_seller,
                    "is_seasonal": p.is_seasonal,
                    "available_quantity": p.available_quantity,
                    "flavor_name": p.flavor.name if p.flavor else None,
                    "flavor_tagline": p.flavor.tagline if p.flavor else None,
                    "allergens": [
                        {"name": a.allergen.name, "icon": a.allergen.icon, "is_trace": a.is_trace}
                        for a in p.allergens
                    ],
                    "image_url": p.image_url,
                })
        return {"products": result, "count": len(result)}

    @mcp.tool(
        name="get_product_details",
        description="""
        Retorna todos os detalhes de um produto específico, incluindo sabor completo,
        ingredientes, alergênicos, notas de degustação e harmonização.

        ENTRADA:
        - product_id (int): ID do produto

        SAÍDA: Produto completo com todos os atributos.

        REGRAS:
        - Alergênicos são SEMPRE incluídos, inclusive os de traço ("pode conter").
        - Retorna erro se produto não existir ou estiver inativo.

        CRÍTICO: Nunca omita informações de alergênicos.
        """,
    )
    def get_product_details(product_id: int) -> dict:
        with get_db() as db:
            repo = ProductRepository(db)
            product = repo.get_by_id(product_id)
            if not product:
                return {"error": "Produto não encontrado ou inativo.", "product_id": product_id}
            return {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "unit_label": product.unit_label,
                "available_quantity": product.available_quantity,
                "flavor": {
                    "name": product.flavor.name,
                    "tagline": product.flavor.tagline,
                    "description": product.flavor.description,
                    "tasting_note": product.flavor.tasting_note,
                    "pairing_suggestion": product.flavor.pairing_suggestion,
                    "emotional_context": product.flavor.emotional_context,
                } if product.flavor else None,
                "allergens": [
                    {
                        "name": a.allergen.name,
                        "icon": a.allergen.icon,
                        "is_trace": a.is_trace,
                        "label": f"Pode conter: {a.allergen.name}" if a.is_trace else f"Contém: {a.allergen.name}",
                    }
                    for a in product.allergens
                ],
                "is_featured": product.is_featured,
                "is_best_seller": product.is_best_seller,
                "is_seasonal": product.is_seasonal,
                "image_url": product.image_url,
            }

    @mcp.tool(name="get_allergen_information", description="Retorna alergênicos de um produto. CRÍTICO para segurança do cliente.")
    def get_allergen_information(product_id: int) -> dict:
        with get_db() as db:
            repo = ProductRepository(db)
            product = repo.get_by_id(product_id)
            if not product:
                return {"error": "Produto não encontrado."}
            allergens = [
                {
                    "name": a.allergen.name,
                    "icon": a.allergen.icon,
                    "is_trace": a.is_trace,
                    "severity_label": "⚠️ Pode conter" if a.is_trace else "🚨 Contém",
                }
                for a in product.allergens
            ]
            return {
                "product_id": product_id,
                "product_name": product.name,
                "allergens": allergens,
                "allergen_count": len(allergens),
                "has_allergens": len(allergens) > 0,
            }
