import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Flux XMLTV complet et stable
XMLTV_URL = "https://github.com/thegoodb/fr/raw/main/spetnazfr.xml"

# Configuration ultra-souple par mots-clés simplifiés (en MAJUSCULES)
CHAINES_CONFIG = {
    # --- TNT & FREEBOX ---
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
    "REELS": ("12", "RéelsTV", "Freebox / Molotov"),
    "LCP": ("13", "LCP Public Sénat", "Freebox / Molotov"),
    "FRANCE 4": ("14", "France 4", "Freebox / Molotov"),
    "BFM": ("15", "BFM TV", "Freebox / Molotov"),
    "CNEWS": ("16", "CNews", "Freebox / Molotov"),
    "CSTAR": ("17", "CStar", "Freebox / Molotov"),
    "T18": ("18", "T18", "Freebox / Molotov"),
    "SERIES": ("19", "TF1 Series Films", "Freebox / Molotov"),
    "EQUIPE": ("20", "L'Equipe", "Freebox / Molotov"),
    "6TER": ("21", "6ter", "Freebox / Molotov"),
    "STORY": ("22", "RMC Story", "Freebox / Molotov"),
    "DECOU": ("23", "RMC Découverte", "Freebox / Molotov"),
    "NOVO": ("24", "NOVO", "Freebox / Molotov"),
    "OUEST": ("25", "Ouest-France TV", "Freebox / Molotov"),
    "LCI": ("26", "LCI", "Freebox / Molotov"),
    "INFO": ("27", "Franceinfo", "Freebox / Molotov"),

    # --- THEMATIQUES FREEBOX ---
    "PREM": ("28", "Paris Première", "Freebox TV"),
    "RTL9": ("29", "RTL 9", "Freebox TV"),
    "TEVA": ("53", "Téva", "Freebox TV"),
    "BREIZH": ("54", "TV Breizh", "Freebox TV"),
    "POLAR": ("55", "Polar+", "Freebox TV"),
    "ACTION": ("82", "Action", "Freebox TV"),
    "GAME": ("118", "Game One", "Freebox TV"),
    "MANGA": ("121", "Mangas", "Freebox TV"),
    "HISTOIRE": ("205", "Histoire TV", "Freebox TV"),
    "SCIENCE": ("207", "Science & Vie TV", "Freebox TV"),
    "USHUA": ("204", "Ushuaïa TV", "Freebox TV"),

    # --- SAMSUNG TV PLUS ---
    "COMEDY": ("4124", "Comedy Central", "Samsung TV Plus"),
    "CINE": ("4142", "Pluto TV Ciné", "Samsung TV Plus"),
    "RAKUTEN": ("4112", "Rakuten TV Action", "Samsung TV Plus"),
    "DOCTOR": ("4304", "Doctor Who TV", "Samsung TV Plus"),
    "SERI": ("4145", "Pluto TV Séries", "Samsung TV Plus")
}

def convertir_heure(xml_date):
    try:
        return f"{xml_date[8:10]}:{xml_date[10:12]}"
    except:
        return "00:00"

def main():
    print("1. Téléchargement du flux TV...")
    try:
        req = urllib.request.Request(XMLTV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"Erreur téléchargement : {e}")
        return

    print("2. Analyse et indexation des chaînes...")
    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")

    try:
        root = ET.fromstring(xml_data)
        
        # Étape clé : On scanne tous les formats d'ID et de noms du fichier XML
        dict_chaines = {}
        for channel in root.findall('channel'):
            chan_id = channel.get('id', '').upper()
            disp = channel.find('display-name')
            disp_text = disp.text.upper() if disp is not None and disp.text else ""
            
            if chan_id:
                # On stocke l'ID et le nom d'affichage pour maximiser les chances
                dict_chaines[chan_id] = f"{chan_id} | {disp_text}"

        print(f"Indexation terminée : {len(dict_chaines)} chaînes mémorisées.")

        # Extraction des programmes
        for prog in root.findall('programme'):
            start_time = prog.get('start')
            
            if start_time and start_time.startswith(aujourdhui):
                chan_id = prog.get('channel', '').upper()
                # On récupère le bloc texte associé à cette chaîne
                identification_chaine = dict_chaines.get(chan_id, "")
                
                # Test de correspondance ultra-large
                for cle, (canal, nom_propre, source) in CHAINES_CONFIG.items():
                    if cle in chan_id or cle in identification_chaine:
                        titre_elem = prog.find('title')
                        titre = titre_elem.text if titre_elem is not None else "Programme"
                        
                        genre = "Autre"
                        cat_elem = prog.find('category')
                        if cat_elem is not None and cat_elem.text:
                            cat_txt = cat_elem.text.lower()
                            if "film" in cat_txt or "ciné" in cat_txt: genre = "Film"
                            elif "série" in cat_txt or "feuilleton" in cat_txt: genre = "Série"
                            elif "doc" in cat_txt: genre = "Documentaire"
                            elif "info" in cat_txt or "journal" in cat_txt: genre = "Actualité"

                        programmes_filtres.append({
                            "canal": canal,
                            "heure": convertir_heure(start_time),
                            "chaine": nom_propre,
                            "titre": titre,
                            "genre": genre,
                            "source": source
                        })
                        break 

    except Exception as e:
        print(f"Erreur d'analyse XML : {e}")
        return

    # Tri chronologique
    programmes_filtres.sort(key=lambda x: x['heure'])
    
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Extraction réussie : {len(programmes_filtres)} programmes injectés.")

if __name__ == "__main__":
    main()
