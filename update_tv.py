import json

def main():
    print("Génération de la grille de programmes fixe...")
    
    # Création d'une vraie grille complète de programmes pour tester l'interface
    programmes = [
        # MATIN
        {"heure": "06:30", "chaine": "TF1", "titre": "Téléshopping", "genre": "Autre", "source": "TNT"},
        {"heure": "06:30", "chaine": "France 2", "titre": "Télématin", "genre": "Actualité", "source": "TNT"},
        {"heure": "08:30", "chaine": "M6", "titre": "M6 Boutique", "genre": "Autre", "source": "TNT"},
        {"heure": "09:50", "chaine": "France 5", "titre": "La maison France 5", "genre": "Documentaire", "source": "TNT"},
        
        # APRÈS-MIDI
        {"heure": "13:00", "chaine": "TF1", "titre": "Journal de 13h", "genre": "Actualité", "source": "TNT"},
        {"heure": "13:00", "chaine": "France 2", "titre": "Journal de 13h", "genre": "Actualité", "source": "TNT"},
        {"heure": "13:45", "chaine": "Arte", "titre": "Mystères d'archives", "genre": "Documentaire", "source": "TNT"},
        {"heure": "14:00", "chaine": "Comedy Central", "titre": "The Daily Show", "genre": "Série", "source": "Samsung TV Plus"},
        {"heure": "17:30", "chaine": "France 5", "titre": "C dans l'air", "genre": "Actualité", "source": "TNT"},
        {"heure": "19:10", "chaine": "M6", "titre": "Le 19.45", "genre": "Actualité", "source": "TNT"},
        
        # SOIRÉE (Prime Time)
        {"heure": "21:10", "chaine": "TF1", "titre": "Grand Film du Vendredi", "genre": "Film", "source": "TNT"},
        {"heure": "21:10", "chaine": "France 2", "titre": "Série Policière", "genre": "Série", "source": "TNT"},
        {"heure": "21:10", "chaine": "France 3", "titre": "Faut pas rêver", "genre": "Documentaire", "source": "TNT"},
        {"heure": "21:10", "chaine": "M6", "titre": "Recherche appartement ou maison", "genre": "Autre", "source": "TNT"},
        {"heure": "21:15", "chaine": "Arte", "titre": "Cinéma d'auteur", "genre": "Film", "source": "TNT"},
        {"heure": "21:15", "chaine": "W9", "titre": "Enquête d'action", "genre": "Documentaire", "source": "TNT"},
        {"heure": "21:15", "chaine": "TMC", "titre": "90' Enquêtes", "genre": "Documentaire", "source": "TNT"},
        
        # CHAÎNES SAMESUNG TV PLUS (Soirée)
        {"heure": "21:00", "chaine": "Comedy Central", "titre": "Friends - Marathon de la soirée", "genre": "Série", "source": "Samsung TV Plus"},
        {"heure": "21:00", "chaine": "Rakuten TV Action", "titre": "Dernier train pour Busan", "genre": "Film", "source": "Samsung TV Plus"},
        {"heure": "21:30", "chaine": "Pluto TV Ciné", "titre": "Le Parrain", "genre": "Film", "source": "Samsung TV Plus"},
        
        # DEUXIÈME PARTIE DE SOIRÉE
        {"heure": "22:45", "chaine": "TF1", "titre": "Vendredi, tout est permis", "genre": "Autre", "source": "TNT"},
        {"heure": "23:00", "chaine": "France 2", "titre": "Taratata 100% Live", "genre": "Autre", "source": "TNT"},
        {"heure": "23:20", "chaine": "Arte", "titre": "Court-circuit", "genre": "Film", "source": "TNT"}
    ]

    # Écriture immédiate du fichier JSON pour l'interface web
    with open("programmes.json", "w", encoding="utf-8") as f:
        json.dump(programmes, f, ensure_ascii=False, indent=4)
        
    print(f"Succès ! {len(programmes)} programmes injectés en local.")

if __name__ == "__main__":
    main()
