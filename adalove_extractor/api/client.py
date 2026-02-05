"""
Cliente HTTP para API do AdaLove.

Este módulo fornece um cliente HTTP assíncrono com:
- Autenticação automática via AWS Cognito
- Retry automático em caso de falhas
- Logging de requisições
- Tratamento de erros
"""

import httpx
import logging
import asyncio
from typing import Optional, Dict, Any, List

from .auth import CognitoAuthenticator
from .endpoints import Endpoints
from .exceptions import (
    APIError,
    AuthenticationError,
    TokenExpiredError,
    EndpointNotFoundError,
    RateLimitError
)


class AdaLoveAPIClient:
    """
    Cliente HTTP para API do AdaLove.
    
    Gerencia autenticação, requisições e tratamento de erros.
    """
    
    def __init__(
        self,
        base_url: str = "https://apiv2.inteli.edu.br",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Inicializa o cliente HTTP.
        
        Args:
            base_url: URL base da API
            timeout: Timeout em segundos
            max_retries: Número máximo de tentativas
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = httpx.AsyncClient(timeout=timeout)
        self.auth = CognitoAuthenticator()
        self.logger = logging.getLogger(__name__)
    
    async def authenticate(self, login: str, senha: str):
        """
        Autentica e armazena token.
        
        Args:
            login: Email do usuário
            senha: Senha do usuário
            
        Raises:
            AuthenticationError: Se autenticação falhar
        """

        if self.auth.is_authenticated():
            self.logger.info("✅ Cliente já autenticado (cache)")
            return

        await self.auth.authenticate_google_oauth(login, senha)
        self.logger.info("✅ Cliente autenticado com sucesso")
    
    def _build_headers(self) -> Dict[str, str]:
        """
        Constrói headers com autenticação e headers browser-like.
        
        IMPORTANTE: Os headers extras (Origin, Referer, sec-*) são necessários
        para evitar erro 500 em alguns endpoints da API.
        
        Returns:
            Dicionário de headers
            
        Raises:
            AuthenticationError: Se token não disponível
        """
        if not self.auth.is_authenticated():
            raise AuthenticationError("Cliente não autenticado")
        
        return {
            # Auth
            "Authorization": f"Bearer {self.auth.token}",
            # Content
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            # Browser identity
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            # CORS/Origin (crítico para evitar 500)
            "Origin": "https://adalove.inteli.edu.br",
            "Referer": "https://adalove.inteli.edu.br/",
            # Sec-* headers
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }

    
    async def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        GET request com retry automático.
        
        Args:
            endpoint: Endpoint da API (ex: "/sections")
            params: Query parameters
            **kwargs: Argumentos adicionais para httpx
            
        Returns:
            Resposta JSON da API
            
        Raises:
            APIError: Em caso de erro na requisição
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._build_headers()
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"📡 GET {endpoint} (tentativa {attempt + 1}/{self.max_retries})")
                
                response = await self.session.get(
                    url, 
                    headers=headers,
                    params=params,
                    **kwargs
                )
                
                # Verificar status code
                if response.status_code == 401:
                    # Token expirado, tentar refresh
                    self.logger.warning("⚠️ Token expirado, tentando refresh...")
                    try:
                        await self.auth.refresh_access_token()
                        headers = self._build_headers()
                        continue
                    except TokenExpiredError:
                        raise AuthenticationError("Token expirado e refresh falhou")
                
                elif response.status_code == 404:
                    raise EndpointNotFoundError(f"Endpoint não encontrado: {endpoint}")
                
                elif response.status_code == 429:
                    # Rate limit
                    retry_after = int(response.headers.get("Retry-After", 60))
                    self.logger.warning(f"⚠️ Rate limit atingido, aguardando {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    continue
                
                elif response.status_code >= 500:
                    # Erro do servidor, tentar novamente
                    self.logger.warning(f"⚠️ Erro do servidor ({response.status_code}), tentando novamente...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                response.raise_for_status()
                
                # Sucesso
                self.logger.debug(f"✅ GET {endpoint} - {response.status_code}")
                return response.json()
            
            except AuthenticationError:
                raise

            except httpx.HTTPStatusError as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"HTTP {e.response.status_code}: {e}")
                await asyncio.sleep(2 ** attempt)
            
            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"Erro de rede: {e}")
                await asyncio.sleep(2 ** attempt)
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"Erro inesperado: {e}")
                await asyncio.sleep(2 ** attempt)
        
        raise APIError(f"Máximo de tentativas excedido para {endpoint}")
    
    async def post(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        POST request com retry automático.
        
        Args:
            endpoint: Endpoint da API
            data: Form data
            json: JSON data
            **kwargs: Argumentos adicionais para httpx
            
        Returns:
            Resposta JSON da API
            
        Raises:
            APIError: Em caso de erro na requisição
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._build_headers()
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"📡 POST {endpoint} (tentativa {attempt + 1}/{self.max_retries})")
                
                response = await self.session.post(
                    url, 
                    headers=headers,
                    data=data,
                    json=json,
                    **kwargs
                )
                
                response.raise_for_status()
                
                self.logger.debug(f"✅ POST {endpoint} - {response.status_code}")
                return response.json()
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"Erro no POST: {e}")
                await asyncio.sleep(2 ** attempt)
        
        raise APIError(f"Máximo de tentativas excedido para {endpoint}")
    
    async def close(self):
        """Fecha a sessão HTTP."""
        await self.session.aclose()
        self.logger.debug("🔒 Sessão HTTP fechada")
    
    async def __aenter__(self):
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
