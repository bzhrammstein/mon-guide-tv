import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Source internationale haut de gamme, conçue pour supporter les requêtes Cloud Actions
XMLTV_URL = "https://iptv-org.github.io/epg/guides/fr/telerama.fr.xml"

# Mapping exact pour cette source (Codes Télérama officiels)
CHAINES_MAPPING = {
    'TF1.fr': ('TF1', 'TNT'),
    'France2.fr': ('France 2', 'TNT'),
    'France3.fr': ('France 3', 'TNT'),
    'CanalPlus.fr': ('Canal+', 'TNT'),
    'France5.fr': ('France 5', 'TNT'),
    'M6.fr': ('M6', 'TNT'),
    'Arte.fr': ('Arte', 'TNT'),
    'C8.fr': ('C8', 'TNT'),
    'W9.fr': ('W9', 'TNT'),
    'TMC.fr': ('TMC', 'TNT'),
    'TFX.fr': ('TFX', 'TNT'),
    'NRJ12.fr': ('NRJ 12', 'TNT'),
    'LCPPublicSenat.fr': ('LCP', 'TNT'),
    'France4.fr': ('France 4', 'TNT'),
    'BFMTV.fr': ('BFM TV', 'TNT'),
    'CNews.fr': ('CNews', 'TNT'),
    'CStar.fr': ('CStar', 'TNT'),
    'Gulli.fr': ('Gulli', 'TNT'),
    'TF1SeriesFilms.fr': ('TF1 Series', 'TNT'),
    'LEquipe.fr': ("L'Equipe", 'TNT'),
    '6ter.fr': ('6ter', 'TNT'),
    'RMCDecouverte.fr': ('RMC Découverte', 'TNT'),
    'Cherie25.fr': ('Chérie 25', 'TNT'),
    'LCI.fr': ('LCI', 'TNT'),
    'FranceInfo.fr': ('Franceinfo', 'TNT')
}

def convertir_heure(xml_date):
    try:
        # Format : "20260612060000 +0200" -> "06:00"
        return f"{xml_date[8:10]}:{xml_date[10:12]}"
    except:
        return "00:00"

def main():
    print("1. Téléchargement du fichier XMLTV mondial...")
    try:
        # Ajout d'une fausse identité de navigateur pour éliminer les dernières sécurités
        req = urllib.request.Request(XMLTV_URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        print(f"Réussite : {len(xml_data)} octets reçus.")
    except Exception as e:
        print(f"Erreur : {e}")
        sauvegarder_secours(f"Erreur de connexion au serveur mondial : {e}")
        return

    print("2. Analyse de la grille TV...")
    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")

    try:
        root = ET.fromstring(xml_data)
        
        for prog in root.findall('programme'):
            start_time = prog.get('start')
            
            # On prend les programmes du jour
            if start_time and start_time.startswith(aujourdhui):
                chan_id = prog.get('channel')
                
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

    # Tri par heure de diffusion
    programmes_filtres.sort(key=lambda x: x['heure'])
    
    if not programmes_filtres:
        sauvegarder_secours(f"Aucun programme trouvé dans la base pour la date du {aujourdhui}.")
        return

    # Écriture définitive du fichier attendu par la page web
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Extraction terminée avec succès. {len(programmes_filtres)} programmes ajoutés.")

def sauvegarder_secours(message):
    secours = [{"heure": "00:00", "chaine": "Avis Système", "titre": message, "genre": "Autre", "source": "TNT"}]
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(secours, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
