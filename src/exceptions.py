class BibliothequeError(Exception):
    """Classe de base pour toutes les exceptions personnalisées du système de bibliothèque."""
    pass


class LivreIndisponibleError(BibliothequeError):
    def __init__(self, isbn: str = None, message: str = "Le livre n'est pas disponible"):
        self.isbn = isbn
        if isbn:
            message = f"Le livre {isbn} n'est pas disponible"
        super().__init__(message)


class QuotaEmpruntDepasseError(BibliothequeError):
    def __init__(self, membre_id: str = None, max_emprunts: int = 5, message: str = "Quota d'emprunts dépassé"):
        self.membre_id = membre_id
        self.max_emprunts = max_emprunts
        if membre_id:
            message = f"Le membre {membre_id} a atteint son quota maximal ({max_emprunts} emprunts)"
        super().__init__(message)


class MembreInexistantError(BibliothequeError):
    def __init__(self, membre_id: str = None, message: str = "Membre introuvable"):
        self.membre_id = membre_id
        if membre_id:
            message = f"Membre {membre_id} introuvable"
        super().__init__(message)


class LivreInexistantError(BibliothequeError):
    def __init__(self, isbn: str = None, message: str = "Livre introuvable"):
        self.isbn = isbn
        if isbn:
            message = f"Livre {isbn} introuvable"
        super().__init__(message)


class DonneesInvalidesError(BibliothequeError):
    def __init__(self, champ: str = None, valeur: str = None, message: str = "Données invalides"):
        self.champ = champ
        self.valeur = valeur
        if champ and valeur:
            message = f"Valeur invalide pour {champ} : {valeur}"
        super().__init__(message)


class ErreurSauvegardeError(BibliothequeError):
    def __init__(self, fichier: str = None, message: str = "Erreur lors de la sauvegarde"):
        self.fichier = fichier
        if fichier:
            message = f"Erreur lors de la sauvegarde dans le fichier {fichier}"
        super().__init__(message)


class ErreurChargementError(BibliothequeError):
    def __init__(self, fichier: str = None, message: str = "Erreur lors du chargement"):
        self.fichier = fichier
        if fichier:
            message = f"Erreur lors du chargement depuis le fichier {fichier}"
        super().__init__(message)


class ActionImpossibleError(BibliothequeError):
    def __init__(self, action: str = None, raison: str = None, message: str = "Action impossible"):
        self.action = action
        self.raison = raison
        if action and raison:
            message = f"Action '{action}' impossible : {raison}"
        super().__init__(message)


class LivreNonEmprunteError(BibliothequeError):
    def __init__(self, isbn: str = None, message: str = "Le livre n'a pas été emprunté"):
        self.isbn = isbn
        if isbn:
            message = f"Le livre {isbn} n'a pas été emprunté"
        super().__init__(message)


class EmpruntImpossible(BibliothequeError):
    def __init__(self, raison: str = None, message: str = "Emprunt impossible"):
        if raison:
            message = f"Emprunt impossible : {raison}"
        super().__init__(message)


class RetourImpossible(BibliothequeError):
    def __init__(self, raison: str = None, message: str = "Retour impossible"):
        if raison:
            message = f"Retour impossible : {raison}"
        super().__init__(message)
