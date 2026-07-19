from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from repositories.product_repository import ProductRepository
from schemas.product import ProductFilterInput
from adapters.groq_adapter import recommend_flavors, generate_gift_message
from typing import Optional, List


def register(mcp: FastMCP):

    @mcp.tool(
        name="recommend_chocolates",
        description="""
        Recomenda sabores de bombons com base na ocasião e preferências do cliente.
        Usa a API Groq com contexto mínimo — nunca recebe dados pessoais sensíveis.

        ENTRADA:
        - occasion (str): ex "aniversário", "casamento", "agradecimento"
        - preferences (list[str]): sabores favoritos do cliente
        - restrictions (list[str]): restrições alimentares
        - only_available (bool): considerar apenas produtos em estoque

        SAÍDA: Texto com recomendações emocionais e sensoriais.
        """,
    )
    def recommend_chocolates(
        occasion: str,
        preferences: Optional[List[str]] = None,
        restrictions: Optional[List[str]] = None,
        only_available: bool = True,
    ) -> dict:
        with get_db() as db:
            repo = ProductRepository(db)
            filters = ProductFilterInput()
            products = repo.list_products(filters)
            if only_available:
                products = [p for p in products if p.available_quantity > 0]
            available = [{"name": p.flavor.name if p.flavor else p.name} for p in products]
        recommendation = recommend_flavors(
            occasion=occasion,
            preferences=preferences or [],
            restrictions=restrictions or [],
            available_flavors=available,
        )
        return {"recommendation": recommendation, "occasion": occasion}

    @mcp.tool(
        name="generate_gift_message",
        description="""
        Gera uma mensagem personalizada para cartão de presente.
        Usa a API Groq com apenas nome, destinatário, ocasião e tom.
        Nunca recebe dados pessoais desnecessários.

        ENTRADA:
        - sender (str): nome de quem envia
        - recipient (str): nome de quem recebe
        - occasion (str): ocasião
        - tone (str, opcional): tom desejado (padrão: "afetuoso")

        SAÍDA: Mensagem de cartão pronta para uso.
        """,
    )
    def generate_gift_message_tool(
        sender: str,
        recipient: str,
        occasion: str,
        tone: str = "afetuoso",
    ) -> dict:
        message = generate_gift_message(
            sender=sender,
            recipient=recipient,
            occasion=occasion,
            tone=tone,
        )
        return {"message": message, "sender": sender, "recipient": recipient, "occasion": occasion}

    @mcp.tool(
        name="get_tasting_recommendation",
        description="Retorna as recomendações de degustação, harmonização e contexto emocional de um produto.",
    )
    def get_tasting_recommendation(product_id: int) -> dict:
        with get_db() as db:
            repo = ProductRepository(db)
            product = repo.get_by_id(product_id)
            if not product or not product.flavor:
                return {"error": "Produto ou sabor não encontrado."}
            return {
                "product_name": product.name,
                "flavor_name": product.flavor.name,
                "tasting_note": product.flavor.tasting_note,
                "pairing_suggestion": product.flavor.pairing_suggestion,
                "emotional_context": product.flavor.emotional_context,
            }
