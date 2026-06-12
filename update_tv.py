import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Flux XMLTV officiel Télérama hébergé sur GitHub (Autorisé à 100% par l'automate)
XMLTV_URL = "https://raw.githubusercontent.com/Polyedre/xmltv-france/master/tvguide.xml"

# Correspondance des identifiants techniques Télérama pour vos chaînes préférées
CHAINES_MAPPING = {
    # TNT France
    'C192.api.telerama.fr': ('TF1', 'TNT'),
    'C4.api.telerama.fr': ('France 2', 'TNT'),
    'C80.api.telerama.fr': ('France 3', 'TNT'),
    'C34.api.telerama.fr': ('Canal+', 'TNT'),
    'C47.api.telerama.fr': ('France 5', 'TNT'),
    'C118.api.telerama.fr': ('M6', 'TNT'),
    'C111.api.telerama.fr': ('Arte', 'TNT'),
    'C445.api.telerama.fr': ('C8', 'TNT'),
    'C119.api.telerama.fr': ('W9', 'TNT'),
    'C195.api.telerama.fr': ('TMC', 'TNT'),
    'C446.api.telerama.fr': ('TFX', 'TNT'),
    'C444.api.telerama.fr': ('NRJ 12', 'TNT'),
    'C78.api.telerama.fr': ('France 4', 'TNT'),
    'C481.api.telerama.fr': ('BFM TV', 'TNT'),
    'C226.api.telerama.fr': ('CNews', 'TNT'),
    'C458.api.telerama.fr': ('CStar', 'TNT'),
    'C482.api.telerama.fr': ('Gulli', 'TNT'),
    'C1404.api.telerama.fr': ('TF1 Series', 'TNT'),
    'C1401.api.telerama.fr': ("L'Equipe", 'TNT'),
    'C1403.api.telerama.fr': ('6ter', 'TNT'),
    'C1400.api.telerama.fr': ('RMC Découverte', 'TNT'),
    'C1399.api.telerama.fr': ('Chérie 25', 'TNT'),
    'C1073.api.telerama.fr': ('LCI', 'TNT'),
    'C2052.api.telerama.fr': ('Franceinfo', 'TNT'),
    
    # Samsung TV Plus / FAST thématiques courantes
    'C1964.api.telerama.fr': ('Comedy Central', 'Samsung TV Plus'),
    'C2243.api.telerama.fr': ('Pluto TV Ciné', 'Samsung TV Plus'),
    'C2112.api.telerama.fr': ('Rakuten TV Action', 'Samsung TV Plus')
}

def convertir_heure(xml_date):
    try:
        return f"{xml_date[8:10]}:{xml_date[10:12]}"
    except:
        return "00:00"

def main():
    print("1. Téléchargement du fichier XMLTV depuis GitHub...")
    try:
        req = urllib.request.Request(XMLTV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        print(f"Téléchargement réussi : {len(xml_data)} octets reçus.")
    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        sauvegarder_secours(f"Erreur de téléchargement : {e}")
        return

    print("2. Analyse et filtrage des programmes...")
    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")

    try:
        root = ET.fromstring(xml_data)
        
        for prog in root.findall('programme'):
            start_time = prog.get('start')
            
            # Filtrage sur la date du jour
            if start_time and start_time.startswith(aujourdhui):
                chan_id = prog.get('channel')
                
                # Si la chaîne fait partie de notre liste ciblée
                if chan_id in CHAINES_MAPPING:
                    nom_propre, source = CHAINES_MAPPING[chan_id]
                    
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
                        "chaine": nom_propre,
                        "titre": titre,
                        "genre": genre,
                        "source": source
                    })

    except Exception as e:
        print(f"Erreur d'analyse : {e}")
        sauvegarder_secours(f"Erreur technique d'analyse XML : {e}")
        return

    # Tri par heure
    programmes_filtres.sort(key=lambda x: x['heure'])
    
    if not programmes_filtres:
        sauvegarder_secours(f"Aucun programme trouvé dans la base Télérama pour la date du {aujourdhui}.")
        return

    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Extraction réussie : {len(programmes_filtres)} programmes sauvegardés.")

def sauvegarder_secours(message):
    secours = [{"heure": "00:00", "chaine": "Avis Système", "titre": message, "genre": "Autre", "source": "TNT"}]
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(secours, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
