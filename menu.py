from rich.console import Console
from rich.prompt import Prompt, Confirm

import classifiche
import risultati_prove_libere


console = Console()

def menu_principale(gp_selezionato, anno_selezionato):
    """Replica le 'Tab' della pagina web come opzioni di menu."""
    while True:
        console.print(f"[bold]GP Selezionato:[/bold] {gp_selezionato.get('meeting_official_name', 'N/D')} ({anno_selezionato})\n")

        opzioni = {
            "1": "Classifiche (Piloti e Costruttori)",
            "2": "Risultati Prove Libere (FP1, FP2, FP3)",
            "3": "Risultati Qualifiche (Sprint e Standard)",
            "4": "Risultati Gare (Sprint e Domenica)",
            "5": "Analisi Passo Gara",
            "6": "Strategie Gomme",
            "7": "Riassunto Weekend Pilota Specifico",
            "0": "Esci dal Programma"
        }

        for k, v in opzioni.items():
            console.print(f"[cyan]{k}[/cyan]) {v}")

        scelta = Prompt.ask("\nSelezionare l'operazione desiderata", choices=list(opzioni.keys()))

        if scelta == "0":
            break
        elif scelta == "1":
            classifiche.main(gp_selezionato, anno_selezionato)
        elif scelta == "2":
            risultati_prove_libere.main(gp_selezionato, anno_selezionato)
        elif scelta == "3":
            visualizza_risultati_sessione("Qualifying")
        elif scelta == "4":
            visualizza_risultati_sessione("Race")
        elif scelta == "5":
            visualizza_strategie_gomme()
        elif scelta == "6":
            analisi_telemetria_confronto()
        elif scelta == "7":
            mostra_riassunto_pilota()
        else:
            break

        Prompt.ask("\nPremere Invio per tornare al menu...")