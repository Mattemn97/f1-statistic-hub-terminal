from custom_logger import logger
import client_api
from utils import barra_caricamento, pulisci_schermo
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from collections import defaultdict

console = Console()

def main(granpremio, anno):
    pulisci_schermo()
    
    chiave_m_selezionato = granpremio.get("meeting_key")
    nome_gp = granpremio.get('meeting_official_name', 'N/D')

    console.print(Panel(f"[bold f1_red]F1 STATISTICS HUB[/] - {nome_gp} ({anno})", expand=False))
    logger.info(f"Avvio elaborazione classifiche con aggregazione lato client per {nome_gp}")

    # 1. Recupero Calendario
    lista_gp_totale = barra_caricamento(f"Caricamento calendario {anno}...", client_api.recupera_gran_premi_per_anno, anno)
    indice_corrente = next((i for i, gp in enumerate(lista_gp_totale) if gp['meeting_key'] == chiave_m_selezionato), len(lista_gp_totale))
    gp_passati = lista_gp_totale[:indice_corrente + 1]
    
    # 2. Recupero info base (Essenziale per mappare Pilota -> Team)
    sessioni_gp_corrente = client_api.recupera_sessioni_per_gran_premio(chiave_m_selezionato)
    gara_corrente = next((s for s in sessioni_gp_corrente if s['session_name'] == 'Race'), sessioni_gp_corrente[-1])
    info_piloti_raw = client_api.recupera_piloti(gara_corrente['session_key'])
    
    # Mappe di utilità
    colori_team = {p.get('team_name'): p.get('team_colour', 'FFFFFF') for p in info_piloti_raw}
    mappa_pilota_team = {p.get('driver_number'): p.get('team_name') for p in info_piloti_raw}
    nomi_piloti = {p.get('driver_number'): p.get('broadcast_name') for p in info_piloti_raw}

    # 3. Recupero Storico PILOTI (Unica chiamata API per GP)
    storico_piloti = []
    
    with console.status("[bold yellow]Analisi storica in corso (Solo Piloti)...[/]") as status:
        for gp in gp_passati:
            sigla = gp.get("country_code", "GP")
            sessioni = client_api.recupera_sessioni_per_gran_premio(gp['meeting_key'])
            gara = next((s for s in sessioni if s['session_name'] == 'Race'), None)
            
            if gara:
                status.update(f"[bold yellow]Scaricando dati piloti: {sigla}...[/]")
                # Facciamo SOLO la chiamata piloti
                class_p = client_api.recupera_classifica_piloti(gara['session_key'])
                storico_piloti.append({"sigla": sigla, "dati": class_p or []})

    if not storico_piloti:
        console.print("[red]Dati non disponibili.[/]")
        return

    # --- TABELLA PILOTI ---
    tabella_piloti = Table(title="CLASSIFICA MONDIALE PILOTI", header_style="bold magenta")
    tabella_piloti.add_column("Pos", justify="right", style="cyan")
    tabella_piloti.add_column("Pilota", width=25)
    for s in storico_piloti:
        tabella_piloti.add_column(s["sigla"], justify="center")
    tabella_piloti.add_column("Totale", justify="right", style="bold green")

    ultima_class_p = sorted(storico_piloti[-1]["dati"], key=lambda x: (x.get('position_current') or 999))

    for r in ultima_class_p:
        d_num = r.get('driver_number')
        t_name = mappa_pilota_team.get(d_num, "N/D")
        colore = colori_team.get(t_name, "FFFFFF")
        
        txt_pilota = Text(nomi_piloti.get(d_num, f"Pilota {d_num}"))
        txt_pilota.stylize(f"#{colore}")

        punti_per_gp = []
        prec = 0
        for tappa in storico_piloti:
            rec = next((p for p in tappa["dati"] if p['driver_number'] == d_num), None)
            att = rec.get('points_current', prec) if rec and rec.get('points_current') is not None else prec
            guadagno = max(0, att - prec)
            prec = att
            punti_per_gp.append(f"[bold white]{guadagno}[/]" if guadagno > 0 else "[grey50]-[/]")

        tabella_piloti.add_row(str(r.get('position_current') or "-"), txt_pilota, *punti_per_gp, str(r.get('points_current') or "0"))

    console.print(tabella_piloti)
    console.print("\n")

    # --- TABELLA COSTRUTTORI (Aggregata localmente) ---
    # Ricostruiamo la struttura dei punti per i team partendo dai dati piloti
    tabella_team = Table(title="CLASSIFICA MONDIALE COSTRUTTORI (Aggregata)", header_style="bold magenta")
    tabella_team.add_column("Pos", justify="right", style="cyan")
    tabella_team.add_column("Scuderia", width=25)
    for s in storico_piloti:
        tabella_team.add_column(s["sigla"], justify="center")
    tabella_team.add_column("Totale", justify="right", style="bold green")

    # Calcolo punti totali per team per l'ordinamento
    punti_totali_team = defaultdict(float)
    for p in storico_piloti[-1]["dati"]:
        t_name = mappa_pilota_team.get(p['driver_number'])
        if t_name:
            punti_totali_team[t_name] += (p.get('points_current') or 0)

    # Ordinamento team per punti decrescenti
    team_ordinati = sorted(punti_totali_team.items(), key=lambda x: x[1], reverse=True)

    for pos, (t_name, totale) in enumerate(team_ordinati, 1):
        colore = colori_team.get(t_name, "FFFFFF")
        txt_team = Text(t_name, style=f"#{colore}")

        punti_per_gp_team = []
        prec_team = 0
        
        for tappa in storico_piloti:
            # Sommiamo il guadagno di tutti i piloti di questo team in questa tappa
            punti_tappa_team = 0
            for p in tappa["dati"]:
                if mappa_pilota_team.get(p['driver_number']) == t_name:
                    # Troviamo il guadagno del pilota in questa tappa (punti_attuali - punti_precedenti_nello_storico)
                    # Per semplicità qui calcoliamo i punti correnti totali del team alla tappa X
                    punti_tappa_team += (p.get('points_current') or 0)
            
            guadagno_team = max(0, punti_tappa_team - prec_team)
            prec_team = punti_tappa_team
            punti_per_gp_team.append(f"[bold white]{guadagno_team}[/]" if guadagno_team > 0 else "[grey50]-[/]")

        tabella_team.add_row(str(pos), txt_team, *punti_per_gp_team, str(int(totale)))

    console.print(tabella_team)