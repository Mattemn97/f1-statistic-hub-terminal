import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

class CustomLogger:
    """
    Una classe Logger configurata per salvare i log esclusivamente su file rotativo.
    """

    @staticmethod
    def get_logger(name: str = "ProjectLogger", log_file: str = "app.log", level=logging.DEBUG):
        """
        Ritorna un'istanza di logger configurata solo per file.
        """
        logger = logging.getLogger(name)

        # Evita di aggiungere handler duplicati
        if logger.hasHandlers():
            return logger

        logger.setLevel(level)

        # 1. Formattazione per i log su file
        file_format = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s (%(filename)s:%(lineno)d)'
        )

        # 2. Handler per il File (Rotativo: max 5MB per file, tiene 3 backup)
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True) 
        
        file_handler = RotatingFileHandler(
            log_path / log_file, 
            maxBytes=5*1024*1024, 
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

        return logger

# Istanza pronta all'uso (scriverà solo in logs/app.log)
logger = CustomLogger.get_logger()