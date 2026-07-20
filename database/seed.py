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
            ("Gluten", "\U0001F33E"), ("Lactose", "\U0001F95B"), ("Amendoim", "\U0001F95C"),
            ("Soja", "\U0001FAD8"), ("Castanhas", "\U0001F330"), ("Ovos", "\U0001F95A"),
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
            ("Doce de Leite Artesanal", True),
            ("Amendoim Torrado", False),
            ("Castanha Selecionada", True),
            ("Pistache Nobre", True),
            ("Licor Amarula", True),
            ("Cafe Torrado e Moido", False),
            ("Pimenta Artesanal", False),
            ("Manteiga de Cacau", False),
        ]
        for name, is_premium in ingredients_data:
            if not db.query(Ingredient).filter_by(name=name).first():
                db.add(Ingredient(name=name, is_premium=is_premium))
        db.flush()

        # --- Sabores (os 7 sabores oficiais da Alma de Cacau) ---
        flavors_data = [
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

        cat_trufas = db.query(ProductCategory).filter_by(name="Trufas Especiais").first()
        cat_presente = db.query(ProductCategory).filter_by(name="Colecao Presente").first()

        # --- Produtos (nomes IDENTICOS aos "label" do _PRODUCT_MAP em assistant.py) ---
        products_data = [
            {
                "sku": "ADC-PIM", "name": "Trufa de Pimenta",
                "description": "O contraste perfeito entre o doce e o picante.",
                "price": Decimal("10.50"), "unit_label": "unidade", "weight_grams": 25,
                "available_quantity": 50, "is_featured": True, "is_best_seller": False,
                "flavor_name": "Pimenta", "category": cat_trufas,
            },
            {
                "sku": "ADC-DLA", "name": "Trufa Doce de Leite com Amendoim",
                "description": "Doce de leite cremoso com crocancia do amendoim.",
                "price": Decimal("9.90"), "unit_label": "unidade", "weight_grams": 25,
                "available_quantity": 50, "is_featured": True, "is_best_seller": True,
                "flavor_name": "Doce de Leite com Amendoim", "category": cat_trufas,
            },
            {
                "sku": "ADC-CAS", "name": "Trufa de Castanha",
                "description": "Recheio cremoso com pedacos selecionados de castanha.",
                "price": Decimal("9.50"), "unit_label": "unidade", "weight_grams": 25,
                "available_quantity": 50, "is_featured": False, "is_best_seller": False,
                "flavor_name": "Castanha", "category": cat_trufas,
            },
            {
                "sku": "ADC-CBR", "name": "Trufa de Chocolate Branco",
                "description": "Cremoso, suave e irresistivel.",
                "price": Decimal("9.50"), "unit_label": "unidade", "weight_grams": 25,
                "available_quantity": 50, "is_featured": False, "is_best_seller": False,
                "flavor_name": "Chocolate Branco", "category": cat_trufas,
            },
            {
                "sku": "ADC-PIS", "name": "Trufa de Pistache",
                "description": "Sabor nobre, cremoso e levemente amanteigado.",
                "price": Decimal("10.50"), "unit_label": "unidade", "weight_grams": 25,
                "available_quantity": 50, "is_featured": True, "is_best_seller": True,
                "flavor_name": "Pistache", "category": cat_trufas,
            },
            {
                "sku": "ADC-AMA", "name": "Trufa de Amarula",
                "description": "Toque suave e marcante do licor Amarula.",
                "price": Decimal("9.90"), "unit_label": "unidade", "weight_grams": 25,
                "available_quantity": 50, "is_featured": False, "is_best_seller": False,
                "flavor_name": "Amarula", "category": cat_trufas,
            },
            {
                "sku": "ADC-CAF", "name": "Trufa de Cafe",
                "description": "Recheio intenso que desperta os sentidos.",
                "price": Decimal("8.90"), "unit_label": "unidade", "weight_grams": 25,
                "available_quantity": 50, "is_featured": False, "is_best_seller": False,
                "flavor_name": "Cafe", "category": cat_trufas,
            },
            {
                "sku": "ADC-BOX9", "name": "Caixa Degustacao 9 Trufas",
                "description": "Selecao de 9 trufas artesanais nos sabores mais amados da casa.",
                "price": Decimal("69.90"), "unit_label": "caixa de 9", "weight_grams": 250,
                "available_quantity": 20, "is_featured": True, "is_best_seller": True,
                "flavor_name": None, "category": cat_presente,
            },
        ]
        for pd in products_data:
            if not db.query(Product).filter_by(sku=pd["sku"]).first():
                flavor = flavors.get(pd.pop("flavor_name")) if pd.get("flavor_name") else None
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
            ("Doce de Leite Artesanal", "kg", Decimal("4.0"), Decimal("1.0"), Decimal("22.00")),
            ("Amendoim Torrado", "kg", Decimal("3.0"), Decimal("0.5"), Decimal("18.00")),
            ("Castanha Selecionada", "kg", Decimal("2.0"), Decimal("0.5"), Decimal("60.00")),
            ("Pistache Nobre", "kg", Decimal("1.5"), Decimal("0.3"), Decimal("90.00")),
            ("Licor Amarula", "l", Decimal("2.0"), Decimal("0.5"), Decimal("55.00")),
            ("Cafe Torrado e Moido", "kg", Decimal("2.0"), Decimal("0.5"), Decimal("35.00")),
            ("Pimenta Artesanal", "g", Decimal("300.0"), Decimal("50.0"), Decimal("0.15")),
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
