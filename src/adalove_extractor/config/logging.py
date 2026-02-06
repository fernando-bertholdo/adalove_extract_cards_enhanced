"""
Configuração de logging do sistema.
"""

import logging
import os
from datetime import datetime


def configure_logging(
    nome_turma: str, 
    log_dir: str = "logs",
    log_level: str = "INFO"
) -> logging.Logger:
    """
    Configura logging para arquivo e console.
    
    Args:
        nome_turma: Nome da turma para prefixo do arquivo
        log_dir: Diretório para salvar logs
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger configurado
        
    Example:
        >>> logger = configure_logging("modulo6")
        >>> logger.info("Extração iniciada")
    """
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"{nome_turma}_{timestamp}.log")
    
    # Converte string de nível para constante
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Remove handlers existentes
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # File handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
    file_handler.setFormatter(file_formatter)
    
    # Console handler - sempre DEBUG para debug detalhado
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
    console_handler.setFormatter(console_formatter)
    
    # Configura root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Nível mais baixo para capturar tudo
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"📝 Log salvo em: {log_filename}")
    
    return logger





