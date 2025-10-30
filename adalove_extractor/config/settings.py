"""
Configurações do sistema usando Pydantic Settings.

Carrega configurações do arquivo .env e permite override via variáveis de ambiente.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações centralizadas do sistema.
    
    Carrega valores de .env e permite override via variáveis de ambiente.
    """
    
    # === Autenticação ===
    login: str = ""
    senha: str = ""
    
    # === Diretórios ===
    output_dir: str = "dados_extraidos"
    logs_dir: str = "logs"
    
    # === Playwright ===
    headless: bool = False
    browser_channel: str = "chrome"
    timeout_ms: int = 30000
    
    # === Extração ===
    max_retries: int = 3
    interactive: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override interactive se variável de ambiente estiver definida
        if os.getenv("ADALOVE_INTERACTIVE", "").lower() in ("false", "0", "no"):
            self.interactive = False
    
    # === Enriquecimento ===
    enable_anchoring: bool = True
    timezone_offset: str = "-03:00"
    
    # === Logging ===
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def validate_credentials(self) -> bool:
        """
        Valida se as credenciais foram configuradas.
        
        Returns:
            True se login e senha estão definidos
        """
        return bool(self.login and self.senha)


# Singleton de settings
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Retorna instância singleton de Settings.
    
    Returns:
        Objeto Settings configurado
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings







