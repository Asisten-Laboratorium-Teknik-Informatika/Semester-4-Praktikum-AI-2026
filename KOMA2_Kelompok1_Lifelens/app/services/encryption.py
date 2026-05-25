from __future__ import annotations

import os

from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken


load_dotenv()


def _get_fernet() -> Fernet:
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("ENCRYPTION_KEY belum diatur di environment.")
    return Fernet(key.encode())


def encrypt_text(text: str) -> str:
    if text is None:
        raise ValueError("text tidak boleh None")
    return _get_fernet().encrypt(text.encode("utf-8")).decode("utf-8")


def decrypt_text(encrypted_text: str) -> str:
    if encrypted_text is None:
        raise ValueError("encrypted_text tidak boleh None")
    try:
        return _get_fernet().decrypt(encrypted_text.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Teks terenkripsi tidak valid atau kunci salah.") from exc
