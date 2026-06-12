import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Flux XMLTV complet, stable et autorisé pour le Cloud
XMLTV_URL = "https://github.com/thegoodb/fr/raw/main/spetnazfr.xml"

# Mapping étendu et actualisé selon la nouvelle grille TNT
# Format : 'Identifiant_XML': ('Canal', 'Nom de la chaîne', 'Source')
CHAINES_MAPPING = {
    # --- FREEBOX TV (TNT Nouvelle Génération) ---
    'TF1.fr': ('1', 'TF1', 'Freebox / Molotov'),
    'France2.fr': ('2', 'France 2', 'Freebox / Molotov'),
    'France3.fr': ('3', 'France 3', 'Freebox / Molotov'),
    'CanalPlus.fr': ('4', 'Canal+', 'Freebox / Molotov'),
    'France5.fr': ('5', 'France 5', 'Freebox / Molotov'),
    'M6.fr': ('6', 'M6', 'Freebox / Molotov'),
    'Arte.fr': ('7', 'Arte', 'Freebox / Molotov'),
    'C8.fr': ('8', 'C8', 'Freebox / Molotov'),
    'W9.fr': ('9', 'W9', 'Freebox / Molotov'),
    'TMC.fr': ('10', 'TMC', 'Freebox / Molotov'),
    'TFX.fr': ('11', 'TFX', 'Freebox / Molotov'),
    'TeleStarTV.fr': ('12', 'Télé Star TV', 'Freebox / Molotov'),
    'LCP.fr': ('13', 'LCP Public Sénat', 'Freebox / Molotov'),
    'France4.fr': ('14', 'France 4', 'Freebox / Molotov'),
    'BFMTV.fr': ('15', 'BFM TV', 'Freebox / Molotov'),
    'CNews.fr': ('16', 'CNews', 'Freebox / Molotov'),
    'CStar.fr': ('17', 'CStar', 'Freebox / Molotov'),
    'Gulli.fr': ('18', 'Gulli', 'Freebox / Molotov'),
    'TF1SeriesFilms.fr': ('19', 'TF1 Series Films', 'Freebox / Molotov'),
    'LEquipe.fr': ('20', "L'Equipe", 'Freebox / Molotov'),
    '6ter.fr': ('21', '6ter', 'Freebox / Molotov'),
    'RMCStory.fr': ('22', 'RMC Story', 'Freebox / Molotov'),
    'RMCDecouverte.fr': ('23', 'RMC Découverte', 'Freebox / Molotov'),
    'OuestFranceTV.fr': ('25', 'Ouest-France TV', 'Freebox / Molotov'),
    'LCI.fr': ('26', 'LCI', 'Freebox / Molotov'),
    'FranceInfo.fr': ('27', 'Franceinfo', 'Freebox / Molotov'),

    # --- EXTENSION FREEBOX TV & SÉRIES ---
    'ParisPremiere.fr': ('28', 'Paris Première', 'Freebox TV'),
    'RTL9.fr': ('29', 'RTL 9', 'Freebox TV'),
    'Teva.fr': ('53', 'Téva', 'Freebox TV'),
    'PolarPlus.fr': ('55', 'Polar+', 'Freebox TV'),
    'Breizh.fr': ('54', 'TV Breizh', 'Freebox TV'),
    'Action.fr': ('82', 'Action', 'Freebox TV'),
    'GameOne.fr': ('118', 'Game One', 'Freebox TV'),
    'Mangas.fr': ('121', 'Mangas', 'Freebox TV'),
    'Histoire.fr': ('205', 'Histoire TV', 'Freebox TV'),
    'TouteLaHistoire.fr': ('206', "Toute l'Histoire", 'Freebox TV'),
    'ScienceEtVie.fr': ('207', 'Science & Vie TV', 'Freebox TV'),
    'Ushuaia.fr': ('204', 'Ushuaïa TV', 'Freebox TV'),
    'TV5Monde.fr': ('357', 'TV5 Monde', 'Freebox TV'),

    # --- SAMSUNG TV PLUS ---
    'ComedyCentral.fr': ('4124', 'Comedy Central', 'Samsung TV Plus'),
    'PlutoTVCine.fr': ('4142', 'Pluto TV Ciné', 'Samsung TV Plus'),
    'RakutenTVAction.fr': ('4112', 'Rakuten TV Action', 'Samsung TV Plus'),
    'DoctorWho.fr': ('4304', 'Doctor Who TV', 'Samsung TV Plus'),
    'PlutoTVSeries.fr': ('4145', 'Pluto TV Séries', 'Samsung TV Plus'),
    'RakutenTVComedie.fr': ('4113', 'Rakuten TV Comédie', 'Samsung TV Plus'),
    'BFMTV_Samsung.fr': ('4001', 'BFM TV (Flux FAST)', 'Samsung TV Plus'),
    'WilderTV.fr': ('4135', 'Wilder TV', 'Samsung TV Plus'),
    'VevoPop.fr': ('4701', 'Vevo Pop', 'Samsung TV Plus')
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
        print("Téléchargement réussi.")
    except Exception as e:
        print(f"Erreur : {e}")
        return

    print("2. Analyse et filtrage...")
    programmes_filtres = []
    aujourdhui = datetime.now().strftime("%Y%m%d")

    try:
        root = ET.fromstring(xml_data)
        for prog in root.findall('programme'):
            start_time = prog.get('start')
            
            if start_time and start_time.startswith(aujourdhui):
                chan_id = prog.get('channel')
                
                if chan_id in CHAINES_MAPPING:
                    canal, nom_propre, source = CHAINES_MAPPING[chan_id]
                    
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

    except Exception as e:
        print(f"Erreur d'analyse XML : {e}")
        return

    # Tri chronologique
    programmes_filtres.sort(key=lambda x: x['heure'])
    
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Succès : {len(programmes_filtres)} programmes chargés.")

if __name__ == "__main__":
    main()
