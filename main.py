from utils import selezione_iniziale
from menu import menu_principale
from custom_logger import logger

logger.info("F1 STATISTICS HUB inizializzato correttamente.")

def main():
    anno, granpremio = selezione_iniziale()
    menu_principale(granpremio, anno)

if __name__ == "__main__":
    main()