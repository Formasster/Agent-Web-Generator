import logging
from sqlalchemy.orm import Session
from app.db.models import User, ChatMessage, GeneratedPage

logger = logging.getLogger(__name__)


def get_or_create_user(db: Session, session_id: str) -> User:
    """Obtiene un usuario por session_id o lo crea si no existe."""
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        user = User(session_id=session_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Usuario creado: {user.id} (session: {session_id})")
    return user


def save_message(db: Session, user_id, role: str, content: str) -> ChatMessage:
    """Guarda un mensaje del chat (role: 'user' o 'agent')."""
    message = ChatMessage(user_id=user_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def save_generated_page(db: Session, user_id, prompt: str, site_type: str, html: str) -> GeneratedPage:
    """Guarda una página generada."""
    page = GeneratedPage(
        user_id=user_id,
        prompt=prompt,
        site_type=site_type,
        html=html
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    logger.info(f"Página guardada: {page.id} (tipo: {site_type})")
    return page


def get_chat_history(db: Session, session_id: str) -> list:
    """Obtiene el historial de mensajes de un usuario."""
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        return []
    return db.query(ChatMessage).filter(
        ChatMessage.user_id == user.id
    ).order_by(ChatMessage.created_at.asc()).all()


def get_user_pages(db: Session, session_id: str) -> list:
    """Obtiene las páginas generadas por un usuario."""
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        return []
    return db.query(GeneratedPage).filter(
        GeneratedPage.user_id == user.id
    ).order_by(GeneratedPage.created_at.desc()).all()