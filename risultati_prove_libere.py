import client_api
from custom_logger import logger
from utils import barra_caricamento, pulisci_schermo, formatta_tempo
from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

console = Console()

def elabora_risultati_prove_libere(piloti_crudi, giri_crudi):
    """
    Aggrega i dati dei giri per ogni pilota
    e calcola i migliori settori e il miglior tempo totale.
    """
    logger.info(f"Elaborazione risultati: {len(piloti_crudi)} piloti e {len(giri_crudi)} giri.")
    
    statistiche = {}
    
    # Inizializzazione statistiche per pilota
    for p in piloti_crudi:
        num = p.get('driver_number')
        statistiche[num] = {
            "numero": num,
            "nome": p.get('broadcast_name', 'Sconosciuto'),
            "colore_team": p.get('team_colour', 'FFFFFF'),
            "miglior_giro": float('inf'),
            "s1": float('inf'), 
            "s2": float('inf'), 
            "s3": float('inf'),
            "giri_totali": 0
        }

    # Elaborazione giri
    for giro in giri_crudi:
        num = giro.get('driver_number')
        if num not in statistiche:
            continue
            
        stat = statistiche[num]
        stat["giri_totali"] += 1
        
        # Miglior giro totale
        durata = giro.get('lap_duration')
        if durata and durata < stat["miglior_giro"]:
            stat["miglior_giro"] = durata
            
        # Migliori settori (Best personal)
        s1, s2, s3 = giro.get('duration_sector_1'), giro.get('duration_sector_2'), giro.get('duration_sector_3')
        if s1 and s1 < stat["s1"]: stat["s1"] = s1
        if s2 and s2 < stat["s2"]: stat["s2"] = s2
        if s3 and s3 < stat["s3"]: stat["s3"] = s3

    # Filtraggio (chi ha fatto almeno un giro) e ordinamento
    classifica = [p for p in statistiche.values() if p["giri_totali"] > 0]
    classifica.sort(key=lambda x: x["miglior_giro"])
    
    return classifica

def genera_tabella_sessione(chiave_sessione, nome_sessione):
    """
    Simile alla vecchia 'visualizza_sessione_libere', 
    ma invece di stampare, RESTITUISCE l'oggetto Table.
    """
    if not chiave_sessione:
        return Panel(f"[yellow]Sessione {nome_sessione}\nnon disponibile[/]", width=30)

    try:
        piloti = client_api.recupera_piloti(chiave_sessione)
        giri = client_api.recupera_giri(chiave_sessione)
        risultati = elabora_risultati_prove_libere(piloti, giri)
        
        if not risultati:
            return Panel(f"[red]{nome_sessione}\nNessun dato[/]", width=30)

        # Creiamo la tabella (riduciamo un po' le larghezze per favorire l'affiancamento)
        tabella = Table(title=f"RISULTATI {nome_sessione.upper()}", header_style="bold cyan", title_style="bold")
        tabella.add_column("P", justify="center")
        tabella.add_column("Pilota")
        tabella.add_column("Tempo", justify="center")
        tabella.add_column("S1", justify="center")
        tabella.add_column("S2", justify="center")
        tabella.add_column("S3", justify="center")
        tabella.add_column("Giri", justify="center")

        for i, p in enumerate(risultati):
            pos = i + 1
            stile_tempo = "bold #b92df7" if i == 0 else "bold white"
            nome_pilota = Text(p['nome'], style=f"#{p['colore_team']}") # Tagliamo il nome se troppo lungo

            tabella.add_row(
                str(pos),
                nome_pilota,
                Text(formatta_tempo(p['miglior_giro']), style=stile_tempo),
                f"{p['s1']:.1f}" if p['s1'] != float('inf') else "-", 
                f"{p['s2']:.1f}" if p['s2'] != float('inf') else "-",
                f"{p['s3']:.1f}" if p['s3'] != float('inf') else "-",
                str(p['giri_totali'])
            )
        return tabella

    except Exception as e:
        return Panel(f"[red]Errore {nome_sessione}[/]", width=30)

def main(granpremio, anno):
    pulisci_schermo()
    chiave_m = granpremio.get("meeting_key")
    nome_gp = granpremio.get("meeting_official_name", "N/D")

    console.print(Panel(f"[bold white]PROVE LIBERE[/] - {nome_gp} ({anno})", expand=True))

    sessioni = client_api.recupera_sessioni_per_gran_premio(chiave_m)
    mappa_sessioni = {s['session_name']: s['session_key'] for s in sessioni if 'Practice' in s['session_name']}

    tabelle_da_mostrare = []

    with console.status("[bold yellow]Elaborazione sessioni...[/]"):
        # Generiamo le tabelle e le mettiamo in una lista
        t1 = genera_tabella_sessione(mappa_sessioni.get("Practice 1"), "PL 1")
        t2 = genera_tabella_sessione(mappa_sessioni.get("Practice 2"), "PL 2")
        t3 = genera_tabella_sessione(mappa_sessioni.get("Practice 3"), "PL 3")
        
        tabelle_da_mostrare = [t1, t2, t3]

    # Visualizziamo tutto affiancato
    console.print(Columns(tabelle_da_mostrare, equal=True, expand=True))