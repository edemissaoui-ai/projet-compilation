"""Exécute le jeu de tests tests/tests.txt (Étudiant 4).

Utilisation (depuis la racine du dépôt) :
    python3 tests/run_tests.py [fichier_de_tests]

Pour chaque expression valide :
  * les mots acceptés doivent être reconnus et les mots rejetés refusés ;
  * propriété « au plus 2n états » (n = nombre de symboles, @, |, *, +, ?),
    numérotation contiguë 0 .. 2n-1 obtenue sans variable globale ;
  * invariant de Thompson : l'état initial n'a pas de transition entrante,
    l'état d'acceptation n'a pas de transition sortante.
Pour chaque test d'erreur : l'analyse doit échouer à la position indiquée.
Enfin, la propriété des 2n états est contrôlée automatiquement sur des
expressions engendrées aléatoirement et sur des imbrications profondes.

Le code de retour est 0 si tous les tests passent, 1 sinon.
"""
import os
import random
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))
sys.path.insert(0, RACINE)

from analyseurLex import tokenize            # noqa: E402
from analyseurSyntaxique import Parser, ParseError  # noqa: E402

# La reconnaissance d'un mot relève de la partie 5 (Étudiant 3). Si son
# module est présent, on l'utilise ; sinon on se sert d'une version minimale
# fondée sur l'ε-fermeture, réservée aux tests.
try:
    from simulation import accepte          # noqa: E402
except ImportError:
    def epsilon_fermeture(transitions, etats):
        pile, vus = list(etats), set(etats)
        while pile:
            q = pile.pop()
            for source, etiquette, cible in transitions:
                if source == q and etiquette is None and cible not in vus:
                    vus.add(cible)
                    pile.append(cible)
        return vus

    def accepte(fragment, mot):
        courant = epsilon_fermeture(fragment.transitions, {fragment.init})
        for c in mot:
            suivants = {cible for source, etiquette, cible in fragment.transitions
                        if source in courant and etiquette == c}
            courant = epsilon_fermeture(fragment.transitions, suivants)
        return fragment.fin in courant


def construire(expression):
    """Analyse complète ; renvoie (fragment, n') avec R.n = 0."""
    parser = Parser(tokenize(expression))
    fragment, n_sortant = parser.R(0)
    parser.eat("EOF")
    return fragment, n_sortant


def taille(expression):
    """n de l'énoncé : symboles, @, |, *, +, ? (ni parenthèses ni concaténation)."""
    return sum(1 for c in expression if c not in "()")


def erreurs_proprietes(expression, fragment, n_sortant):
    """Liste (vide si tout va bien) des violations de propriétés structurelles."""
    erreurs = []
    n = taille(expression)
    etats = fragment.states()
    if len(etats) > 2 * n:
        erreurs.append(f"{len(etats)} états > 2n = {2 * n}")
    if set(etats) != set(range(n_sortant)):
        erreurs.append(f"numérotation non contiguë (n' = {n_sortant}, états {etats})")
    if any(cible == fragment.init for _, _, cible in fragment.transitions):
        erreurs.append(f"l'état initial {fragment.init} a une transition entrante")
    if any(source == fragment.fin for source, _, _ in fragment.transitions):
        erreurs.append(f"l'état final {fragment.fin} a une transition sortante")
    return erreurs


def lire_tests(chemin):
    with open(chemin, encoding="utf-8") as f:
        for numero, ligne in enumerate(f, 1):
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue
            champs = [c.strip() for c in ligne.split(";")]
            if len(champs) != 3:
                raise ValueError(f"ligne {numero} mal formée : {ligne}")
            yield numero, champs


def mots(champ):
    return ["" if m == "@" else m for m in champ.split()]


def tester_fichier(chemin):
    succes = echecs = 0
    for numero, (expression, champ2, champ3) in lire_tests(chemin):
        problemes = []
        if champ2 == "ERREUR":
            attendue = int(champ3)
            try:
                construire(expression)
                problemes.append("expression acceptée alors qu'une erreur était attendue")
            except ParseError as e:
                if e.pos != attendue:
                    problemes.append(f"erreur à la position {e.pos}, {attendue} attendue")
                detail = str(e)
            libelle = f"[erreur] {expression}"
        else:
            try:
                fragment, n_sortant = construire(expression)
            except ParseError as e:
                problemes.append(f"rejet inattendu : {e}")
            else:
                for m in mots(champ2):
                    if not accepte(fragment, m):
                        problemes.append(f"« {m or '@'} » devrait être accepté")
                for m in mots(champ3):
                    if accepte(fragment, m):
                        problemes.append(f"« {m or '@'} » devrait être rejeté")
                problemes += erreurs_proprietes(expression, fragment, n_sortant)
                detail = f"{len(fragment.states())} états, 2n = {2 * taille(expression)}"
            libelle = expression
        if problemes:
            echecs += 1
            print(f"ÉCHEC  l.{numero:<3} {libelle}")
            for p in problemes:
                print(f"         - {p}")
        else:
            succes += 1
            print(f"OK     l.{numero:<3} {libelle:<22} {detail}")
    return succes, echecs


# ---------- test automatique de la propriété « au plus 2n états » ----------

def expression_aleatoire(rng, profondeur):
    """Engendre une expression valide en suivant la grammaire R / T / F / A."""
    def R(p):
        return "|".join(T(p) for _ in range(rng.choice([1, 1, 1, 2, 3])))

    def T(p):
        return "".join(F(p) for _ in range(rng.choice([1, 1, 2, 3])))

    def F(p):
        return A(p) + "".join(rng.choice("*+?") for _ in range(rng.choice([0, 0, 0, 1, 2])))

    def A(p):
        if p > 0 and rng.random() < 0.35:
            return "(" + R(p - 1) + ")"
        return rng.choice("abcXY09@")

    return R(profondeur)


def tester_2n(nombre=500, graine=2026):
    rng = random.Random(graine)
    cas = [expression_aleatoire(rng, rng.randint(1, 6)) for _ in range(nombre)]
    cas += ["(" * k + "a*" + ")*" * k for k in (5, 20, 40)]   # (((a*)*)*)...
    cas += ["a" * 300, "|".join("ab" for _ in range(100)), "a" + "*+?" * 50]
    echecs = 0
    for expression in cas:
        try:
            fragment, n_sortant = construire(expression)
            problemes = erreurs_proprietes(expression, fragment, n_sortant)
        except (ParseError, RecursionError) as e:
            problemes = [f"{type(e).__name__} : {e}"]
        if problemes:
            echecs += 1
            print(f"ÉCHEC  2n  {expression[:60]}")
            for p in problemes:
                print(f"         - {p}")
    print(f"Propriété des 2n états : {len(cas) - echecs}/{len(cas)} expressions conformes "
          f"({nombre} aléatoires, graine {graine}, + 6 cas extrêmes)")
    return len(cas) - echecs, echecs


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RACINE, "tests", "tests.txt")
    s1, e1 = tester_fichier(chemin)
    print(f"\nJeu de tests : {s1}/{s1 + e1} tests réussis\n")
    s2, e2 = tester_2n()
    return 0 if e1 == 0 and e2 == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
