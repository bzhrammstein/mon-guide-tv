import urllib.request
import xml.etree.ElementTree as ET
import json
import gzip
from datetime import datetime

# Source de confiance (Flux XMLTV compressé en .gz pour aller très vite sans bloquer)
XMLTV_GZ_URL = "https://github.com/v09876/tv-fr/raw/main/guide.xml.gz"

CHAINES_CONFIG = {
    "1": ("TF1", "Freebox / Molotov", "TF1"),
    "2": ("France 2", "Freebox / Molotov", "FRANCE 2"),
    "3": ("France 3", "Freebox / Molotov", "FRANCE 3"),
    "4": ("Canal+", "Freebox / Molotov", "CANAL +"),
    "5": ("France 5", "Freebox / Molotov", "FRANCE 5"),
    "6": ("M6", "Freebox / Molotov", "M6"),
    "7": ("Arte", "Freebox / Molotov", "ARTE"),
    "8": ("C8", "Freebox / Molotov", "C8"),
    "9": ("W9", "Freebox / Molotov", "W9"),
    "10": ("TMC", "Freebox / Molotov", "TMC"),
    "11": ("TFX", "Freebox / Molotov", "TFX"),
    "12": ("RéelsTV", "Freebox / Molotov", "REELS TV"),
    "13": ("LCP Public Sénat", "Freebox / Molotov", "LCP"),
    "14": ("France 4", "Freebox / Molotov", "FRANCE 4"),
    "15": ("BFM TV", "Freebox / Molotov", "BFM TV"),
    "16": ("CNews", "Freebox / Molotov", "CNEWS"),
    "17": ("CStar", "Freebox / Molotov", "CSTAR"),
    "18": ("T18", "Freebox / Molotov", "T18"),
    "19": ("TF1 Series Films", "Freebox / Molotov", "TF1 SERIES"),
    "20": ("L'Equipe", "Freebox / Molotov", "L'EQUIPE"),
    "21": ("6ter", "Freebox / Molotov", "6TER"),
    "22": ("RMC Story", "Freebox / Molotov", "RMC STORY"),
    "23": ("RMC Découverte", "Freebox / Molotov", "RMC DECOUVERTE"),
    "24": ("NOVO", "Freebox / Molotov", "NOVO"),
    "25": ("Ouest-France TV", "Freebox / Molotov", "OUEST FRANCE"),
    "26": ("LCI", "Freebox / Molotov", "LCI"),
    "27": ("Franceinfo", "Freebox / Molotov", "FRANCE INFO"),
    "55": ("Polar+", "Freebox TV", "POLAR PLUS")
}

def main():
    print("Téléchargement du guide de masse compressé...")
    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")
    
    try:
        req = urllib.request.Request(XMLTV_GZ_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with gzip.open(response, 'rb') as f_decompressed:
                xml_content = f_decompressed.read()
                
        print("Décompression réussie. Analyse de l'arborescence...")
        root = ET.fromstring(xml_content)
        
        # Cartographie des chaînes du fichier
        dict_chaines = {}
        for channel in root.findall('channel'):
            c_id = channel.get('id')
            disp = channel.find('display-name')
            if c_id and disp is not None and disp.text:
                dict_chaines[c_id] = disp.text.upper()

        # Extraction exhaustive de tous les programmes du jour
        for prog in root.findall('programme'):
            start = prog.get('start', '')
            if start.startswith(aujourdhui):
                ch_id = prog.get('channel')
                nom_xml = dict_chaines.get(ch_id, "").upper()
                
                for canal, (nom_chaine, source, mot_cle) in CHAINES_CONFIG.items():
                    if mot_cle in nom_xml or nom_xml in mot_cle:
                        heure = f"{start[8:10]}:{start[10:12]}"
                        
                        titre_elem = prog.find('title')
                        titre = titre_elem.text if titre_elem is not None else "Programme"
                        
                        cat_elem = prog.find('category')
                        cat_txt = cat_elem.text.lower() if cat_elem is not None and cat_elem.text else ""
                        
                        genre = "Autre"
                        if "film" in cat_txt or "ciné" in cat_txt: genre = "Film"
                        elif "série" in cat_txt or "feuilleton" in cat_txt: genre = "Série"
                        elif "doc" in cat_txt: genre = "Documentaire"
                        elif "info" in cat_txt or "journal" in cat_txt: genre = "Actualité"
                        
                        programmes_filtres.append({
                            "canal": canal, "heure": heure, "chaine": nom_chaine,
                            "titre": titre, "genre": genre, "source": source
                        })
                        break
                        
    except Exception as e:
        print(f"Erreur technique : {e}")

    # Tri par canal puis par heure
    programmes_filtres.sort(key=lambda x: (int(x['canal']), x['heure']))
    
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Succès : {len(programmes_filtres)} programmes extraits pour aujourd'hui.")

if __name__ == "__main__":
    main()
