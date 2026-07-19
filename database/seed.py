"""
Dados iniciais para o banco de dados da Alma de Cacau.
Executar: python -c "from database.seed import run_seed; run_seed()"
"""
from database.engine import get_db, init_db
from database.models import (
    Allergen, Ingredient, Flavor, ProductCategory,
    Product, InventoryItem, User, UserRole,
)
import hashlib
from decimal import Decimal


def _hash_password(password: str) -> str:
    salt = "alma_de_cacau_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def run_seed():
    init_db()
    with get_db() as db:
        # --- Alergenos ---
        allergens_data = [
            ("Gluten", "🌾"), ("Lactose", "🥛"), ("Amendoim", "🥜"),
            ("Soja", "🫘"), ("Castanhas", "🌰"), ("Ovos", "🥚"),
        ]
        allergens = {}
        for name, icon in allergens_data:
            a = db.query(Allergen).filter_by(name=name).first()
            if not a:
                a = Allergen(name=name, icon=icon)
                db.add(a)
            allergens[name] = a
        db.flush()

        # --- Ingredientes ---
        ingredients_data = [
            ("Chocolate Belga 70% Cacau", True),
            ("Chocolate Branco Premium", True),
            ("Caramelo Artesanal", True),
            ("Praline de Amendoim", True),
            ("Maracuja Fresco", False),
            ("Flor de Sal do Nordeste", False),
            ("Avela Piemontesa", True),
            ("Manteiga de Cacau", False),
        ]
        for name, is_premium in ingredients_data:
            if not db.query(Ingredient).filter_by(name=name).first():
                db.add(Ingredient(name=name, is_premium=is_premium))
        db.flush()

        # --- Sabores ---
        flavors_data = [
            {
                "name": "Intenso 70%",
                "tagline": "Alma pura do cacau",
                "description": "Chocolate amargo de origem com 70% de cacau selecionado.",
                "tasting_note": "Deixe derreter lentamente na lingua para sentir as notas de frutas vermelhas e castanha.",
                "pairing_suggestion": "Harmoniza com cafe espresso ou vinho tinto encorpado.",
                "emotional_context": "Para momentos de reflexao e introspeccao. Um presente para quem aprecia o genuino.",
            },
            {
                "name": "Caramelo Flor de Sal",
                "tagline": "O equilibrio perfeito",
                "description": "Ganache aveludada de caramelo artesanal com toque de flor de sal do Nordeste.",
                "tasting_note": "O contraste doce-salgado revela-se camada a camada.",
                "pairing_suggestion": "Acompanha cha verde ou champagne brut.",
                "emotional_context": "Para celebrar dualidades e conexoes especiais.",
            },
            {
                "name": "Maracuja Tropical",
                "tagline": "O Brasil em cada mordida",
                "description": "Ganache de chocolate ao leite com polpa fresca de maracuja.",
                "tasting_note": "Acidez vibrante que desperta os sentidos, finalizada em suavidade.",
                "pairing_suggestion": "Perfeito com suco de frutas tropicais ou agua com gas.",
                "emotional_context": "Para presentear com alegria e leveza.",
            },
            {
                "name": "Avela & Chocolate",
                "tagline": "O classico reinventado",
                "description": "Praline artesanal de avela piemontesa envolta em chocolate amargo.",
                "tasting_note": "Crocante por fora, cremoso por dentro. Um abraco em forma de bombom.",
                "pairing_suggestion": "Excelente com cappuccino ou leite quente.",
                "emotional_context": "Para momentos de conforto e nostalgia afetiva.",
            },
            {
                "name": "Chocolate Branco & Framboesa",
                "tagline": "Elegancia e frescor",
                "description": "Ganache de chocolate branco belga com compota de framboesa.",
                "tasting_note": "Doce e floral com acidez delicada da framboesa.",
                "pairing_suggestion": "Harmoniza com rose espumante ou cha de hibisco.",
                "emotional_context": "Para celebrar feminilidade, aniversarios e primeiros presentes.",
            },
        ]
        flavors = {}
        for fd in flavors_data:
            f = db.query(Flavor).filter_by(name=fd["name"]).first()
            if not f:
                f = Flavor(**fd)
                db.add(f)
            flavors[fd["name"]] = f
        db.flush()

        # --- Categorias ---
        cats_data = [
            ("Bombons Classicos", 1), ("Trufas Especiais", 2),
            ("Colecao Presente", 3), ("Edicao Sazonal", 4),
        ]
        for name, order in cats_data:
            if not db.query(ProductCategory).filter_by(name=name).first():
                db.add(ProductCategory(name=name, display_order=order))
        db.flush()

        cat_classicos = db.query(ProductCategory).filter_by(name="Bombons Classicos").first()
        cat_trufas = db.query(ProductCategory).filter_by(name="Trufas Especiais").first()

        # --- Produtos ---
        products_data = [
            {
                "sku": "ADC-001", "name": "Bombom Intenso 70%",
                "description": "Bombom artesanal de chocolate amargo 70% cacau, moldado a mao.",
                "price": Decimal("8.50"), "unit_label": "unidade", "weight_grams": 25,
                "available_quantity": 50, "is_featured": True, "is_best_seller": True,
                "flavor_name": "Intenso 70%", "category": cat_classicos,
            },
            {
                "sku": "ADC-002", "name": "Trufa Caramelo Flor de Sal",
                "description": "Trufa de caramelo artesanal com flor de sal, envolta em chocolate 70%.",
                "price": Decimal("9.90"), "unit_label": "unidade", "weight_grams": 30,
                "available_quantity": 35, "is_featured": True, "is_best_seller": True,
                "flavor_name": "Caramelo Flor de Sal", "category": cat_trufas,
            },
            {
                "sku": "ADC-003", "name": "Bombom Maracuja Tropical",
                "description": "Ganache de maracuja fresco em casca de chocolate ao leite.",
                "price": Decimal("8.90"), "unit_label": "unidade", "weight_grams": 25,
                "available_quantity": 40, "is_featured": False,
                "flavor_name": "Maracuja Tropical", "category": cat_classicos,
            },
            {
                "sku": "ADC-BOX9", "name": "Caixa Degustacao 9 Bombons",
                "description": "Selecao de 9 bombons artesanais nos sabores mais amados da casa.",
                "price": Decimal("69.90"), "unit_label": "caixa de 9", "weight_grams": 250,
                "available_quantity": 20, "is_featured": True, "is_best_seller": True,
                "flavor_name": None, "category": cat_classicos,
            },
        ]
        for pd in products_data:
            if not db.query(Product).filter_by(sku=pd["sku"]).first():
                flavor = flavors.get(pd.pop("flavor_name")) if pd["flavor_name"] else None
                category = pd.pop("category")
                product = Product(
                    flavor_id=flavor.id if flavor else None,
                    category_id=category.id if category else None,
                    **{k: v for k, v in pd.items() if k not in ("flavor_name", "category")},
                )
                db.add(product)
            else:
                pd.pop("flavor_name", None)
                pd.pop("category", None)
        db.flush()

        # --- Estoque ---
        inventory_data = [
            ("Chocolate Belga 70%", "kg", Decimal("10.0"), Decimal("2.0"), Decimal("45.00")),
            ("Chocolate Branco Premium", "kg", Decimal("5.0"), Decimal("1.0"), Decimal("52.00")),
            ("Caramelo Artesanal", "kg", Decimal("3.0"), Decimal("0.5"), Decimal("28.00")),
            ("Flor de Sal", "g", Decimal("500.0"), Decimal("100.0"), Decimal("0.05")),
            ("Embalagens Standard", "un", Decimal("200.0"), Decimal("50.0"), Decimal("0.80")),
        ]
        for name, unit, qty, min_qty, cost in inventory_data:
            if not db.query(InventoryItem).filter_by(name=name).first():
                db.add(InventoryItem(
                    name=name, unit=unit, quantity=qty,
                    min_quantity=min_qty, cost_per_unit=cost,
                ))

        # --- Admin ---
        if not db.query(User).filter_by(email="admin@almadecacau.com.br").first():
            db.add(User(
                email="admin@almadecacau.com.br",
                hashed_password=_hash_password("AlmaDeCacau@2024"),
                full_name="Administrador Alma de Cacau",
                role=UserRole.admin,
            ))

        print("[SEED] Dados iniciais inseridos com sucesso.")
