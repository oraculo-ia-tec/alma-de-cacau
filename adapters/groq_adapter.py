import os
from groq import Groq
from typing import Optional


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = "llama-3.3-70b-versatile"  # fixo — nao depende do env

_client: Optional[Groq] = None


def _get_client() -> Groq:
    global _client
    if not _client:
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


BRAND_SYSTEM_PROMPT = """Você é a assistente virtual da Alma de Cacau, uma marca artesanal premium de bombons.
Tom: afetuoso, elegante, artesanal, próximo, inspirador e sensorial.
Nunca invente ingredientes, alergênicos, preços ou disponibilidade.
Sempre baseie suas respostas nos dados fornecidos.
Escreva em português do Brasil com cuidado e afeto.
Assinatura da marca: 'Alma de Cacau — Transformando chocolate em lembrança.'"""


def recommend_flavors(
    occasion: str,
    preferences: list[str],
    restrictions: list[str],
    available_flavors: list[dict],
) -> str:
    prompt = f"""
Ocasião: {occasion}
Preferências do cliente: {', '.join(preferences) if preferences else 'nenhuma informada'}
Restrições alimentares: {', '.join(restrictions) if restrictions else 'nenhuma'}
Sabores disponíveis hoje: {[f["name"] for f in available_flavors]}

Com base nisso, recomende até 3 sabores com uma justificativa sensorial e emocional para cada um.
Seja afetuoso, específico e inspire o cliente a escolher com o coração.
"""
    response = _get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": BRAND_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


def generate_gift_message(
    sender: str,
    recipient: str,
    occasion: str,
    tone: str = "afetuoso",
) -> str:
    prompt = f"""
Crie uma mensagem de cartão para presente com as seguintes informações:
- Quem envia: {sender}
- Quem recebe: {recipient}
- Ocasião: {occasion}
- Tom desejado: {tone}

A mensagem deve ser curta (máximo 4 linhas), original, sincera e alinhada com a marca Alma de Cacau.
Termine com a assinatura: '— Alma de Cacau'
"""
    response = _get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": BRAND_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()
