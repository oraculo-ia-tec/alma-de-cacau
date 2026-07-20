"""
Script de atualizacao direta do catalogo - Alma de Cacau
Sincroniza os 7 sabores oficiais (conforme material grafico) com o banco.
Usa UPDATE-OR-CREATE (por SKU/nome), diferente do seed.py que so insere se nao existir.
Executar: python -c "from database.update_catalog import run_update; run_update()"
"""
from database.engine import get_db
from database.models import Flavor, Product, ProductCategory
from decimal import Decimal


FLAVORS_DATA = [
    {
        "name": "Pimenta",
        "tagline": "Equilibrio e intensidade",
        "description": "O contraste perfeito entre o doce e o picante. Um sabor surpreendente, marcante e inconfundivel.",
        "tasting_note": "Aprecie devagar, sentindo o calor suave e o sabor que permanece.",
        "pairing_suggestion": "Harmoniza com cafe espresso ou destilados amadeirados.",
        "emotional_context": "Para quem busca uma experiencia sensorial ousada e memoravel.",
    },
    {
        "name": "Doce de Leite com Amendoim",
        "tagline": "Pura nostalgia",
        "description": "A uniao do doce de leite cremoso com a crocancia do amendoim. Um classico que abraca o coracao.",
        "tasting_note": "Ideal com um cafe ou em um momento especial de pausa.",
        "pairing_suggestion": "Acompanha bem cafe com leite ou chocolate quente.",
        "emotional_context": "Para presentear com afeto e lembranca de infancia.",
    },
    {
        "name": "Castanha",
        "tagline": "Sofisticacao e crocancia",
        "description": "Recheio cremoso com pedacos selecionados de castanha. Sabor nobre, elegante e envolvente.",
        "tasting_note": "Harmoniza perfeitamente com um bom vinho ou para ocasioes especiais.",
        "pairing_suggestion": "Combina com vinho tinto encorpado ou porto.",
        "emotional_context": "Para celebrar conquistas e momentos de requinte.",
    },
    {
        "name": "Chocolate Branco",
        "tagline": "Delicadeza em cada mordida",
        "description": "Cremoso, suave e irresistivel. Um sabor que derrete na boca e conquista para sempre.",
        "tasting_note": "Aprecie com calma, para sentir toda a sua suavidade.",
        "pairing_suggestion": "Acompanha cha branco ou espumante doce.",
        "emotional_context": "Para presentes delicados e declaracoes afetuosas.",
    },
    {
        "name": "Pistache",
        "tagline": "Refinado e unico",
        "description": "Sabor nobre, cremoso e levemente amanteigado. Uma experiencia que encanta os sentidos.",
        "tasting_note": "Deguste lentamente, para sentir o sabor rico do verdadeiro pistache.",
        "pairing_suggestion": "Harmoniza com cha verde ou champagne brut.",
        "emotional_context": "Para quem aprecia sofisticacao em cada detalhe.",
    },
    {
        "name": "Amarula",
        "tagline": "Cremosidade e charme",
        "description": "Recheio cremoso com o toque suave e marcante do licor Amarula. Um sabor sofisticado e exotico.",
        "tasting_note": "Sirva geladinho, e deixe que o licor revele todo o encanto.",
        "pairing_suggestion": "Perfeito puro ou com um digestivo cremoso.",
        "emotional_context": "Para momentos de celebracao e indulgencia.",
    },
    {
        "name": "Cafe",
        "tagline": "Energia e sabor",
        "description": "Recheio intenso que desperta os sentidos. O sabor do cafe em uma mordida perfeita.",
        "tasting_note": "O companheiro ideal para o seu cafe da manha ou da tarde.",
        "pairing_suggestion": "Acompanha cappuccino ou leite quente.",
        "emotional_context": "Para quem precisa de um empurrao de energia com elegancia.",
    },
]

PRODUCTS_DATA = [
    {"sku": "ADC-PIM", "name": "Trufa de Pimenta", "flavor_name": "Pimenta",
     "description": "O contraste perfeito entre o doce e o picante.",
     "price": Decimal("10.50"), "is_featured": True, "is_best_seller": False},
    {"sku": "ADC-DLA", "name": "Trufa Doce de Leite com Amendoim", "flavor_name": "Doce de Leite com Amendoim",
     "description": "Doce de leite cremoso com crocancia do amendoim.",
     "price": Decimal("9.90"), "is_featured": True, "is_best_seller": True},
    {"sku": "ADC-CAS", "name": "Trufa de Castanha", "flavor_name": "Castanha",
     "description": "Recheio cremoso com pedacos selecionados de castanha.",
     "price": Decimal("9.50"), "is_featured": False, "is_best_seller": False},
    {"sku": "ADC-CBR", "name": "Trufa de Chocolate Branco", "flavor_name": "Chocolate Branco",
     "description": "Cremoso, suave e irresistivel.",
     "price": Decimal("9.50"), "is_featured": False, "is_best_seller": False},
    {"sku": "ADC-PIS", "name": "Trufa de Pistache", "flavor_name": "Pistache",
     "description": "Sabor nobre, cremoso e levemente amanteigado.",
     "price": Decimal("10.50"), "is_featured": True, "is_best_seller": True},
    {"sku": "ADC-AMA", "name": "Trufa de Amarula", "flavor_name": "Amarula",
     "description": "Toque suave e marcante do licor Amarula.",
     "price": Decimal("9.90"), "is_featured": False, "is_best_seller": False},
    {"sku": "ADC-CAF", "name": "Trufa de Cafe", "flavor_name": "Cafe",
     "description": "Recheio intenso que desperta os sentidos.",
     "price": Decimal("8.90"), "is_featured": False, "is_best_seller": False},
]


def run_update():
    with get_db() as db:
        cat_trufas = db.query(ProductCategory).filter_by(name="Trufas Especiais").first()
        if not cat_trufas:
            cat_trufas = ProductCategory(name="Trufas Especiais", display_order=2)
            db.add(cat_trufas)
            db.flush()

        flavors = {}
        for fd in FLAVORS_DATA:
            f = db.query(Flavor).filter_by(name=fd["name"]).first()
            if f:
                for key, value in fd.items():
                    setattr(f, key, value)
            else:
                f = Flavor(**fd)
                db.add(f)
            flavors[fd["name"]] = f
        db.flush()

        for pd in PRODUCTS_DATA:
            flavor = flavors.get(pd.pop("flavor_name"))
            sku = pd.pop("sku")
            name = pd.pop("name")
            product = db.query(Product).filter_by(sku=sku).first()
            if not product:
                product = db.query(Product).filter(Product.name.ilike(f"%{name}%")).first()

            if product:
                product.name = name
                product.sku = sku
                product.flavor_id = flavor.id if flavor else None
                product.category_id = cat_trufas.id
                product.is_active = True
                for key, value in pd.items():
                    setattr(product, key, value)
            else:
                product = Product(
                    sku=sku, name=name, flavor_id=flavor.id if flavor else None,
                    category_id=cat_trufas.id, unit_label="unidade", weight_grams=25,
                    available_quantity=50, is_active=True, **pd,
                )
                db.add(product)
        db.flush()

        print("[UPDATE] Catalogo dos 7 sabores atualizado com sucesso.")
        for p in db.query(Product).filter(Product.sku.in_([p["sku"] for p in [
            {"sku": s} for s in ["ADC-PIM","ADC-DLA","ADC-CAS","ADC-CBR","ADC-PIS","ADC-AMA","ADC-CAF"]
        ]])).all():
            print(f"  {p.sku} | {p.name} | ativo={p.is_active} | preco={p.price}")
