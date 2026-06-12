import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Flux XMLTV de secours (ultra-stable et mis à jour très tôt le matin)
XMLTV_URL = "https://xmltvfr.fr/xmltv/programmes.xml"

# On simplifie la recherche : si le nom de la chaîne contient un de ces mots, on la garde !
CHAINES_TNT_CIBLES = ["TF1", "FRANCE 2", "FRANCE 3", "CANAL+", "FRANCE 5", "M6", "ARTE", "C8", "W9", "TMC", "TFX", "NRJ 12", "FRANCE 4", "BFM", "CNEWS", "LCI", "FRANCEINFO"]
CHAINES_SAMSUNG_CIBLES = ["COMEDY", "RAKUTEN", "PLUTO", "DOCTOR WHO"]

def convertir_heure(xml_date):
    try:
        return f"{xml_date[8:10]}:{xml_date[10:12]}"
    except:
        return "00:00"

def main():
    print("1. Téléchargement du fichier XMLTV...")
    try:
        req = urllib.request.Request(XMLTV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open("tv.xml", "wb") as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        return

    print("2. Analyse du fichier...")
    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")
    print(f"Recherche des programmes pour la date du : {aujourdhui}")

    try:
        context = ET.iterparse("tv.xml", events=("start", "end"))
        dict_chaines = {}
        
        # Récupération des noms de chaînes
        for event, elem in context:
            if event == "end" and elem.tag == "channel":
                chan_id = elem.get("id")
                disp = elem.find("display-name")
                if chan_id and disp is not None and disp.text:
                    dict_chaines[chan_id] = disp.text.upper() # Tout en majuscules pour comparer sans erreur
                elem.clear()

        # Récupération des programmes
        context = ET.iterparse("tv.xml", events=("start", "end"))
        for event, elem in context:
            if event == "end" and elem.tag == "programme":
                start_time = elem.get("start")
                
                if start_time and start_time.startswith(aujourdhui):
                    chan_id = elem.get("channel")
                    nom_chaine_brut = dict_chaines.get(chan_id, "").upper()
                    
                    source = None
                    # Vérification souple (ex: si "TF1 HD" contient "TF1")
                    if any(tnt in nom_chaine_brut for tnt in CHAINES_TNT_CIBLES):
                        source = "TNT"
                    elif any(sam in nom_chaine_brut for sam in CHAINES_SAMSUNG_CIBLES):
                        source = "Samsung TV Plus"
                    
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

                        # On redonne un joli nom propre à la chaîne pour l'affichage
                        nom_affiche = nom_chaine_brut.title()

                        programmes_filtres.append({
                            "heure": convertir_heure(start_time),
                            "chaine": nom_affiche,
                            "titre": titre,
                            "genre": genre,
                            "source": source
                        })
                elem.clear()
    except Exception as e:
        print(f"Erreur d'analyse XML : {e}")

    # Tri par heure
    programmes_filtres.sort(key=lambda x: x['heure'])
    
    # Si la liste est vide, on injecte de fausses lignes explicites pour comprendre le souci
    if not programmes_filtres:
        programmes_filtres.append({
            "heure": "00:00", 
            "chaine": "Information", 
            "titre": f"Le fichier XML ne contenait aucun programme pour aujourd'hui ({aujourdhui}).", 
            "genre": "Autre", 
            "source": "TNT"
        })

    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Sauvegarde effectuée. {len(programmes_filtres)} programmes enregistrés.")

if __name__ == "__main__":
    main()
