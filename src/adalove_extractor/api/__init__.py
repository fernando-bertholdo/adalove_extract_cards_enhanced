"""
Módulo de API para extração de dados do AdaLove via HTTP requests.

Este módulo fornece um cliente HTTP para interagir com a API REST do AdaLove,
eliminando a necessidade de automação de navegador para extração de dados.
"""

from .client import AdaLoveAPIClient
from .auth import CognitoAuthenticator
from .endpoints import Endpoints
from .exceptions import (
    APIError,
    AuthenticationError,
    TokenExpiredError,
    EndpointNotFoundError,
    RateLimitError
)

__all__ = [
    "AdaLoveAPIClient",
    "CognitoAuthenticator",
    "Endpoints",
    "APIError",
    "AuthenticationError",
    "TokenExpiredError",
    "EndpointNotFoundError",
    "RateLimitError",
]
