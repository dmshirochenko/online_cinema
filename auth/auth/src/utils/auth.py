import random
import string
import uuid


def get_random_password(size: int = 10) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(characters) for _ in range(size))
    return password


def _get_unique_postfix(size: int = 6) -> str:
    return str(uuid.uuid4().hex.upper()[:size])


def get_login_from_name(name: str, postfix_size: int = 6) -> str:
    login = "_".join(name.split()) + "_" + _get_unique_postfix(postfix_size)
    return login
