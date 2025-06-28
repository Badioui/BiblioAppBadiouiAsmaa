import matplotlib
# Utilise un backend non‑interactif pour éviter tout conflit avec Tkinter
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
import csv
from datetime import datetime, timedelta
from pathlib import Path


class Visualisation:
    """Génération de graphiques pour BibliothequeApp.
    Tous les graphiques sont enregistrés sur disque (pas d'affichage direct).
    Le backend "Agg" évite la fermeture intempestive de Tkinter.
    """

    # --- Méthodes internes utilitaires --------------------------------------------------
    @staticmethod
    def _safe_savefig(save_path: str):
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(save_path, bbox_inches="tight")
        plt.close()
        return save_path

    # --- Graphique 1 : Répartition des genres -------------------------------------------
    @staticmethod
    def diagramme_genres(livres, save_path="assets/stats_genres.png"):
        if not livres:
            raise ValueError("La liste des livres est vide")

        genres = [livre.genre for livre in livres]
        compteur = Counter(genres)

        plt.figure(figsize=(6, 6))
        plt.pie(
            compteur.values(),
            labels=compteur.keys(),
            autopct=lambda p: f"{p:.1f}%\n({int(p * sum(compteur.values()) / 100)})",
            startangle=140,
        )
        plt.title("Répartition des livres par genre")
        return Visualisation._safe_savefig(save_path)

    # --- Graphique 2 : Top auteurs -------------------------------------------------------
    @staticmethod
    def histogramme_auteurs(livres, save_path="assets/stats_auteurs.png"):
        if not livres:
            raise ValueError("La liste des livres est vide")

        auteurs = [livre.auteur for livre in livres]
        top_auteurs = Counter(auteurs).most_common(10)
        if not top_auteurs:
            raise ValueError("Aucun auteur disponible pour l'histogramme")

        plt.figure(figsize=(8, 5))
        plt.barh(
            [a for a, _ in top_auteurs],
            [c for _, c in top_auteurs],
            color="#5DADE2",
        )
        plt.xlabel("Nombre de livres")
        plt.title("Top 10 des auteurs")
        plt.gca().invert_yaxis()
        return Visualisation._safe_savefig(save_path)

    # --- Graphique 3 : Courbe des emprunts ----------------------------------------------
    @staticmethod
    def courbe_emprunts(historique_path="data/historique.csv", save_path="assets/stats_temps.png"):
        jours = [(datetime.now().date() - timedelta(days=i)) for i in range(29, -1, -1)]
        compteur = {jour: 0 for jour in jours}

        try:
            with open(historique_path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f, delimiter=";"):
                    if row.get("action", "").lower() != "emprunt":
                        continue
                    try:
                        date_evt = datetime.strptime(row["date"], "%Y-%m-%d %H:%M").date()
                        if date_evt in compteur:
                            compteur[date_evt] += 1
                    except (ValueError, KeyError):
                        continue
        except FileNotFoundError:
            # Pas d'historique : la courbe sera plate
            pass

        plt.figure(figsize=(10, 4))
        plt.plot(list(compteur.keys()), list(compteur.values()), marker="o", linewidth=2)
        plt.title("Emprunts sur 30 jours")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle="--", alpha=0.6)
        return Visualisation._safe_savefig(save_path)

    # --- Génération groupée --------------------------------------------------------------
    @classmethod
    def generer_tous_graphiques(cls, livres, historique_path="data/historique.csv"):
        """Tente de générer les trois graphiques. Ignore proprement ceux qui échouent."""
        chemins = {}
        try:
            chemins["genres"] = cls.diagramme_genres(livres)
        except Exception as e:
            print("[Visualisation] Ignoré genres :", e)
        try:
            chemins["auteurs"] = cls.histogramme_auteurs(livres)
        except Exception as e:
            print("[Visualisation] Ignoré auteurs :", e)
        try:
            chemins["emprunts"] = cls.courbe_emprunts(historique_path)
        except Exception as e:
            print("[Visualisation] Ignoré emprunts :", e)
        if not chemins:
            raise RuntimeError("Aucun graphique n'a pu être généré")
        return chemins

