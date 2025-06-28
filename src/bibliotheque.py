import csv
import os
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from exceptions import *
from collections import Counter




class Livre:
    """Représente un livre avec ses informations de base."""
    def __init__(self, isbn: str, titre: str, auteur: str, annee: int, genre: str, statut: str = "disponible"):
        self.isbn = isbn
        self.titre = titre
        self.auteur = auteur
        self.annee = annee
        self.genre = genre
        self.statut = statut

    def __str__(self):
        return f"{self.titre} ({self.auteur}, {self.annee}) - {self.genre}"


class Membre:
    """Représente un membre inscrit à la bibliothèque."""
    MAX_EMPRUNTS = 5

    def __init__(self, id: str, nom: str):
        self.id = id
        self.nom = nom
        self.livres_empruntes: List[str] = []


class Bibliotheque:
    """Classe principale de gestion des livres, membres et emprunts."""
    def __init__(self):
        self.livres: Dict[str, Livre] = {}
        self.membres: Dict[str, Membre] = {}
        self.charger_donnees()

    # === Chargement des données ===
    def charger_donnees(self):
        self._charger_livres()
        self._charger_membres()

    def _charger_livres(self):
        try:
            with open('data/livres.txt', 'r', encoding='utf-8') as f:
                for ligne in f:
                    data = ligne.strip().split(';')
                    if len(data) == 6:
                        isbn, titre, auteur, annee_str, genre, statut = data
                        isbn = isbn.strip()
                        titre = titre.strip()
                        auteur = auteur.strip()
                        annee_str = annee_str.strip()
                        genre = genre.strip()
                        statut = statut.strip()
                        annee = int(annee_str)

                        self.livres[isbn] = Livre(isbn, titre, auteur, annee, genre, statut)

        except FileNotFoundError:
            Path('data').mkdir(exist_ok=True)
            open('data/livres.txt', 'w').close()

    def _charger_membres(self):
        try:
            with open('data/membres.txt', 'r', encoding='utf-8') as f:
                for ligne in f:
                    data = ligne.strip().split(';')
                    if len(data) >= 2:
                        id_membre = data[0].strip()
                        nom = data[1].strip()
                        membre = Membre(id_membre, nom)

                        if len(data) > 2 and data[2]:
                            membre.livres_empruntes = [isbn.strip() for isbn in data[2].split(',')]

                        self.membres[membre.id] = membre

        except FileNotFoundError:
            open('data/membres.txt', 'w').close()

    def sauvegarder_donnees(self):
        with open('data/livres.txt', 'w', encoding='utf-8') as f:
            for livre in self.livres.values():
                f.write(f"{livre.isbn};{livre.titre};{livre.auteur};{livre.annee};{livre.genre};{livre.statut}\n")

        with open('data/membres.txt', 'w', encoding='utf-8') as f:
            for membre in self.membres.values():
                livres = ','.join(membre.livres_empruntes)
                f.write(f"{membre.id};{membre.nom};{livres}\n")

    def _enregistrer_historique(self, isbn: str, id_membre: str, action: str):
        """Ajoute une entrée dans le fichier historique.csv"""
        Path('data').mkdir(exist_ok=True)
        fichier = Path('data/historique.csv')
        fichier_existe = fichier.exists()

        with open(fichier, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ["date", "isbn", "id_membre", "action"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            if not fichier_existe:
                writer.writeheader()
            writer.writerow({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "isbn": isbn,
                "id_membre": id_membre,
                "action": action
            })

    # === Méthodes métier ===
    def ajouter_livre(self, livre: Livre):
        """Ajoute un livre à la bibliothèque."""
        if livre.isbn in self.livres:
            raise ValueError(f"Livre avec ISBN {livre.isbn} existe déjà")
        self.livres[livre.isbn] = livre

    def enregistrer_membre(self, membre: Membre):
        """Inscrit un nouveau membre."""
        if membre.id in self.membres:
            raise ValueError(f"Membre avec ID {membre.id} existe déjà")
        self.membres[membre.id] = membre

    def emprunter_livre(self, isbn: str, id_membre: str) -> None:
        isbn, id_membre = isbn.strip(), id_membre.strip()
    
        if isbn not in self.livres:
            raise LivreInexistantError(isbn)
        if id_membre not in self.membres:
            raise MembreInexistantError(id_membre)

        livre = self.livres[isbn]
        membre = self.membres[id_membre]

        if livre.statut.startswith("emprunté:"):
            raise LivreIndisponibleError(isbn)
        if len(membre.livres_empruntes) >= Membre.MAX_EMPRUNTS:
            raise QuotaEmpruntDepasseError(id_membre, Membre.MAX_EMPRUNTS)

    # OPÉRATION D'EMPRUNT
        livre.statut = f"emprunté:{id_membre}"
        membre.livres_empruntes.append(isbn)
        self._enregistrer_historique(isbn, id_membre, "emprunt")
        
    def _valider_isbn(self, isbn: str):
        """Validation basique d'ISBN"""
        isbn = isbn.strip()
        if not isbn or len(isbn) < 10:
            raise DonneesInvalidesError("ISBN", isbn, "ISBN invalide (10 caractères minimum)")
        return isbn


    def retourner_livre(self, isbn: str):
        """Alias de rendre_livre (compatibilité)"""
        self.rendre_livre(isbn)


    def rendre_livre(self, isbn: str):
        """Gère le retour d'un livre, lève exception si problème."""
        isbn = isbn.strip()

        if isbn not in self.livres:
            raise LivreInexistantError(f"Livre {isbn} introuvable")
    
        livre = self.livres[isbn]

        if not livre.statut.startswith("emprunté:"):
            raise LivreNonEmprunteError(f"Le livre '{livre.titre}' n'est pas emprunté actuellement")
    
        id_membre = livre.statut.split(":")[1]
        livre.statut = "disponible"
    
        if id_membre in self.membres:
            membre = self.membres[id_membre]
            if isbn in membre.livres_empruntes:
                membre.livres_empruntes.remove(isbn)
    
    # Historique
        self._enregistrer_historique(isbn, id_membre, "retour")


    def supprimer_membre(self, id_membre: str):
        """Supprime un membre après vérification et restitution de ses livres."""
        id_membre = id_membre.strip()

        if id_membre not in self.membres:
            raise MembreInexistantError(f"Membre {id_membre} introuvable")
    
        membre = self.membres[id_membre]

    # Retour automatique des livres empruntés
        for isbn in membre.livres_empruntes[:]:  # copie pour éviter les conflits
            self.rendre_livre(isbn)
    
    # Suppression
        del self.membres[id_membre]


    def supprimer_livre(self, isbn: str):
        """Supprime un livre après vérification qu'il n'est pas emprunté."""
        isbn = isbn.strip()

        if isbn not in self.livres:
            raise LivreInexistantError(f"Livre {isbn} introuvable")
    
        livre = self.livres[isbn]
        if livre.statut.startswith("emprunté:"):
            raise LivreIndisponibleError(f"Impossible de supprimer le livre {isbn} : il est emprunté")
    
    # Suppression
        del self.livres[isbn]


    def exporter_csv(self):
        """Exporte livres, membres et historique dans dossier export/"""
        os.makedirs("export", exist_ok=True)

        # Export livres
        with open("export/livres.csv", "w", newline='', encoding='utf-8') as f:
            fieldnames = ['isbn', 'titre', 'auteur', 'annee', 'genre', 'statut']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for livre in self.livres.values():
                writer.writerow({
                    'isbn': livre.isbn,
                    'titre': livre.titre,
                    'auteur': livre.auteur,
                    'annee': livre.annee,
                    'genre': livre.genre,
                    'statut': livre.statut
                })

        # Export membres
        with open("export/membres.csv", "w", newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'nom', 'livres_empruntes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for membre in self.membres.values():
                writer.writerow({
                    'id': membre.id,
                    'nom': membre.nom,
                    'livres_empruntes': ",".join(membre.livres_empruntes)
                })

        # Export historique (copie simple)
        historique_src = "data/historique.csv"
        historique_dst = "export/historique.csv"
        if os.path.exists(historique_src):
            with open(historique_src, "r", encoding='utf-8') as src, \
                 open(historique_dst, "w", encoding='utf-8') as dst:
                dst.write(src.read())



    def top_livres_empruntes(self, n=3):
        """Retourne une liste (livre, nb_emprunts) triée par nb emprunts décroissant"""
        compteur = Counter()
        historique_path = "data/historique.csv"
        
        if not os.path.exists(historique_path):
            return []
        
        with open(historique_path, "r", encoding='utf-8') as f:
            # On lit chaque ligne et compte les emprunts
            for line in f:
                parts = line.strip().split(";")
                if len(parts) >= 4:
                    action = parts[3].strip().lower()
                    isbn = parts[1].strip()
                    if action == "emprunt":
                        compteur[isbn] += 1
        
        livres_counts = []
        for isbn, count in compteur.most_common(n):
            livre = self.livres.get(isbn, None)
            if livre:
                livres_counts.append((livre, count))
        return livres_counts
    


    def top_membres_actifs(self, n=3):
        """Retourne une liste (membre, nb_emprunts) triée par nb emprunts décroissant"""
        compteur = Counter()
        historique_path = "data/historique.csv"
        
        if not os.path.exists(historique_path):
            return []
        
        with open(historique_path, "r", encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) >= 4:
                    action = parts[3].strip().lower()
                    id_membre = parts[2].strip()
                    if action == "emprunt":
                        compteur[id_membre] += 1
        
        membres_counts = []
        for id_membre, count in compteur.most_common(n):
            membre = self.membres.get(id_membre, None)
            if membre:
                membres_counts.append((membre, count))
        return membres_counts






