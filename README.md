# 📚 Mini-Projet Python : Système de Gestion de Bibliothèque

Bienvenue dans l'application **BiblioApp** — une application Python complète pour la gestion d'une bibliothèque avec interface en ligne de commande, visualisations statistiques et interface graphique Tkinter.

---

## 🌟 Fonctionnalités principales

### 📚 Gestion des livres

* Ajouter, supprimer des livres
* Emprunter et retourner un livre
* Sauvegarde automatique dans `data/livres.txt`

### 👤 Gestion des membres

* Enregistrement d’un membre
* Gestion du quota d’emprunt (maximum 3 livres)
* Sauvegarde dans `data/membres.txt`

### ⚠️ Gestion des erreurs personnalisées

* `LivreIndisponibleError`
* `QuotaEmpruntDepasseError`
* `MembreInexistantError`
* `LivreInexistantError`

### 📊 Visualisation des statistiques

* Diagramme circulaire : répartition des genres
* Histogramme : top 10 des auteurs
* Courbe : emprunts sur 30 jours

### 📂 Persistance des données

* Fichiers CSV/TXT automatiques dans `data/`
* Historique des actions dans `historique.csv`

### 🔄 Interface graphique Tkinter *(bêta)*

* Page d’accueil animée
* Fenêtre principale à venir

---

## 📁 Structure du projet

```
pyAPPBADIOUI/
├── assets/                   # Graphiques sauvegardés
├── data/                    # Fichiers CSV/TXT de données
│   ├── livres.txt
│   ├── membres.txt
│   └── historique.csv
├── docs/                    # Rapport PDF
│   └── rapport.pdf
├── src/                     # Code source Python
│   ├── main.py              # Menu interactif principal
│   ├── bibliotheque.py      # Logique métier
│   ├── exceptions.py        # Erreurs personnalisées
│   ├── gui.py               # Interface graphique Tkinter
│   ├── stats.py             # Fonctions de stats CLI
│   └── visualisations.py    # Graphiques matplotlib
├── requirements.txt               
└── README.md                # Ce fichier
```

---

## 🚀 Installation & exécution

### 1. Cloner le projet

```bash
git clone https://github.com/<ton-nom>/pyAPPBADIOUI.git
cd pyAPPBADIOUI
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Lancer l’application (CLI)

```bash
./start.sh
```

### 4. Ou directement

```bash
python src/main.py
```

---

## 📃 Exemples d'utilisation (CLI)

```bash
=== MENU PRINCIPAL ===
1. Afficher les livres
2. Afficher les membres
3. Ajouter un livre
4. Enregistrer un membre
5. Emprunter un livre
6. Retourner un livre
...
```

---

## 📊 Statistiques

Les graphiques s'afficheront et seront sauvegardés dans `assets/` :

* `stats_genres.png`
* `stats_auteurs.png`
* `stats_temps.png`

---

## 🔧 Modules Python utilisés

* `csv`, `datetime`, `os`, `tkinter`
* `matplotlib`

---

## 📊 Rapport & Vidéo

* Le fichier `docs/rapport.pdf` contient : UML, captures, explications.
* Une vidéo de 4 minutes présente l’application, les cas d’utilisation, et le code.

---

## 🌟 Auteur

Projet réalisé par **\[Ton Nom]** dans le cadre du module Python Avancé — 2025

> "Automatiser une bibliothèque, c'est cultiver la connaissance par le code."

---

## 🔧 Améliorations futures

* Interface graphique complète
* Système de recommandation (TensorFlow/Keras)
* Sauvegarde JSON ou base de données SQLite

---

Merci d'avoir consulté ce projet ✨
