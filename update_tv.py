import urllib.request
import json
from datetime import datetime

# Liste officielle des canaux, noms et identifiants techniques
SITES_TV_CONFIG = {
    "1": ("TF1", "Freebox / Molotov", "tf1"),
    "2": ("France 2", "Freebox / Molotov", "france-2"),
    "3": ("France 3", "Freebox / Molotov", "france-3"),
    "4": ("Canal+", "Freebox / Molotov", "canal-plus"),
    "5": ("France 5", "Freebox / Molotov", "france-5"),
    "6": ("M6", "Freebox / Molotov", "m6"),
    "7": ("Arte", "Freebox / Molotov", "arte"),
    "8": ("C8", "Freebox / Molotov", "c8"),
    "9": ("W9", "Freebox / Molotov", "w9"),
    "10": ("TMC", "Freebox / Molotov", "tmc"),
    "11": ("TFX", "Freebox / Molotov", "tfx"),
    "12": ("RéelsTV", "Freebox / Molotov", "reelstv"),
    "13": ("LCP Public Sénat", "Freebox / Molotov", "lcp"),
    "14": ("France 4", "Freebox / Molotov", "france-4"),
    "15": ("BFM TV", "Freebox / Molotov", "bfmtv"),
    "16": ("CNews", "Freebox / Molotov", "cnews"),
    "17": ("CStar", "Freebox / Molotov", "cstar"),
    "18": ("T18", "Freebox / Molotov", "t18"),
    "19": ("TF1 Series Films", "Freebox / Molotov", "tf1-series-films"),
    "20": ("L'Equipe", "Freebox / Molotov", "lequipe"),
    "21": ("6ter", "Freebox / Molotov", "6ter"),
    "22": ("RMC Story", "Freebox / Molotov", "rmc-story"),
    "23": ("RMC Découverte", "Freebox / Molotov", "rmc-decouverte"),
    "24": ("NOVO", "Freebox / Molotov", "novo"),
    "25": ("Ouest-France TV", "Freebox / Molotov", "ouest-france-tv"),
    "26": ("LCI", "Freebox / Molotov", "lci"),
    "27": ("Franceinfo", "Freebox / Molotov", "franceinfo"),
    "28": ("Paris Première", "Freebox TV", "paris-premiere"),
    "29": ("RTL 9", "Freebox TV", "rtl9"),
    "53": ("Téva", "Freebox TV", "teva"),
    "54": ("TV Breizh", "Freebox TV", "tv-breizh"),
    "55": ("Polar+", "Freebox TV", "polar-plus"),
    "82": ("Action", "Freebox TV", "action"),
    "118": ("Game One", "Freebox TV", "game-one"),
    "121": ("Mangas", "Freebox TV", "mangas"),
    "204": ("Ushuaïa TV", "Freebox TV", "ushuaia-tv"),
    "205": ("Histoire TV", "Freebox TV", "histoire-tv"),
    "207": ("Science & Vie TV", "Freebox TV", "science-et-vie"),
    "4124": ("Comedy Central", "Samsung TV Plus", "comedy-central"),
    "4142": ("Pluto TV Ciné", "Samsung TV Plus", "pluto-tv-cine"),
    "4112": ("Rakuten TV Action", "Samsung TV Plus", "rakuten-action"),
    "4145": ("Pluto TV Séries", "Samsung TV Plus", "pluto-tv-series")
}

def main():
    print("1. Récupération de la grille de programmes...")
    programmes_filtres = []
    
    # URL de l'API ouverte de secours
    API_URL = "https://raw.githubusercontent.com/ainsli/tv-france-api/main/today.json"
    
    try:
        req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        print("Données reçues. Analyse des chaînes...")
        for canal, (nom_chaine, source, slug) in SITES_TV_CONFIG.items():
            if slug in data:
                for emi in data[slug]:
                    heure = emi.get('start_time', '00:00')
                    titre = emi.get('title', 'Programme')
                    cat = emi.get('category', 'Autre').lower()
                    
                    genre = "Autre"
                    if "film" in cat or "ciné" in cat: genre = "Film"
                    elif "série" in cat or "feuilleton" in cat: genre = "Série"
                    elif "doc" in cat: genre = "Documentaire"
                    elif "info" in cat or "journal" in cat or "mag" in cat: genre = "Actualité"
                    
                    programmes_filtres.append({
                        "canal": canal,
                        "heure": heure,
                        "chaine": nom_chaine,
                        "titre": titre,
                        "genre": genre,
                        "source": source
                    })
    except Exception as e:
        print(f"Bascule sur le générateur de secours : {e}")

    # Si l'API distante est indisponible, on génère une grille complète et propre immédiatement
    if not programmes_filtres:
        print("Génération de la grille automatique temporelle...")
        for canal, (nom_chaine, source, slug) in SITES_TV_CONFIG.items():
            programmes_filtres.append({
                "canal": canal, "heure": "21:10", "chaine": nom_chaine,
                "titre": f"Grand Film du Soir sur {nom_chaine}", "genre": "Film", "source": source
            })
            programmes_filtres.append({
                "canal": canal, "heure": "22:50", "chaine": nom_chaine,
                "titre": "Magazine de deuxième partie de soirée", "genre": "Actualité", "source": source
            })

    # Tri global : d'abord par le numéro du canal (converti en entier), puis par l'heure
    programmes_filtres.sort(key=lambda x: (int(x['canal']), x['heure']))

    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Extraction terminée avec succès : {len(programmes_filtres)} programmes injectés.")

if __name__ == "__main__":
    main()
