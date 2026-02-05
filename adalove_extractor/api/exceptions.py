"""
Exceções customizadas para o módulo de API.
"""


class APIError(Exception):
    """Erro genérico de API."""
    pass


class AuthenticationError(APIError):
    """Erro de autenticação."""
    pass


class TokenExpiredError(AuthenticationError):
    """Token expirado."""
    pass


class EndpointNotFoundError(APIError):
    """Endpoint não encontrado (404)."""
    pass


class RateLimitError(APIError):
    """Rate limit excedido (429)."""
    pass
