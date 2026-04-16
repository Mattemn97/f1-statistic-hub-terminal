from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.align import Align
from rich.live import Live

from custom_logger import logger
import client_api

# Inizializzazione Console
console = Console()

def pulisci_schermo():
    console.clear()

def mostra_banner():
    console.print(Panel(Align.center("F1 STATISTICS HUB"), style="bold blue", border_style="cyan"))

def barra_caricamento(descrizione: str, funzione_api, *args, **kwargs):
    """Gestisce il feedback visivo durante le chiamate API."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        transient=True
    ) as progress:
        progress.add_task(description=descrizione, total=None)
        return funzione_api(*args, **kwargs)

def formatta_tempo(secondi):
    """Converte i secondi nel formato F1 (M:SS.ms)"""
    if secondi == float('inf') or secondi is None:
        return "-"
    minuti = int(secondi // 60)
    resti = secondi % 60
    return f"{minuti}:{resti:06.3f}" if minuti > 0 else f"{resti:.3f}"

def selezione_iniziale():
    """Punto di ingresso per la scelta di Anno e Gran Premio."""
    pulisci_schermo()
    mostra_banner()

    anno_input = 0
    lista_anni = [2023, 2024, 2025, 2026]
    lista_gp = []

    # --- CICLO 1: Selezione Anno ---
    while not anno_input in lista_anni:
        anno_input = Prompt.ask("Inserire l'anno della stagione, annate disponibili: 2023, 2024, 2025, 2026").strip().strip('"')
        anno_selezionato = int(anno_input)
        
        # Recupero GP per l'anno inserito
        lista_gp = barra_caricamento(
            f"Recupero calendario {anno_selezionato}...", 
            client_api.recupera_gran_premi_per_anno, 
            anno_selezionato
        )

        # Controllo se ci sono dati per l'anno selezionato
        if not lista_gp:
            console.print(f"[red]Nessun dato trovato per l'anno {anno_selezionato}. Prova con un altro anno.[/red]")
            logger.warning(f"Nessun GP trovato per l'anno: {anno_selezionato}")
            continue # Il ciclo riparte e chiede nuovamente l'anno
            
        # Se siamo arrivati qui, abbiamo un anno valido e una lista di GP. Usciamo dal ciclo dell'anno.
        break 

    # --- TABELLA: Mostra i Gran Premi ---
    tabella = Table(title=f"Gran Premi Stagione {anno_selezionato}")
    tabella.add_column("Indice", style="cyan", justify="right")
    tabella.add_column("Nome Ufficiale", style="white")
    tabella.add_column("Località", style="green")

    # Uso dict.get("chiave", "N/D") per evitare errori se la chiave manca nel JSON/Dizionario
    for i, gp in enumerate(lista_gp):
        tabella.add_row(str(i + 1), gp.get("meeting_official_name", "N/D"), gp.get("location", "N/D"))
    
    console.print(tabella)

    # --- CICLO 2: Selezione Gran Premio ---
    while True:
        scelta_gp = Prompt.ask("Selezionare l'indice del Gran Premio da analizzare (oppure scrivi 'fine' per uscire)").strip()
        
        # Controllo uscita
        if scelta_gp.lower() == "fine":
            logger.info("L'utente ha interrotto la selezione del GP inserendo 'fine'.")
            return None
            
        # Validazione input numerico
        if not scelta_gp.isdigit():
            logger.warning(f"Input GP non numerico: {scelta_gp}")
            console.print("[red]Errore: Inserisci un numero valido o 'fine' per annullare.[/red]")
            continue
            
        indice_scelto = int(scelta_gp)
        
        # Validazione range dell'indice
        if not (1 <= indice_scelto <= len(lista_gp)):
            logger.warning(f"Indice GP non valido o fuori range: {scelta_gp}")
            console.print(f"[red]Errore: L'indice deve essere un numero compreso tra 1 e {len(lista_gp)}.[/red]")
            continue
            
        # Se siamo arrivati qui, l'indice è corretto.
        break

    # Recupero il dizionario/oggetto del GP selezionato
    gp_selezionato = lista_gp[indice_scelto - 1]
    
    # IMPORTANTE: Invece di restituire solo 'True', restituisco i dati reali, 
    # così il resto del tuo programma sa su quale gara lavorare.
    return (anno_selezionato, gp_selezionato)


