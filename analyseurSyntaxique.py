# ce programme reçoit la liste de jetons du analyseurLex et vérifie qu’elle respecte la grammaire LL(1)
from analyseurLex import tokenize,errlexic

FIRST_F = ("(", "SYMBOLE", "@")  #premier(F)
ORDER = ["(", "SYMBOLE", "@", "|", "*", "+", "?", ")", "EOF"] #pour garder l'ordre des jetons dans le msg d'erreur

def display(kind):
    if kind == "SYMBOLE":
        return "un symbole"
    if kind == "EOF":
        return "fin de l'expression"
    return f"'{kind}'"
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens   # liste des jetons par l'anlyseur lexicale
        self.i = 0             # indice du jeton courant
        self.expected = set()  # jetons testee à la position courante
