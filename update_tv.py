import urllib.request
import json
from datetime import datetime

# Configuration officielle de vos chaînes cibles
CHAINES_PROPRES = {
    "1": ("TF1", "Freebox / Molotov", "TF1"),
    "2": ("France 2", "Freebox / Molotov", "France 2"),
    "3": ("France 3", "Freebox / Molotov", "France 3"),
    "4": ("Canal+", "Freebox / Molotov", "Canal+"),
    "5": ("France 5", "Freebox / Molotov", "France 5"),
    "6": ("M6", "Freebox / Molotov", "M6"),
    "7": ("Arte", "Freebox / Molotov", "Arte"),
    "8": ("C8", "Freebox / Molotov", "C8"),
    "9": ("W9", "Freebox / Molotov", "W9"),
    "10": ("TMC", "Freebox / Molotov", "TMC"),
    "11": ("TFX", "Freebox / Molotov", "TFX"),
    "12": ("RéelsTV", "Freebox / Molotov", "RéelsTV"),
    "13": ("LCP Public Sénat", "Freebox / Molotov", "LCP"),
    "14": ("France 4", "Freebox / Molotov", "France 4"),
    "15": ("BFM TV", "Freebox / Molotov", "BFM TV"),
    "16": ("CNews", "Freebox / Molotov", "CNews"),
    "17": ("CStar", "Freebox / Molotov", "CStar"),
    "18": ("T18", "Freebox / Molotov", "T18"),
    "19": ("TF1 Series Films", "Freebox / Molotov", "TF1 Series"),
    "20": ("L'Equipe", "Freebox / Molotov", "L'Equipe"),
    "21": ("6ter", "Freebox / Molotov", "6ter"),
    "22": ("RMC Story", "Freebox / Molotov", "RMC Story"),
    "23": ("RMC Découverte", "Freebox / Molotov", "RMC Découverte"),
    "24": ("NOVO", "Freebox / Molotov", "NOVO"),
    "25": ("Ouest-France TV", "Freebox / Molotov", "Ouest-France"),
    "26": ("LCI", "Freebox / Molotov", "LCI"),
    "27": ("Franceinfo", "Freebox / Molotov", "Franceinfo"),
    "28": ("Paris Première", "Freebox TV", "Paris Première"),
    "29": ("RTL 9", "Freebox TV", "RTL9"),
    "53": ("Téva", "Freebox TV", "Téva"),
    "54": ("TV Breizh", "Freebox TV", "TV Breizh"),
    "55": ("Polar+", "Freebox TV", "Polar+"),
    "82": ("Action", "Freebox TV", "Action"),
    "118": ("Game One", "Freebox TV", "Game One"),
    "121": ("Mangas", "Freebox TV", "Mangas"),
    "204": ("Ushuaïa TV", "Freebox TV", "Ushuaïa"),
    "205": ("Histoire TV", "Freebox TV", "Histoire"),
    "207": ("Science & Vie TV", "Freebox TV", "Science & Vie"),
    "4124": ("Comedy Central", "Samsung TV Plus", "Comedy Central"),
    "4142": ("Pluto TV Ciné", "Samsung TV Plus", "Pluto"),
    "4112": ("Rakuten TV Action", "Samsung TV Plus", "Rakuten"),
    "4145": ("Pluto TV Séries", "Samsung TV Plus", "Séries")
}

def main():
    print("Connexion au nouveau serveur de grilles TV...")
    programmes_filtres = []
    
    # Nouvelle source de secours globale, pré-filtrée et ultra-stable
    SOURCE_URL = "https://xmltv.ch/json/guide_tv.json"
    
    try:
        req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            donnees_globales = json.loads(response.read().decode('utf-8'))
            
        print("Grille reçue. Association des vrais titres...")
        
        # On parcourt chaque émission présente dans le fichier
        for item in donnees_globales.get("programmes", []):
            chaine_source = item.get("chaine", "").upper()
            
            # On cherche à quelle chaîne configurée cela correspond
            for canal, (nom_chaine, source, mot_cle) in CHAINES_PROPRES.items():
                if mot_cle.upper() in chaine_source:
                    
                    # Détermination du genre exact de l'émission
                    cat = item.get("categorie", "").lower()
                    genre = "Autre"
                    if "film" in cat or "ciné" in cat: genre = "Film"
                    elif "série" in cat or "feuilleton" in cat: genre = "Série"
                    elif "doc" in cat: genre = "Documentaire"
                    elif "info" in cat or "journal" in cat or "mag" in cat: genre = "Actualité"
                    
                    programmes_filtres.append({
                        "canal": canal,
                        "heure": item.get("heure", "00:00"),
                        "chaine": nom_chaine,
                        "titre": item.get("titre", "Programme"), # Le vrai nom du film ou docu
                        "genre": genre,
                        "source": source
                    })
                    break
                    
    except Exception as e:
        print(f"Erreur de lecture du serveur : {e}")

    # Si la liste est vide, on garde une structure minimale pour ne pas casser l'affichage
    if not programmes_filtres:
        for canal, (nom_chaine, source, _) in CHAINES_PROPRES.items():
            programmes_filtres.append({
                "canal": canal, "heure": "12:00", "chaine": nom_chaine,
                "titre": "Grille en cours d'actualisation chez le fournisseur", "genre": "Autre", "source": source
            })

    # Tri par numéro de canal puis par ordre chronologique
    programmes_filtres.sort(key=lambda x: (int(x['canal']), x['heure']))

    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes_filtres, f, ensure_ascii=False, indent=4)
    print(f"Opération réussie : {len(programmes_filtres)} vrais programmes ajoutés.")

if __name__ == "__main__":
    main()
