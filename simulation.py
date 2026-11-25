"""Simulation d'un AFN avec transitions epsilon (Partie 5)."""

from collections import defaultdict


class Simulateur:
    """Prépare les transitions une seule fois pour tester plusieurs mots."""

    def __init__(self, fragment):
        self.init = fragment.init
        self.fin = fragment.fin
        self.epsilon = defaultdict(set)
        self.par_symbole = defaultdict(lambda: defaultdict(set))

        for source, etiquette, cible in fragment.transitions:
            if etiquette is None or etiquette == "ε":
                self.epsilon[source].add(cible)
            else:
                self.par_symbole[source][etiquette].add(cible)

    def epsilon_fermeture(self, etats):
        """Renvoie les états accessibles depuis etats avec zéro ou plusieurs ε."""
        fermeture = set(etats)
        pile = list(fermeture)

        while pile:
            etat = pile.pop()
            for suivant in self.epsilon[etat]:
                if suivant not in fermeture:
                    fermeture.add(suivant)
                    pile.append(suivant)

        return fermeture

    def accepte(self, mot):
        """Indique si le mot est reconnu par l'automate."""
        courant = self.epsilon_fermeture({self.init})

        for caractere in mot:
            atteints = set()
            for etat in courant:
                atteints.update(self.par_symbole[etat].get(caractere, ()))
            courant = self.epsilon_fermeture(atteints)

            if not courant:
                return False

        return self.fin in courant


def epsilon_fermeture(transitions, etats):
    """Version indépendante de l'ε-fermeture, pratique pour les tests."""
    epsilon = defaultdict(set)
    for source, etiquette, cible in transitions:
        if etiquette is None or etiquette == "ε":
            epsilon[source].add(cible)

    fermeture = set(etats)
    pile = list(fermeture)

    while pile:
        etat = pile.pop()
        for suivant in epsilon[etat]:
            if suivant not in fermeture:
                fermeture.add(suivant)
                pile.append(suivant)

    return fermeture


def accepte(fragment, mot):
    """Fonction simple utilisée par le reste du projet et par run_tests.py."""
    return Simulateur(fragment).accepte(mot)
