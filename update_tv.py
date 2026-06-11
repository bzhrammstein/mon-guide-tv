import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Flux XMLTV alternatif ultra-léger et stable
XMLTV_URL = "https://xmltvfr.fr/xmltv/programmes.xml"

CHAINES_TNT = ["TF1", "France 2", "France 3", "Canal+", "France 5", "M6", "Arte", "C8", "W9", "TMC", "TFX", "NRJ 12", "France 4", "BFM TV", "CNews", "LCI", "Franceinfo"]
CHAINES_SAMSUNG = ["Comedy Central Grand Réseau", "Rakuten TV Films Action", "Pluto TV Ciné", "Doctor Who TV"]

def convertir_heure(xml_date):
    try:
        # Extrait l'heure (ex: "20260611211000" -> "21:10")
        return f"{xml_date[8:10]}:{xml_date[10:12]}"
    except:
        return "00:00"

def main():
    print("Téléchargement du fichier XMLTV...")
    try:
        # Configuration d'un en-tête pour éviter les blocages serveurs
        req = urllib.request.Request(XMLTV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open("tv.xml", "wb") as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        return

    print("Analyse du fichier XML...")
    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")

    try:
        # Lecture pas à pas pour éviter de surcharger la mémoire
        context = ET.iterparse("tv.xml", events=("start", "end"))
        dict_chaines = {}
        
        # Premier passage pour lister les chaînes
        for event, elem in context:
            if event == "end" and elem.tag == "channel":
                chan_id = elem.get("id")
                disp = elem.find("display-name")
                if chan_id and disp is not None:
                    dict_chaines[chan_id] = disp.text
                elem.clear()

        # Second passage pour les programmes
        context = ET.iterparse("tv.xml", events=("start", "end"))
        for event, elem in context:
            if event == "end" and elem.tag == "programme":
                start_time = elem.get("start")
                
                if start_time and start_time.startswith(aujourdhui):
                    chan_id = elem.get("channel")
                    nom_chaine = dict_chaines.get(chan_id, chan_id)
                    
                    source = None
                    if nom_chaine in CHAINES_TNT: source = "TNT"
                    elif nom_chaine in CHAINES_SAMSUNG: source = "Samsung TV Plus"
                    
                    if source:
                        titre_elem = elem.find("title")
                        titre = titre_elem.text if titre_elem is not None else "Programme"
                        
                        genre = "Autre"
                        cat_elem = elem.find("category")
                        if cat_elem is not None and cat_elem.text:
                            cat_txt = cat_elem.text.lower()
                            if "film" in cat_txt or "ciné" in cat_txt: genre = "Film"
                            elif "série" in cat_txt or "feuilleton" in cat_txt: genre = "Série"
                            elif "doc" in cat_txt: genre = "Documentaire"
                            elif "info" in cat_txt or "journal" in cat_txt: genre = "Actualité"

                        programmes_filtres.append({
                            "heure": convertir_heure(start_time),
                            "chaine": nom_chaine,
                            "titre": titre,
                            "genre": genre,
                            "source": source
                        })
                elem.clear()
    except Exception as e:
        print(f"Erreur pendant l'analyse XML : {e}")

    # Tri et sauvegarde
    programmes_filtres.sort(key=lambda x: x['heure'])
    
    # Si le tri est vide, on met une donnée de secours pour éviter que la page web bugge
    if not programmes_filtres:
        programmes_filtres.append({
            "heure": "12:00", "chaine": "Système", "titre": "Mise à jour en cours", "genre": "Autre", "source": "TNT"
        })

    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print("Fichier programmes.json généré.")

if __name__ == "__main__":
    main()
