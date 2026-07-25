"""Player de videos da Cacau para a interface Streamlit."""
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VIDEOS_DIR = PROJECT_ROOT / "cacau" / "videos"

WELCOME_VIDEO = VIDEOS_DIR / "boas-vindas.mp4"
PAYMENT_CONFIRMED_VIDEO = VIDEOS_DIR / "pagamento-confirmado.mp4"


def show_video(video_path: Path, *, caption: str | None = None, autoplay: bool = False) -> bool:
    """Exibe um video local se existir e retorna se ele foi mostrado."""
    if not video_path.exists():
        st.warning(f"Video da Cacau nao encontrado: {video_path.name}")
        return False
    st.video(str(video_path), autoplay=autoplay, muted=False)
    if caption:
        st.caption(caption)
    return True


def show_welcome_video() -> bool:
    return show_video(
        WELCOME_VIDEO,
        caption="Cacau, sua especialista em bombons artesanais. 🍫",
        autoplay=True,
    )


def show_payment_confirmed_video() -> bool:
    return show_video(
        PAYMENT_CONFIRMED_VIDEO,
        caption="Pagamento confirmado! Seu pedido ja esta sendo preparado com carinho. 🤎",
        autoplay=True,
    )