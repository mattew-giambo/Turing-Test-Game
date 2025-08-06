from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Genera l'hash sicuro di una password in chiaro.

    Args:
        password (str): Password da proteggere.

    Returns:
        str: Hash cifrato della password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica la corrispondenza tra una password in chiaro e il suo hash.

    Args:
        plain_password (str): Password fornita dall’utente.
        hashed_password (str): Hash salvato nel database.

    Returns:
        bool: True se la verifica ha successo, False altrimenti.

    Raises:
        HTTPException: Se il formato dell'hash è invalido o non verificabile.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Password errata"
        )

