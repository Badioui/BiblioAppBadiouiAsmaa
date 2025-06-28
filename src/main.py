import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from datetime import datetime
import csv
from collections import Counter
import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PIL import Image, ImageTk


from bibliotheque import Bibliotheque, Livre, Membre
from exceptions import * 
from visualisations import Visualisation


# Couleurs globales 
COULEUR_BLEU = "#3498db"
COULEUR_ACCENT = "#f39c12"
COULEUR_TEXTE = "#2c3e50"
COULEUR_FOND = "#f5f7fa"


class BibliothequeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📚 Système de Gestion de Bibliothèque")
        self.geometry("1100x700")
        
        self.biblio = Bibliotheque()
        # Création du fichier historique s'il n'existe pas
        historique_path = Path("data/historique.csv")
        if not historique_path.exists():
            historique_path.parent.mkdir(parents=True, exist_ok=True)
            with historique_path.open("w", encoding="utf-8", newline="") as f:
                f.write("date;isbn;id_membre;action\n")

        
        self._configurer_interface()
        self._creer_sidebar()
        self.afficher_accueil()
        
        self.report_callback_exception = self._handle_exception
        self.protocol("WM_DELETE_WINDOW", self._fermer_application)

    def _configurer_interface(self):
        self.configure(bg=COULEUR_FOND)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
    
        self.style.configure('TFrame', background=COULEUR_FOND)
        self.style.configure('TLabel', background=COULEUR_FOND, font=('Segoe UI', 11), foreground=COULEUR_TEXTE)
        self.style.configure('TLabelFrame.Label', font=('Segoe UI', 11, 'bold'))
        self.style.configure("Rounded.TButton", 
        font=('Segoe UI', 10, 'bold'),
        padding=6,
        relief="flat",
        background=COULEUR_BLEU,
        foreground='white')
        self.style.map("Rounded.TButton",
        background=[("active", COULEUR_ACCENT)],
        foreground=[("active", 'white')])
        self.style.configure("Treeview",
        font=('Segoe UI', 10),
        rowheight=28,
        background='white',
        fieldbackground='white',
        foreground=COULEUR_TEXTE)

        self.style.configure("Treeview.Heading",
        font=('Segoe UI', 10, 'bold'),
        background=COULEUR_BLEU,
        foreground='white')

        self.sidebar = ttk.Frame(self, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)

        self.main_area = ttk.Frame(self)
        self.main_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)


    def _creer_sidebar(self):
        self.sidebar.configure(style='TFrame')
        ttk.Label(self.sidebar, text="📚 MENU", font=('Segoe UI', 14, 'bold')).pack(pady=20)

        boutons = [
            ("🏠 Accueil", self.afficher_accueil),
            ("📖 Livres", self.afficher_livres),
            ("👥 Membres", self.afficher_membres),
            ("🔁 Emprunts", self.afficher_emprunts),
            ("📊 Statistiques", self.afficher_statistiques),
            ("💾 Sauvegarder", self._sauvegarder)
        ]

        for texte, commande in boutons:
            btn = ttk.Button(self.sidebar, text=texte, command=commande)
            btn.pack(fill=tk.X, padx=15, pady=8)


    def _create_tooltip(self, widget, text):
        # Tooltip minimaliste sur hover
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack(ipadx=5, ipady=2)
        
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def leave(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _fermer_application(self):
        self._sauvegarder()
        self.destroy()

    def _sauvegarder(self):
        try:
            self.biblio.sauvegarder_donnees()
            messagebox.showinfo("Sauvegarde", "Données sauvegardées avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la sauvegarde : {e}")

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()


    def afficher_accueil(self):
        self.clear_main_area()

    # Couleurs et polices
        COULEUR_BLEU = "#2980b9"
        COULEUR_ACCENT = "#f39c12"
        COULEUR_FOND = "#ecf0f1"
        COULEUR_TEXTE = "#34495e"
        COULEUR_CARTES = "#ffffff"
        COULEUR_CONSEILS_BG = "#dff0d8"

    # Police personnalisée
        titre_font = Font(family="Segoe UI", size=24, weight="bold")
        sous_titre_font = Font(family="Segoe UI", size=12)
        chiffre_font = Font(family="Segoe UI", size=20, weight="bold")

    # Barre supérieure
        header = ttk.Frame(self.main_area)
        header.pack(fill=tk.X, pady=(0,20), padx=20)

    # Icône livre (simple carré bleu à gauche)
        canvas_icon = tk.Canvas(header, width=40, height=40, bg=COULEUR_BLEU, highlightthickness=0)
        canvas_icon.create_text(20, 20, text="📚", font=("Segoe UI Emoji", 24))
        canvas_icon.pack(side=tk.LEFT)

    # Titre
        ttk.Label(header, text="Tableau de bord", font=titre_font, foreground=COULEUR_BLEU).pack(side=tk.LEFT, padx=10)

    # Frame cartes statistiques
        cartes_frame = ttk.Frame(self.main_area)
        cartes_frame.pack(fill=tk.X, padx=20)

    # Données
        livres_count = len(self.biblio.livres)
        membres_count = len(self.biblio.membres)
        emprunts_count = sum(len(m.livres_empruntes) for m in self.biblio.membres.values())
        ratio = emprunts_count / livres_count if livres_count > 0 else 0

        stats = [
            ("📚 Livres", livres_count, COULEUR_BLEU),
            ("👥 Membres", membres_count, "#27ae60"),
            ("🔖 Emprunts", emprunts_count, COULEUR_ACCENT),
        ]

    # Fonction pour créer une carte
        def creer_carte(parent, label, val, couleur):
            cadre = tk.Frame(parent, bg=COULEUR_CARTES, bd=0, relief=tk.RAISED)
            cadre.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, ipadx=10, ipady=20)

        # Ombre légère (simple effet)
            cadre.config(highlightbackground="#bbb", highlightthickness=1)

        # Label icône + texte
            label_icon = tk.Label(cadre, text=label, font=sous_titre_font, bg=COULEUR_CARTES, fg=COULEUR_TEXTE)
            label_icon.pack(anchor='w', padx=15)

        # Chiffre grand et coloré
            chiffre = tk.Label(cadre, text=str(val), font=chiffre_font, bg=COULEUR_CARTES, fg=couleur)
            chiffre.pack(anchor='w', padx=15, pady=(5,10))

        for label, val, couleur in stats:
            creer_carte(cartes_frame, label, val, couleur)

    # Graphique camembert des emprunts / disponibles
        graphique_frame = ttk.Frame(self.main_area)
        graphique_frame.pack(pady=30, padx=20, fill=tk.BOTH, expand=True)

        fig, ax = plt.subplots(figsize=(4,3), dpi=100)
        labels = ['Empruntés', 'Disponibles']
        sizes = [emprunts_count, max(livres_count - emprunts_count, 0)]
        colors = [COULEUR_ACCENT, COULEUR_BLEU]
        explode = (0.1, 0)

        ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                startangle=90, colors=colors, shadow=True)
        ax.axis('equal')  # Cercle parfait
        ax.set_title("Répartition des livres", fontsize=14, color=COULEUR_TEXTE)

        canvas = FigureCanvasTkAgg(fig, master=graphique_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True)

    # Encadré conseils
        conseils = [
            "🔎 Utilisez l'onglet Livres pour gérer la collection.",
            "👥 Inscrivez de nouveaux membres facilement.",
            "📅 Surveillez les emprunts pour éviter les retards.",
            "📊 Consultez les statistiques pour suivre l'activité.",
            "💾 N'oubliez pas de sauvegarder vos données régulièrement."
        ]

        conseils_frame = tk.Frame(self.main_area, bg=COULEUR_CONSEILS_BG, bd=2, relief=tk.GROOVE)
        conseils_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(conseils_frame, text="Conseils d’utilisation", font=('Segoe UI', 14, 'bold'), background=COULEUR_CONSEILS_BG).pack(anchor='w', padx=15, pady=(10,5))

        for c in conseils:
            ttk.Label(conseils_frame, text=c, font=sous_titre_font, background=COULEUR_CONSEILS_BG).pack(anchor='w', padx=25, pady=2)

    # Optionnel : footer bas
        footer = ttk.Label(self.main_area, text="📖 BibliothèqueApp © 2025", font=('Segoe UI', 9), foreground='#888')
        footer.pack(side=tk.BOTTOM, pady=10)


    # --- Gestion Livres ---
    def afficher_livres(self):
        self.clear_main_area()
        
        ttk.Label(self.main_area, 
                 text="GESTION DES LIVRES", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        search_frame = ttk.Frame(self.main_area)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT)
        self.search_livre = ttk.Entry(search_frame)
        self.search_livre.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.search_livre.bind('<KeyRelease>', self._filtrer_livres)
        self.search_livre.focus_set()  # focus automatique
        
        colonnes = ('isbn', 'titre', 'auteur', 'annee', 'genre', 'statut')
        self.tree_livres = ttk.Treeview(self.main_area, columns=colonnes, show='headings')
        
        for col in colonnes:
            self.tree_livres.heading(col, text=col.upper(), command=lambda c=col: self._tri_treeview(self.tree_livres, c, False))
            self.tree_livres.column(col, width=120)
        
        self.tree_livres.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        form_frame = ttk.LabelFrame(self.main_area, text="Ajouter un nouveau livre")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        champs = ['ISBN', 'Titre', 'Auteur', 'Année', 'Genre']
        self.entries_livre = {}
        
        for i, champ in enumerate(champs):
            ttk.Label(form_frame, text=champ).grid(row=0, column=i, padx=2, pady=2)
            entry = ttk.Entry(form_frame)
            entry.grid(row=1, column=i, padx=2, pady=2, sticky='ew')
            form_frame.columnconfigure(i, weight=1)
            self.entries_livre[champ] = entry
        
        ttk.Button(form_frame, text="Ajouter", style="Rounded.TButton", command=self._ajouter_livre).grid(
            row=1, column=len(champs), padx=5, sticky='e')
        
        btn_frame = ttk.Frame(self.main_area)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Supprimer", style="Rounded.TButton", command=self._supprimer_livre).pack(side=tk.LEFT)
        
        self._actualiser_liste_livres()

    def _tri_treeview(self, tree, col, reverse):
        # Trie la Treeview par la colonne donnée
        data = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        # Essaye de convertir en int pour trier numériquement si possible
        try:
            data = [(int(item[0]), item[1]) for item in data]
        except Exception:
            pass
        
        data.sort(reverse=reverse)
        
        for index, (val, k) in enumerate(data):
            tree.move(k, '', index)
        
        # Change le callback pour inverser le tri au clic suivant
        tree.heading(col, command=lambda: self._tri_treeview(tree, col, not reverse))

    def _actualiser_liste_livres(self):
        self.tree_livres.delete(*self.tree_livres.get_children())
        for livre in self.biblio.livres.values():
            self.tree_livres.insert('', 'end', values=(
                livre.isbn, livre.titre, livre.auteur, 
                livre.annee, livre.genre, livre.statut))

    def _filtrer_livres(self, event=None):
        terme = self.search_livre.get().lower()
        self.tree_livres.delete(*self.tree_livres.get_children())
        
        for livre in self.biblio.livres.values():
            if (terme in livre.isbn.lower() or 
                terme in livre.titre.lower() or 
                terme in livre.auteur.lower()):
                self.tree_livres.insert('', 'end', values=(
                    livre.isbn, livre.titre, livre.auteur, 
                    livre.annee, livre.genre, livre.statut))

    def _ajouter_livre(self):
        try:
            # Validation simple champs non vides
            for champ in ['ISBN', 'Titre', 'Auteur', 'Année', 'Genre']:
                if not self.entries_livre[champ].get().strip():
                    raise ValueError(f"Le champ '{champ}' est obligatoire")
            
            livre = Livre(
                isbn=self.entries_livre['ISBN'].get().strip(),
                titre=self.entries_livre['Titre'].get().strip(),
                auteur=self.entries_livre['Auteur'].get().strip(),
                annee=int(self.entries_livre['Année'].get()),
                genre=self.entries_livre['Genre'].get().strip()
            )
            
            self.biblio.ajouter_livre(livre)
            self._actualiser_liste_livres()
            self._sauvegarder() 
            
            for entry in self.entries_livre.values():
                entry.delete(0, tk.END)
            self.entries_livre['ISBN'].focus_set()
            
            
            messagebox.showinfo("Succès", "Livre ajouté avec succès")
            
        except ValueError as e:
            messagebox.showerror("Erreur", f"Données invalides : {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ajouter le livre : {e}")

    def _supprimer_livre(self):
        selection = self.tree_livres.selection()
        if not selection:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un livre")
            return
            
        isbn = str(self.tree_livres.item(selection[0])['values'][0]).strip()

        
        try:
            # Utilise ta méthode métier ici (plus sûr)
            self.biblio.supprimer_livre(isbn)
            self._actualiser_liste_livres()
            self._sauvegarder() 
            messagebox.showinfo("Succès", "Livre supprimé avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la suppression : {e}")

    # --- Gestion Membres ---
    def afficher_membres(self):
        self.clear_main_area()
        
        ttk.Label(self.main_area, 
                 text="GESTION DES MEMBRES", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        colonnes = ('id', 'nom', 'emprunts')
        self.tree_membres = ttk.Treeview(self.main_area, columns=colonnes, show='headings')
        
        for col in colonnes:
            self.tree_membres.heading(col, text=col.upper(), command=lambda c=col: self._tri_treeview(self.tree_membres, c, False))
            self.tree_membres.column(col, width=120)
        
        self.tree_membres.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        form_frame = ttk.LabelFrame(self.main_area, text="Ajouter un nouveau membre")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, padx=2, pady=2)
        self.entry_membre_id = ttk.Entry(form_frame)
        self.entry_membre_id.grid(row=1, column=0, padx=2, pady=2, sticky='ew')
        
        ttk.Label(form_frame, text="Nom:").grid(row=0, column=1, padx=2, pady=2)
        self.entry_membre_nom = ttk.Entry(form_frame)
        self.entry_membre_nom.grid(row=1, column=1, padx=2, pady=2, sticky='ew')
        
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=3)
        
        ttk.Button(form_frame, text="Ajouter", style="Rounded.TButton", command=self._ajouter_membre).grid(
            row=1, column=2, padx=5, sticky='e')
        
        btn_frame = ttk.Frame(self.main_area)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Supprimer", style="Rounded.TButton", command=self._supprimer_membre).pack(side=tk.LEFT)
        
        self._actualiser_liste_membres()
        self.entry_membre_id.focus_set()

    def _actualiser_liste_membres(self):
        self.tree_membres.delete(*self.tree_membres.get_children())
        for membre in self.biblio.membres.values():
            nb_emprunts = len(membre.livres_empruntes)
            self.tree_membres.insert('', 'end', values=(
                membre.id, membre.nom, f"{nb_emprunts}/{Membre.MAX_EMPRUNTS}"))

    def _ajouter_membre(self):
        try:
            if not self.entry_membre_id.get().strip():
                raise ValueError("Le champ 'ID' est obligatoire")
            if not self.entry_membre_nom.get().strip():
                raise ValueError("Le champ 'Nom' est obligatoire")
            
            membre = Membre(
                id=self.entry_membre_id.get().strip(),
                nom=self.entry_membre_nom.get().strip()
            )
            
            self.biblio.enregistrer_membre(membre)
            self._actualiser_liste_membres()
            self._sauvegarder() 
            
            self.entry_membre_id.delete(0, tk.END)
            self.entry_membre_nom.delete(0, tk.END)
            self.entry_membre_id.focus_set()
            
            messagebox.showinfo("Succès", "Membre ajouté avec succès")
            
        except ValueError as e:
            messagebox.showerror("Erreur", f"Données invalides : {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ajouter le membre : {e}")

    def _supprimer_membre(self):
        selection = self.tree_membres.selection()
        if not selection:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un membre")
            return
            
        id_membre = str(self.tree_membres.item(selection[0])['values'][0]).strip()

        
        try:
            self.biblio.supprimer_membre(id_membre)
            self._actualiser_liste_membres()
            self._sauvegarder() 
            messagebox.showinfo("Succès", "Membre supprimé avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la suppression : {e}")

    # --- Gestion Emprunts ---
    def afficher_emprunts(self):
        self.clear_main_area()
        
        ttk.Label(self.main_area, 
                 text="GESTION DES EMPRUNTS", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        colonnes = ('membre', 'livre', 'date')
        self.tree_emprunts = ttk.Treeview(self.main_area, columns=colonnes, show='headings')
        
        for col in colonnes:
            self.tree_emprunts.heading(col, text=col.upper())
            self.tree_emprunts.column(col, width=150)
        
        self.tree_emprunts.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        form_frame = ttk.LabelFrame(self.main_area, text="Actions")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Membre:").grid(row=0, column=0, padx=2, pady=2)
        self.combo_membres = ttk.Combobox(form_frame, state='readonly')
        self.combo_membres.grid(row=1, column=0, padx=2, pady=2, sticky='ew')
        
        ttk.Label(form_frame, text="Livre:").grid(row=0, column=1, padx=2, pady=2)
        self.combo_livres = ttk.Combobox(form_frame, state='readonly')
        self.combo_livres.grid(row=1, column=1, padx=2, pady=2, sticky='ew')
        
        ttk.Button(form_frame, text="Emprunter", style="Rounded.TButton", command=self._emprunter_livre).grid(
            row=1, column=2, padx=5, sticky='e')
        self.btn_emprunter = ttk.Button(
        form_frame,
        text="Emprunter",
        style="Rounded.TButton",
        command=self._emprunter_livre
        )
        self.btn_emprunter.grid(row=1, column=2, padx=5, sticky='e')
        ttk.Button(form_frame, text="Retourner", style="Rounded.TButton", command=self._retourner_livre).grid(
        row=1, column=3, padx=5, sticky='e')
        
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=2)
        
        self._actualiser_liste_emprunts()
        self._actualiser_comboboxes()
    
    def _actualiser_si_existe(self, nom_methode: str):
        """Appelle une méthode d'actualisation uniquement si elle existe déjà."""
        meth = getattr(self, nom_methode, None)
        if callable(meth):
            meth()


    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """Intercepte toute exception Tkinter non gérée et évite la fermeture brutale."""
        import traceback, sys
        err_msg = "\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(err_msg, file=sys.stderr)           # log dans la console
        messagebox.showerror("Erreur inattendue", err_msg)



    def _retourner_livre(self):
        """Action du bouton « Retourner ». Gère les deux variantes possibles :
        - Bibliotheque.retourner_livre(isbn)
        - Bibliotheque.retourner_livre(isbn, id_membre)
        """
        selection = self.tree_emprunts.selection()
        if not selection:
            messagebox.showwarning(
                "Avertissement",
                "Veuillez sélectionner un emprunt à retourner")
            return

        # Décompose la ligne sélectionnée
        values = self.tree_emprunts.item(selection[0])['values']
        id_membre  = values[0].split(" - ")[0].strip()
        isbn_livre = values[1].split(" - ")[0].strip()

        try:
            # Calcule combien de paramètres attend la méthode métier
            meth = getattr(self.biblio, 'retourner_livre', None) \
                   or getattr(self.biblio, 'rendre_livre', None)
            if meth is None:
                raise AttributeError("La classe Bibliotheque ne possède pas de méthode de retour de livre.")

            nb_params = meth.__code__.co_argcount  # inclut 'self'
            if nb_params == 2:
                # Signature (self, isbn)
                meth(isbn_livre)
            else:
                # Signature (self, isbn, id_membre)
                meth(isbn_livre, id_membre)

            # Rafraîchit les vues (protégé pour éviter les AttributeError)
            self._actualiser_liste_emprunts()
            if hasattr(self, 'tree_membres'):
                self._actualiser_liste_membres()
            if hasattr(self, 'tree_livres'):
                self._actualiser_liste_livres()
            self._actualiser_comboboxes()
            self._sauvegarder()

            self.afficher_notification("✅ Livre retourné avec succès", couleur="#27ae60")


        except RetourImpossible as e:
            self.afficher_notification("❌ Échec de retour ", couleur="red")
        

    def _actualiser_liste_emprunts(self):
        """Recharge le tableau des emprunts avec **uniquement** les livres encore non disponibles."""

    # 1) On vide d'abord le Treeview
        self.tree_emprunts.delete(*self.tree_emprunts.get_children())
        emprunts_actuels = {}
    # 2) Parcours du fichier historique pour conserver la date d'emprunt,
    #    mais on n'affiche la ligne que si le livre est encore emprunté
        try:
            with open('data/historique.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader, None)  # saute l'entête


                for row in reader:
                    if len(row) >= 4:
                        date_str, isbn, id_membre, action = row
                        action = action.strip().lower()

                        if action == "emprunt":
                            emprunts_actuels[isbn] = (id_membre, date_str)
                        elif action == "retour" and isbn in emprunts_actuels:
                            del emprunts_actuels[isbn]  # livre retourné => supprimer de la liste


                
            for isbn, (id_membre, date_str) in emprunts_actuels.items():
                livre = self.biblio.livres.get(isbn)
                membre = self.biblio.membres.get(id_membre)

                if livre and membre:
                    self.tree_emprunts.insert('', 'end', values=(
                        f"{membre.id} - {membre.nom}",
                        f"{livre.isbn} - {livre.titre}",
                        date_str
                    ))

        except FileNotFoundError:
            pass

    def _actualiser_comboboxes(self):
        membres = [f"{m.id} - {m.nom}" for m in self.biblio.membres.values()]
        self.combo_membres['values'] = membres
        if membres:
            self.combo_membres.current(0)
        
        livres_dispo = [
            f"{l.isbn} - {l.titre}" 
            for l in self.biblio.livres.values() 
            if l.statut == "disponible"
        ]
        self.combo_livres['values'] = livres_dispo
        if livres_dispo:
            self.combo_livres.current(0)

    def _emprunter_livre(self):
        membre_str = self.combo_membres.get()
        livre_str = self.combo_livres.get()

        if not membre_str or not livre_str:
            self.afficher_notification(
            "⚠️ Sélectionnez un membre et un livre",
            couleur="#e67e22"           )
            return

        id_membre = membre_str.split(" - ")[0].strip()
        isbn_livre = livre_str.split(" - ")[0].strip()


        try:

            self.biblio.emprunter_livre(isbn_livre, id_membre)
            self._actualiser_liste_emprunts()
            self._actualiser_comboboxes()
            self._actualiser_liste_membres()
            self._actualiser_liste_livres()
            self._sauvegarder() 
            self.afficher_notification("✅ Livre emprunté avec succès", couleur="#27ae60")

        except EmpruntImpossible as e:
            self.afficher_notification(
            f"❌ Échec de l'emprunt : {e}",
            couleur="red")
        except Exception as e:
            pass

    
            

    # --- Statistiques ---
    def afficher_statistiques(self):
        """Affiche les graphiques générés par Visualisation sans fermer l'app en cas d'erreur."""
        self.clear_main_area()

        ttk.Label(
            self.main_area,
            text="📊 STATISTIQUES DE LA BIBLIOTHÈQUE",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=15)

        # 1) Génération des graphiques --------------------------------------------------------
        try:
            chemins = Visualisation.generer_tous_graphiques(
                livres=list(self.biblio.livres.values()),
                historique_path="data/historique.csv",
            )
        except Exception as e:
            print("Erreur dans les statistiques :", e)
            messagebox.showerror("Erreur", f"Impossible de générer les statistiques : {e}")
            return  # on quitte proprement l'onglet, l'app reste ouverte

        # 2) Mise en page --------------------------------------------------------------------
        frame_stats = ttk.LabelFrame(self.main_area, text="Visualisation des Données")
        frame_stats.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        images_refs: list[ImageTk.PhotoImage] = []  # pour éviter le garbage‑collection
        container = ttk.Frame(frame_stats)
        container.pack(fill=tk.BOTH, expand=True)
        cols = 2

        # 3) Boucle d'affichage ---------------------------------------------------------------
        for i, (titre, chemin) in enumerate(chemins.items()):
            bloc = ttk.Frame(container)
            bloc.grid(row=i // cols, column=i % cols, padx=15, pady=10, sticky="nsew")

            if not os.path.exists(chemin):
                ttk.Label(
                    bloc,
                    text=f"{titre} : fichier manquant",
                    foreground="red",
                ).pack()
                continue

            # Essaye d'ouvrir l'image et passe à la suivante en cas d'échec
            try:
                img = Image.open(chemin)
            except Exception as e:
                ttk.Label(
                    bloc,
                    text=f"Impossible d'ouvrir : {chemin}\n{e}",
                    foreground="red",
                ).pack()
                continue

            # Redimensionne, convertit et affiche
            img = img.resize((350, 250), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            images_refs.append(photo)

            ttk.Label(bloc, text=titre.upper(), font=("Segoe UI", 10, "bold")).pack(pady=5)
            ttk.Label(bloc, image=photo).pack()

        # 4) Colonnage flexible --------------------------------------------------------------
        for col in range(cols):
            container.columnconfigure(col, weight=1)

        self._images_refs = images_refs  # garde les références vivantes
    def afficher_notification(self, texte, couleur="#27ae60"):
        """Affiche un message temporaire dans le pied de page."""
        if hasattr(self, 'footer_message'):
            self.footer_message.destroy()
        self.footer_message = ttk.Label(self.main_area, text=texte, foreground=couleur)
        self.footer_message.pack(side=tk.BOTTOM, pady=5)
        self.after(4000, self.footer_message.destroy)
if __name__ == "__main__":
    app = BibliothequeApp()
    app.mainloop()
