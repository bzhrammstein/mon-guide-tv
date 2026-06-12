import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Changement pour une source professionnelle majeure et redondante
XMLTV_URL = "https://xmltv.ch/xmltv/xmltv-fr.xml"

CHAINES_TNT_CIBLES = ["TF1", "FRANCE 2", "FRANCE 3", "CANAL+", "FRANCE 5", "M6", "ARTE", "C8", "W9", "TMC", "TFX", "NRJ12", "NRJ 12", "FRANCE 4", "BFM", "CNEWS", "LCI", "FRANCEINFO", "FRANCE INFO"]
CHAINES_SAMSUNG_CIBLES = ["COMEDY", "RAKUTEN", "PLUTO", "DOCTOR WHO"]

def convertir_heure(xml_date):
    try:
        return f"{xml_date[8:10]}:{xml_date[10:12]}"
    except:
        return "00:00"

def main():
    print("1. Téléchargement du guide TV de secours...")
    try:
        req = urllib.request.Request(XMLTV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        print(f"Téléchargement réussi : {len(xml_data)} octets.")
    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        # En cas de panne sèche, on crée un fichier de secours pour éviter la 404
        sauvegarder_secours("Le serveur XMLTV est indisponible ce matin.")
        return

    print("2. Analyse du XML...")
    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")

    try:
        root = ET.fromstring(xml_data)
        dict_chaines = {}
        for channel in root.findall('channel'):
            chan_id = channel.get('id')
            disp = channel.find('display-name')
            if chan_id and disp is not None and disp.text:
                dict_chaines[chan_id] = disp.text.upper()

        for prog in root.findall('programme'):
            start_time = prog.get('start')
            
            if start_time and start_time.startswith(aujourdhui):
                chan_id = prog.get('channel')
                nom_chaine = dict_chaines.get(chan_id, "").upper()
                
                source = None
                if any(tnt in nom_chaine for tnt in CHAINES_TNT_CIBLES):
                    source = "TNT"
                elif any(sam in nom_chaine for sam in CHAINES_SAMSUNG_CIBLES):
                    source = "Samsung TV Plus"
                
                if source:
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
                        "heure": convertir_heure(start_time),
                        "chaine": nom_chaine.title(),
                        "titre": titre,
                        "genre": genre,
                        "source": source
                    })

    except Exception as e:
        print(f"Erreur d'analyse : {e}")
        sauvegarder_secours(f"Erreur technique d'analyse : {e}")
        return

    programmes_filtres.sort(key=lambda x: x['heure'])
    
    if not programmes_filtres:
        sauvegarder_secours(f"Aucune émission trouvée dans le flux pour la date du {aujourdhui}.")
        return

    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print("Fichier programmes.json généré avec succès.")

def sauvegarder_secours(message):
    # Permet de toujours écrire un fichier pour détruire définitivement l'erreur 404
    secours = [{
        "heure": "00:00", 
        "chaine": "Avis Système", 
        "titre": message, 
        "genre": "Autre", 
        "source": "TNT"
    }]
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(secours, f, ensure_ascii=False, indent=4)
    print("Fichier de secours généré.")

if __name__ == "__main__":
    main()
