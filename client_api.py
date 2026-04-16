import time
import requests
from typing import List, Dict, Any, Optional
from custom_logger import logger

"""
Client Python per l'interfaccia con le API di OpenF1.
Ottimizzato per la gestione di risposte JSON e persistenza della sessione.
"""

INDIRIZZO_BASE = "https://api.openf1.org/v1"
ATTESA_ANTI_FLOOD = 1.0  # Secondi tra le richieste

# Inizializzazione della sessione per migliorare le performance (Keep-Alive)
http_client = requests.Session()

def esegui_richiesta(endpoint: str, parametri: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Gestione centralizzata delle chiamate HTTP con parsing JSON automatico.
    """
    url = f"{INDIRIZZO_BASE}{endpoint}"
    
    # Rispetto del rate-limiting
    time.sleep(ATTESA_ANTI_FLOOD)
    
    try:
        logger.debug(f"Richiesta GET: {url} - Parametri: {parametri}")
        
        # Esecuzione della richiesta
        risposta = http_client.get(url, params=parametri, timeout=20)
        
        # Solleva un'eccezione per status code 4xx o 5xx
        risposta.raise_for_status()
        
        # Decodifica il JSON direttamente in una lista di dizionari
        dati_json = risposta.json()
        
        return dati_json if dati_json is not None else []

    except requests.exceptions.HTTPError as e:
        logger.error(f"Errore HTTP su {endpoint}: {e.response.status_code} - {e.response.text}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore di rete durante la chiamata a {endpoint}: {e}")
        return []
    except Exception as e:
        logger.critical(f"Errore critico durante il parsing JSON o l'esecuzione: {e}", exc_info=True)
        return []

# --- Wrapper API OpenF1 ---

def recupera_gran_premi_per_anno(anno: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/meetings", {"year": anno})

def recupera_sessioni_per_gran_premio(chiave_meeting: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/sessions", {"meeting_key": chiave_meeting})

def recupera_tutte_sessioni_per_anno(anno: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/sessions", {"year": anno})

def recupera_classifica_piloti_meeting(chiave_meeting: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/championship_drivers", {"meeting_key": chiave_meeting})

def recupera_classifica_costruttori_meeting(chiave_meeting: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/championship_teams", {"meeting_key": chiave_meeting})

def recupera_classifica_piloti(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/championship_drivers", {"session_key": chiave_sessione})

def recupera_classifica_costruttori(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/championship_teams", {"session_key": chiave_sessione})

def recupera_piloti(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/drivers", {"session_key": chiave_sessione})

def recupera_giri(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/laps", {"session_key": chiave_sessione})

def recupera_posizioni(chiave_meeting: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/position", {"meeting_key": chiave_meeting})

def recupera_intervalli(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/intervals", {"session_key": chiave_sessione})

def recupera_dati_vettura(chiave_sessione: int, numero_vettura: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/car_data", {"session_key": chiave_sessione, "driver_number": numero_vettura})

def recupera_posizione_in_pista(chiave_sessione: int, numero_vettura: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/location", {"session_key": chiave_sessione, "driver_number": numero_vettura})

def recupera_stint_gomme(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/stints", {"session_key": chiave_sessione})

def recupera_soste_ai_box(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/pit", {"session_key": chiave_sessione})

def recupera_direzione_gara(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/race_control", {"session_key": chiave_sessione})

def recupera_comunicazioni_radio(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/team_radio", {"session_key": chiave_sessione})

def recupera_dati_meteo(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/weather", {"session_key": chiave_sessione})

def recupera_dettagli_sessione(chiave_sessione: int) -> List[Dict[str, Any]]:
    return esegui_richiesta("/sessions", {"session_key": chiave_sessione})