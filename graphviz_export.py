"""Export d'un fragment d'automate au format DOT (Partie 5)."""

import json
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path


def _id_dot(etat):
    """Retourne un identifiant DOT entre guillemets."""
    return json.dumps(str(etat), ensure_ascii=False)


def _est_epsilon(etiquette):
    return etiquette is None or etiquette == "ε"


def _etiquette_dot(etiquette):
    valeur = "ε" if _est_epsilon(etiquette) else str(etiquette)
    return json.dumps(valeur, ensure_ascii=False)


def vers_dot(fragment):
    """Construit le texte DOT correspondant au fragment de Thompson.

    Les transitions ayant la même source et la même destination sont regroupées
    sur une seule arête, comme demandé dans l'énoncé.
    """
    etats = {fragment.init, fragment.fin}
    transitions_groupees = defaultdict(list)

    for source, etiquette, cible in fragment.transitions:
        etats.add(source)
        etats.add(cible)
        cle = (source, cible)
        valeur = "ε" if _est_epsilon(etiquette) else str(etiquette)
        if valeur not in transitions_groupees[cle]:
            transitions_groupees[cle].append(valeur)

    ordre_etats = sorted(etats, key=lambda valeur: str(valeur))
    lignes = [
        "digraph AFN {",
        "    rankdir=LR;",
        "    node [shape=circle];",
        "    \"__debut\" [shape=point];",
        f"    \"__debut\" -> {_id_dot(fragment.init)};",
        f"    {_id_dot(fragment.fin)} [shape=doublecircle];",
    ]

    for etat in ordre_etats:
        lignes.append(f"    {_id_dot(etat)};")

    for (source, cible), etiquettes in sorted(
        transitions_groupees.items(),
        key=lambda element: (str(element[0][0]), str(element[0][1])),
    ):
        etiquettes.sort(key=lambda valeur: (valeur == "ε", valeur))
        label = ",".join(etiquettes)
        lignes.append(
            f"    {_id_dot(source)} -> {_id_dot(cible)} "
            f"[label={json.dumps(label, ensure_ascii=False)}];"
        )

    lignes.append("}")
    return "\n".join(lignes) + "\n"


def ecrire_dot(fragment, chemin):
    """Écrit l'automate dans le fichier DOT demandé."""
    chemin = Path(chemin)
    chemin.write_text(vers_dot(fragment), encoding="utf-8")
    return chemin


def rendre_png(chemin_dot, chemin_png):
    """Lance Graphviz pour produire une image PNG à partir du fichier DOT."""
    executable = shutil.which("dot")
    if executable is None:
        raise RuntimeError(
            "La commande 'dot' est introuvable. Installez Graphviz, puis réessayez."
        )

    subprocess.run(
        [executable, "-Tpng", str(chemin_dot), "-o", str(chemin_png)],
        check=True,
    )
    return Path(chemin_png)
