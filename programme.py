"""Interface en ligne de commande du traducteur d'expressions régulières."""

import argparse
import sys

from analyseurLex import tokenize
from analyseurSyntaxique import ParseError, Parser
from graphviz_export import ecrire_dot
from simulation import Simulateur


def construire_automate(expression):
    """Analyse l'expression et retourne le fragment construit par Thompson."""
    analyseur = Parser(tokenize(expression))
    return analyseur.parse()


def main():
    argument = argparse.ArgumentParser(
        description="Reconnaît des mots à l'aide d'un AFN construit par Thompson."
    )
    argument.add_argument("expression", help="expression régulière à analyser")
    argument.add_argument(
        "mots",
        nargs="*",
        help='mots à tester ; utiliser "" pour le mot vide',
    )
    argument.add_argument(
        "--dot",
        metavar="FICHIER",
        help="écrit l'automate au format Graphviz DOT",
    )
    args = argument.parse_args()

    try:
        fragment = construire_automate(args.expression)
    except ParseError as erreur:
        print(erreur, file=sys.stderr)
        return 1
    except RecursionError:
        print("Erreur : expression trop imbriquée pour l'analyseur.", file=sys.stderr)
        return 1

    if args.dot:
        try:
            ecrire_dot(fragment, args.dot)
        except OSError as erreur:
            print(f"Impossible d'écrire le fichier DOT : {erreur}", file=sys.stderr)
            return 1

    simulateur = Simulateur(fragment)
    for mot in args.mots:
        resultat = "OUI" if simulateur.accepte(mot) else "NON"
        affichage = '""' if mot == "" else mot
        print(f"{affichage} : {resultat}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
