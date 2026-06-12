import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Utilisation d'une source communautaire ultra-accessible pour les serveurs Cloud
XMLTV_URL = "https://raw.githubusercontent.com/Polyedre/xmltv-france/master/tvguide.xml"

# Mots-clés simplifiés au maximum pour matcher les chaînes (ex: "TF1" captera "TF1", "TF1 HD", etc.)
CHAINES_TNT_CIBLES = ["TF1", "FRANCE 2", "FRANCE 3", "CANAL+", "FRANCE 5", "M6", "ARTE", "C8", "W9", "TMC", "TFX", "NRJ12", "NRJ 12", "FRANCE 4", "BFM", "CNEWS", "LCI", "FRANCEINFO", "FRANCE INFO"]
CHAINES_SAMSUNG_CIBLES = ["COMEDY", "RAKUTEN", "PLUTO", "DOCTOR WHO"]

def convertir_heure(xml_date):
    try:
        # Format XMLTV standard : "20260612211000 +0200" -> Extrait "21:10"
        return f"{xml_date[8:10]}:{xml_date[10:12]}"
    except:
        return "00:00"

def main():
    print("1. Téléchargement du guide TV communautaire...")
    try:
        req = urllib.request.Request(XMLTV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        print(f"Téléchargement réussi : {len(xml_data)} octets reçus.")
    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        return

    print("2. Analyse de la structure XML...")
    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")
    print(f"Date recherchée : {aujourdhui}")

    try:
        root = ET.fromstring(xml_data)
        
        # Étape A : On crée la table de correspondance des chaînes
        dict_chaines = {}
        for channel in root.findall('channel'):
            chan_id = channel.get('id')
            disp = channel.find('display-name')
            if chan_id and disp is not None and disp.text:
                dict_chaines[chan_id] = disp.text.upper()

        print(f"Nombre de chaînes indexées : {len(dict_chaines)}")

        # Étape B : Extraction des programmes
        for prog in root.findall('programme'):
            start_time = prog.get('start')
            
            # On vérifie si le programme commence aujourd'hui
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
        print(f"Erreur d'analyse du XML : {e}")
        return

    # Tri par ordre chronologique
    programmes_filtres.sort(key=lambda x: x['heure'])
    
    # Sécurité ultime : si le fichier est vide, on crée une vraie ligne informative
    if not programmes_filtres:
        programmes_filtres.append({
            "heure": "08:00", 
            "chaine": "Aide Système", 
            "titre": "Aucun programme trouvé pour aujourd'hui dans le flux.", 
            "genre": "Autre", 
            "source": "TNT"
        })

    # Sauvegarde finale
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Réussite ! Fichier généré avec {len(programmes_filtres)} programmes.")

if __name__ == "__main__":
    main()
