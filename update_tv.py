import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Utilisation d'un flux XMLTV public fiable pour la TNT Française
XMLTV_URL = "https://xmltv.ch/xmltv/xmltv-fr.xml"

# Configuration de vos chaînes préférées pour éviter d'être noyé sous 400 chaînes
# Vous pourrez modifier cette liste à tout moment !
CHAINES_TNT = ["TF1", "France 2", "France 3", "Canal+", "France 5", "M6", "Arte", "C8", "W9", "TMC", "TFX", "NRJ 12", "LCP Public Sénat", "France 4", "BFM TV", "CNews", "LCI", "Franceinfo"]
CHAINES_SAMSUNG = ["Comedy Central Grand Réseau", "Rakuten TV Films Action", "Pluto TV Ciné", "Doctor Who TV"]

def convertir_heure(xml_date):
    # Format XMLTV : "20260611211000 +0200" -> Extrait "21:10"
    try:
        heure_brute = xml_date.split()[0][8:12]
        return f"{heure_brute[0:2]}:{heure_brute[2:4]}"
    except:
        return "00:00"

def main():
    print("1. Téléchargement de la grille TV du jour...")
    try:
        urllib.request.urlretrieve(XMLTV_URL, "tv.xml")
    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        return

    print("2. Analyse et filtrage des programmes...")
    tree = ET.parse("tv.xml")
    root = tree.getOrCreate() if hasattr(tree, 'getOrCreate') else tree.getroot()
    
    # Étape essentielle : créer une correspondance entre l'identifiant technique XML et le nom clair de la chaîne
    dict_chaines = {}
    for channel in root.findall('channel'):
        chan_id = channel.get('id')
        display_name = channel.find('display-name').text
        dict_chaines[chan_id] = display_name

    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")

    for prog in root.findall('programme'):
        start_time = prog.get('start')
        
        # On ne garde que les programmes qui commencent aujourd'hui
        if start_time and start_time.startswith(aujourdhui):
            chan_id = prog.get('channel')
            nom_chaine = dict_chaines.get(chan_id, chan_id)
            
            source = None
            if nom_chaine in CHAINES_TNT:
                source = "TNT"
            elif nom_chaine in CHAINES_SAMSUNG:
                source = "Samsung TV Plus"
                
            if source:
                titre = prog.find('title').text if prog.find('title') is not None else "Sans titre"
                
                # Détermination simplifiée du genre
                genre = "Autre"
                category = prog.find('category')
                if category is not None and category.text:
                    cat_txt = category.text.lower()
                    if "film" in cat_txt or "ciné" in cat_txt: genre = "Film"
                    elif "série" in cat_txt or "feuilleton" in cat_txt: genre = "Série"
                    elif "doc" in cat_txt or "histoire" in cat_txt: genre = "Documentaire"
                    elif "journal" in cat_txt or "info" in cat_txt or "météo" in cat_txt: genre = "Actualité"

                programmes_filtres.append({
                    "heure": convertir_heure(start_time),
                    "chaine": nom_chaine,
                    "titre": titre,
                    "genre": genre,
                    "source": source
                })

    # Tri par ordre chronologique
    programmes_filtres.sort(key=lambda x: x['heure'])

    print(f"3. Sauvegarde de {len(programmes_filtres)} programmes nettoyés...")
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
