import cmd
from bibliotheque import Bibliotheque,Livre, Membre
from exceptions import *
from visualisations import Visualisation
import sys

class BibliothequeCLI(cmd.Cmd):
    """Interface en ligne de commande pour le système de gestion de bibliothèque"""
    
    prompt = "\n📚 Bibliothèque > "
    intro = """
=== Système de Gestion de Bibliothèque ===
Tapez 'aide' pour la liste des commandes
Tapez 'menu' pour afficher le menu principal
"""

    def __init__(self):
        super().__init__()
        self.biblio = Bibliotheque()
        self.charger_donnees()
        
    def charger_donnees(self):
        """Charge les données au démarrage"""
        try:
            self.biblio.charger_donnees()
            print("\n✅ Données chargées avec succès")
        except Exception as e:
            print(f"\n❌ Erreur lors du chargement: {e}")

    def do_menu(self, arg):
        """Affiche le menu principal"""
        print("""
=== MENU PRINCIPAL ===
1.  Ajouter un livre
2.  Inscrire un membre
3.  Emprunter un livre
4.  Rendre un livre
5.  Lister les livres
6.  Lister les membres
7.  Rechercher un livre
8.  Voir les emprunts
9.  Statistiques
10. Sauvegarder & quitter

Tapez directement la commande (ex: 'ajouter_livre')
ou le numéro du menu (ex: '1')
""")

    # ===== Commandes de gestion =====
    def do_ajouter_livre(self, arg):
        """Ajoute un nouveau livre à la bibliothèque"""
        try:
            print("\n=== NOUVEAU LIVRE ===")
            isbn = input("ISBN: ").strip()
            titre = input("Titre: ").strip()
            auteur = input("Auteur: ").strip()
            annee = int(input("Année: ").strip())
            genre = input("Genre: ").strip()
            
            livre = Livre(isbn, titre, auteur, annee, genre)
            self.biblio.ajouter_livre(livre)
            print(f"\n✅ Livre '{titre}' ajouté avec succès")
            
        except ValueError as e:
            print(f"\n❌ Erreur de saisie: {e}")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

    def do_inscrire_membre(self, arg):
        """Inscrit un nouveau membre"""
        try:
            print("\n=== NOUVEAU MEMBRE ===")
            id_membre = input("ID membre: ").strip()
            nom = input("Nom complet: ").strip()
            
            membre = Membre(id_membre, nom)
            self.biblio.enregistrer_membre(membre)
            print(f"\n✅ Membre '{nom}' inscrit avec succès")
            
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

    # ===== Commandes d'emprunt =====
    def do_emprunter(self, arg):
        """Enregistre un emprunt de livre"""
        try:
            print("\n=== EMPRUNT ===")
            isbn = input("ISBN du livre: ").strip()
            id_membre = input("ID du membre: ").strip()
            
            self.biblio.emprunter_livre(isbn, id_membre)
            livre = self.biblio.livres[isbn]
            membre = self.biblio.membres[id_membre]
            
            print(f"\n✅ '{livre.titre}' emprunté par {membre.nom}")
            
        except (LivreIndisponibleError, QuotaEmpruntDepasseError, 
                MembreInexistantError, LivreInexistantError) as e:
            print(f"\n❌ {e}")
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")

    def do_rendre(self, arg):
        """Enregistre le retour d'un livre"""
        try:
            print("\n=== RETOUR ===")
            isbn = input("ISBN du livre: ").strip()
            # Délégation à la méthode métier, gère erreurs et états
            self.biblio.rendre_livre(isbn)
            livre = self.biblio.livres.get(isbn, None)
            titre = livre.titre if livre else isbn
            print(f"\n✅ '{titre}' a été retourné")
            
        except LivreInexistantError as e:
            print(f"\n❌ {e}")
        except LivreNonEmprunteError as e:
            print(f"\n⚠ {e}")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

    # ===== Commandes de consultation =====
    def do_lister_livres(self, arg):
        """Affiche la liste complète des livres"""
        print("\n=== LIVRES DISPONIBLES ===")
        if not self.biblio.livres:
            print("Aucun livre enregistré")
            return
            
        for livre in self.biblio.livres.values():
            statut = "Disponible" if livre.statut == "disponible" else f"Emprunté ({livre.statut.split(':')[1]})"
            print(f"\n📖 {livre.titre} ({livre.auteur}, {livre.annee})")
            print(f"   ISBN: {livre.isbn} | Genre: {livre.genre} | Statut: {statut}")

    def do_lister_membres(self, arg):
        """Affiche la liste des membres"""
        print("\n=== MEMBRES INSCRITS ===")
        if not self.biblio.membres:
            print("Aucun membre inscrit")
            return
            
        for membre in self.biblio.membres.values():
            print(f"\n👤 {membre.nom} (ID: {membre.id})")
            print(f"   Livres empruntés: {len(membre.livres_empruntes)}/{Membre.MAX_EMPRUNTS}")
            if membre.livres_empruntes:
                print("   Titres empruntés:")
                for isbn in membre.livres_empruntes:
                    if isbn in self.biblio.livres:
                        print(f"    - {self.biblio.livres[isbn].titre}")

    def do_rechercher(self, arg):
        """Recherche un livre par titre, auteur ou genre"""
        terme = arg.strip().lower()
        if not terme:
            terme = input("\nEntrez un terme de recherche: ").lower().strip()
        if not terme:
            print("Veuillez entrer un terme de recherche")
            return
            
        resultats = [
            livre for livre in self.biblio.livres.values()
            if (terme in livre.titre.lower() or 
                terme in livre.auteur.lower() or 
                terme in livre.genre.lower())
        ]
        
        print(f"\n🔍 {len(resultats)} résultat(s) trouvé(s):")
        for livre in resultats:
            print(f"\n- {livre.titre} ({livre.auteur}) | {livre.genre} | ISBN: {livre.isbn}")

    # ===== Commandes statistiques =====
    def do_statistiques(self, arg):
        """Affiche les statistiques de la bibliothèque"""
        print("\n=== STATISTIQUES ===")
        print(f"📚 Nombre total de livres: {len(self.biblio.livres)}")
        print(f"👥 Nombre de membres: {len(self.biblio.membres)}")
        
        emprunts = sum(1 for l in self.biblio.livres.values() if l.statut != "disponible")
        print(f"🔁 Emprunts actifs: {emprunts}")
        
        # Top 3 livres les plus empruntés
        top_livres = self.biblio.top_livres_empruntes(3)
        if top_livres:
            print("\n🏆 Top 3 des livres les plus empruntés :")
            for livre, count in top_livres:
                print(f" - {livre.titre} ({count} emprunts)")

        # Top 3 membres les plus actifs
        top_membres = self.biblio.top_membres_actifs(3)
        if top_membres:
            print("\n🎖️ Top 3 des membres les plus actifs :")
            for membre, count in top_membres:
                print(f" - {membre.nom} ({count} emprunts)")

        # Génération des graphiques
        try:
            print("\n📊 Génération des graphiques...")
            Visualisation.generer_tous_graphiques(
                livres=list(self.biblio.livres.values()),
                historique_path="data/historique.csv"
            )
            print("✅ Graphiques générés dans le dossier 'assets'")
        except Exception as e:
            print(f"❌ Erreur lors de la génération: {e}")

    # ===== Commandes système =====
    def do_sauvegarder(self, arg):
        """Sauvegarde les données actuelles"""
        try:
            self.biblio.sauvegarder_donnees()
            print("\n✅ Données sauvegardées avec succès")
        except Exception as e:
            print(f"\n❌ Erreur lors de la sauvegarde: {e}")

    def do_quitter(self, arg):
        """Quitte l'application après sauvegarde"""
        self.do_sauvegarder(None)
        print("\nMerci d'avoir utilisé notre système. Au revoir !")
        return True

    # ===== Commandes de suppression avec confirmation =====
    def do_supprimer_membre(self, arg):
        """Supprime un membre (avec confirmation)"""
        id_membre = arg.strip()
        if not id_membre:
            id_membre = input("ID du membre à supprimer : ").strip()
        if id_membre not in self.biblio.membres:
            print(f"\n❌ Membre {id_membre} introuvable")
            return
        confirm = input(f"Confirmez la suppression du membre {id_membre} (o/N) ? ").lower()
        if confirm == 'o':
            try:
                self.biblio.supprimer_membre(id_membre)
                print(f"\n✅ Membre {id_membre} supprimé.")
            except Exception as e:
                print(f"\n❌ Erreur: {e}")
        else:
            print("Suppression annulée.")

    def do_supprimer_livre(self, arg):
        """Supprime un livre (avec confirmation)"""
        isbn = arg.strip()
        if not isbn:
            isbn = input("ISBN du livre à supprimer : ").strip()
        if isbn not in self.biblio.livres:
            print(f"\n❌ Livre {isbn} introuvable")
            return
        confirm = input(f"Confirmez la suppression du livre {isbn} (o/N) ? ").lower()
        if confirm == 'o':
            try:
                self.biblio.supprimer_livre(isbn)
                print(f"\n✅ Livre {isbn} supprimé.")
            except Exception as e:
                print(f"\n❌ Erreur: {e}")
        else:
            print("Suppression annulée.")

    # ===== Commande exporter CSV =====
    def do_exporter_csv(self, arg):
        """Exporte les données actuelles en fichiers CSV"""
        try:
            self.biblio.exporter_csv()  # méthode à implémenter côté Bibliotheque
            print("\n✅ Données exportées avec succès dans le dossier 'export'")
        except Exception as e:
            print(f"\n❌ Erreur lors de l'export : {e}")

    # ===== Commande aide avancée =====
    def do_aide_avancee(self, arg):
        """Affiche des conseils et astuces avancés pour l’utilisation"""
        print("""
Commandes avancées utiles :
- exporter_csv : Sauvegarde les données en CSV dans 'export/'
- voir_emprunts : Liste les emprunts en cours
- rechercher [terme] : Chercher un livre par titre, auteur ou genre
- supprimer_membre [ID] : Supprimer un membre (avec confirmation)
- supprimer_livre [ISBN] : Supprimer un livre (avec confirmation)

Utilisez les raccourcis numériques pour un accès rapide.
""")

    # ===== Commandes emprunts en cours =====
    def do_voir_emprunts(self, arg):
        """Affiche les emprunts en cours"""
        print("\n=== EMPRUNTS EN COURS ===")
        emprunts = [l for l in self.biblio.livres.values() if l.statut != "disponible"]
        
        if not emprunts:
            print("Aucun emprunt en cours")
            return
            
        for livre in emprunts:
            id_membre = livre.statut.split(":")[1]
            membre = self.biblio.membres.get(id_membre, None)
            nom_membre = membre.nom if membre else "Membre inconnu"
            print(f"\n- {livre.titre} emprunté par {nom_membre} (ID: {id_membre})")

    # ===== Commandes système =====
    def emptyline(self):
        """Ne rien faire quand on appuie sur Entrée sans commande"""
        pass

    def precmd(self, line):
        """Transforme les commandes en minuscules pour plus de tolérance"""
        return line.lower()

    def default(self, line):
        """Gère les numéros de menu et commandes inconnues"""
        menus = {
            '1': 'ajouter_livre',
            '2': 'inscrire_membre',
            '3': 'emprunter',
            '4': 'rendre',
            '5': 'lister_livres',
            '6': 'lister_membres',
            '7': 'rechercher',
            '8': 'voir_emprunts',
            '9': 'statistiques',
            '10': 'quitter'
        }
        
        if line in menus:
            self.onecmd(menus[line])
        else:
            print(f"\n❌ Commande inconnue: {line}\nTapez 'aide' pour la liste des commandes")

if __name__ == "__main__":
    try:
        BibliothequeCLI().cmdloop()
    except KeyboardInterrupt:
        print("\n\nInterruption par l'utilisateur")
        sys.exit(0)
