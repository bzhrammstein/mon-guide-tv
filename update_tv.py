import urllib.request
import json
from datetime import datetime

# Configuration de votre grille personnelle
CHAINES_PROPRES = {
    "1": ("TF1", "Freebox / Molotov", "tf1"),
    "2": ("France 2", "Freebox / Molotov", "france2"),
    "3": ("France 3", "Freebox / Molotov", "france3"),
    "4": ("Canal+", "Freebox / Molotov", "canalplus"),
    "5": ("France 5", "Freebox / Molotov", "france5"),
    "6": ("M6", "Freebox / Molotov", "m6"),
    "7": ("Arte", "Freebox / Molotov", "arte"),
    "8": ("C8", "Freebox / Molotov", "c8"),
    "9": ("W9", "Freebox / Molotov", "w9"),
    "10": ("TMC", "Freebox / Molotov", "tmc"),
    "11": ("TFX", "Freebox / Molotov", "tfx"),
    "12": ("RéelsTV", "Freebox / Molotov", "reelstv"),
    "13": ("LCP Public Sénat", "Freebox / Molotov", "lcp"),
    "14": ("France 4", "Freebox / Molotov", "france4"),
    "15": ("BFM TV", "Freebox / Molotov", "bfmtv"),
    "16": ("CNews", "Freebox / Molotov", "cnews"),
    "17": ("CStar", "Freebox / Molotov", "cstar"),
    "18": ("T18", "Freebox / Molotov", "t18"),
    "19": ("TF1 Series Films", "Freebox / Molotov", "tf1series"),
    "20": ("L'Equipe", "Freebox / Molotov", "lequipe"),
    "21": ("6ter", "Freebox / Molotov", "6ter"),
    "22": ("RMC Story", "Freebox / Molotov", "rmcstory"),
    "23": ("RMC Découverte", "Freebox / Molotov", "rmcdecouverte"),
    "24": ("NOVO", "Freebox / Molotov", "novo"),
    "25": ("Ouest-France TV", "Freebox / Molotov", "ouestfrance"),
    "26": ("LCI", "Freebox / Molotov", "lci"),
    "27": ("Franceinfo", "Freebox / Molotov", "franceinfo"),
    "28": ("Paris Première", "Freebox TV", "parispremiere"),
    "29": ("RTL 9", "Freebox TV", "rtl9"),
    "53": ("Téva", "Freebox TV", "teva"),
    "54": ("TV Breizh", "Freebox TV", "tvbreizh"),
    "55": ("Polar+", "Freebox TV", "polarplus"),
    "82": ("Action", "Freebox TV", "action"),
    "118": ("Game One", "Freebox TV", "gameone"),
    "121": ("Mangas", "Freebox TV", "mangas"),
    "204": ("Ushuaïa TV", "Freebox TV", "ushuaia"),
    "205": ("Histoire TV", "Freebox TV", "histoire"),
    "207": ("Science & Vie TV", "Freebox TV", "sciencevie"),
    "4124": ("Comedy Central", "Samsung TV Plus", "comedycentral"),
    "4142": ("Pluto TV Ciné", "Samsung TV Plus", "plutocine"),
    "4112": ("Rakuten TV Action", "Samsung TV Plus", "rakuten"),
    "4145": ("Pluto TV Séries", "Samsung TV Plus", "plutoseries")
}

def main():
    print("Connexion au serveur de programmes national...")
    programmes_filtres = []
    
    # API ouverte, stable et mise à jour en continu pour la TNT et le câble
    API_URL = "https://raw.githubusercontent.com/orish9/tv-grille/main/grille.json"
    
    try:
        req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as response:
            donnees = json.loads(response.read().decode('utf-8'))
            
        print("Données reçues. Analyse des grilles de la journée...")
        
        # Parcours des chaînes de l'API
        for chaine_api, emissions in donnees.items():
            chaine_api_clean = chaine_api.lower().replace(" ", "").replace("+", "plus")
            
            for canal, (nom_chaine, source, code_identifiant) in CHAINES_PROPRES.items():
                if code_identifiant in chaine_api_clean or chaine_api_clean in code_identifiant:
                    
                    for emi in emissions:
                        titre = emi.get("title", "Programme")
                        heure = emi.get("start", "00:00")
                        cat = emi.get("category", "Autre").lower()
                        
                        genre = "Autre"
                        if any(x in cat for x in ["film", "ciné", "téléfilm"]): genre = "Film"
                        elif any(x in cat for x in ["série", "feuilleton"]): genre = "Série"
                        elif "doc" in cat: genre = "Documentaire"
                        elif any(x in cat for x in ["info", "journal", "mag", "actualité", "météo"]): genre = "Actualité"
                        
                        programmes_filtres.append({
                            "canal": canal,
                            "heure": heure,
                            "chaine": nom_propre, # Utilisation du nom propre défini
                            "titre": titre,
                            "genre": genre,
                            "source": source
                        })
                    break
                    
    except Exception as e:
        print(f"Erreur technique lors du chargement : {e}")

    # Si l'API est en cours de mise à jour, on affiche une vraie indication claire
    if not programmes_filtres:
        print("Bascule sur l'affichage d'attente.")
        for canal, (nom_chaine, source, _) in CHAINES_PROPRES.items():
            programmes_filtres.append({
                "canal": canal, "heure": "00:00", "chaine": nom_chaine,
                "titre": "Synchronisation de la grille en cours... Cliquez sur Forcer la mise à jour dans quelques instants.", 
                "genre": "Autre", "source": source
            })

    # Tri par numéro de canal croissant, puis chronologiquement
    programmes_filtres.sort(key=lambda x: (int(x['canal']), x['heure']))

    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Mise à jour terminée : {len(programmes_filtres)} programmes extraits.")

if __name__ == "__main__":
    main()
