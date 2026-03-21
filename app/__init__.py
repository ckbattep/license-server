# app/__init__.py

"""
🔐 License Server — Python package.
"""

__version__ = "1.0.0"

from .security.ed25519 import sign_payload, verify_signature
from .server import app  # Flask-приложение для импорта