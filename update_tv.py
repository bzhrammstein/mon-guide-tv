import urllib.request
import xml.etree.ElementTree as ET
import json

# Flux XMLTV testé
XMLTV_URL = "https://github.com/thegoodb/fr/raw/main/spetnazfr.xml"

CHAINES_CONFIG = {
    "TF1": ("1", "TF1", "Freebox / Molotov"),
    "FRANCE 2": ("2", "France 2", "Freebox / Molotov"),
    "FRANCE 3": ("3", "France 3", "Freebox / Molotov"),
    "CANAL": ("4", "Canal+", "Freebox / Molotov"),
    "FRANCE 5": ("5", "France 5", "Freebox / Molotov"),
    "M6": ("6", "M6", "Freebox / Molotov"),
    "ARTE": ("7", "Arte", "Freebox / Molotov"),
    "C8": ("8", "C8", "Freebox / Molotov"),
    "W9": ("9", "W9", "Freebox / Molotov"),
    "TMC": ("10", "TMC", "Freebox / Molotov"),
    "TFX": ("11", "TFX", "Freebox / Molotov"),
    "LCP": ("13", "LCP Public Sénat", "Freebox / Molotov"),
    "FRANCE 4": ("14", "France 4", "Freebox / Molotov"),
    "BFM": ("15", "BFM TV", "Freebox / Molotov"),
    "CNEWS": ("16", "CNews", "Freebox / Molotov"),
    "CSTAR": ("17", "CStar", "Freebox / Molotov"),
    "SERIES": ("19", "TF1 Series Films", "Freebox / Molotov"),
    "EQUIPE": ("20", "L'Equipe", "Freebox / Molotov"),
    "6TER": ("21", "6ter", "Freebox / Molotov"),
    "STORY": ("22", "RMC Story", "Freebox / Molotov"),
    "DECOU": ("23", "RMC Découverte", "Freebox / Molotov"),
    "LCI": ("26", "LCI", "Freebox / Molotov"),
    "INFO": ("27", "Franceinfo", "Freebox / Molotov"),
    "POLAR": ("55", "Polar+", "Freebox TV")
}

def main():
    print("1. Téléchargement du flux TV...")
    try:
        req = urllib.request.Request(XMLTV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"Erreur téléchargement : {e}")
        return

    print("2. Analyse sans aucun filtre de date...")
    programmes_filtres = []

    try:
        root = ET.fromstring(xml_data)
        
        dict_chaines = {}
        for channel in root.findall('channel'):
            chan_id = channel.get('id', '').upper()
            disp = channel.find('display-name')
            disp_text = disp.text.upper() if disp is not None and disp.text else ""
            if chan_id:
                dict_chaines[chan_id] = f"{chan_id} | {disp_text}"

        # On prend TOUS les programmes du fichier, peu importe le jour
        for prog in root.findall('programme'):
            chan_id = prog.get('channel', '').upper()
            identification_chaine = dict_chaines.get(chan_id, "")
            
            for cle, (canal, nom_propre, source) in CHAINES_CONFIG.items():
                if cle in chan_id or cle in identification_chaine:
                    start_time = prog.get('start', '00000000000000')
                    heure_propre = f"{start_time[8:10]}:{start_time[10:12]}"
                    # On affiche la date brute à côté du titre pour comprendre le décalage
                    date_brute = f"[{start_time[6:8]}/{start_time[4:6]}] "
                    
                    titre_elem = prog.find('title')
                    titre = titre_elem.text if titre_elem is not None else "Programme"
                    
                    programmes_filtres.append({
                        "canal": canal,
                        "heure": heure_propre,
                        "chaine": nom_propre,
                        "titre": date_brute + titre,
                        "genre": "Autre",
                        "source": source
                    })
                    break 

    except Exception as e:
        print(f"Erreur d'analyse XML : {e}")
        return

    # Limiter aux 50 premiers résultats trouvés pour voir ce qu'il contient
    programmes_filtres = programmes_filtres[:50]

    if not programmes_filtres:
        programmes_filtres.append({
            "canal": "0", "heure": "00:00", "chaine": "Diagnostic", 
            "titre": "Le fichier XMLTV téléchargé est totalement vide ou corrompu à la source.", 
            "genre": "Autre", "source": "Freebox"
        })

    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print("Diagnostic terminé.")

if __name__ == "__main__":
    main()
