# ce programme reçoit la liste de jetons du analyseurLex et vérifie qu’elle respecte la grammaire LL(1)
# Etudiant 2 : schéma de traduction et construction de Thompson (Partie 3).
from analyseurLex import tokenize, errlexic
from automate import (
    make_symbol, make_epsilon, make_union, make_concat,
    make_star, make_plus, make_optional,
)

FIRST_F = ("(", "SYMBOLE", "@")  #premier(F)
ORDER = ["(", "SYMBOLE", "@", "|", "*", "+", "?", ")", "EOF"] #pour garder l'ordre des jetons dans le msg d'erreur

def display(kind):
    if kind == "SYMBOLE":
        return "un symbole"
    if kind == "EOF":
        return "fin de l'expression"
    return f"'{kind}'"


class ParseError(Exception):
    def __init__(self, pos, message):
        super().__init__(message)
        self.pos = pos


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens   # liste des jetons par l'anlyseur lexicale
        self.i = 0             # indice du jeton courant
        self.expected = set()  # jetons testee à la position courante

    @property
    def cur(self):
        return self.tokens[self.i]

    def test(self, *kinds):
        self.expected.update(kinds)
        return self.cur.kind in kinds

    def advance(self):
        token = self.cur
        self.i += 1
        self.expected = set()
        return token

    def eat(self, kind):
        # Only the token required here is expected at this point: the
        # epsilon decisions of the prime procedures leave older tests behind.
        self.expected = set()
        if self.test(kind):
            self.advance()
        else:
            self.error()

    def error(self):
        tok = self.cur
        exp = [display(k) for k in ORDER if k in self.expected]
        found = display(tok.kind) if tok.kind in ("EOF", "SYMBOLE") else f"'{tok.value}'"
        if tok.kind == "SYMBOLE":
            found = f"'{tok.value}'"
        msg = (f"Erreur à la position {tok.pos} : "
               f"{' ou '.join(exp)} attendu, {found} trouvé")
        raise ParseError(tok.pos, msg)

    def parse(self):
        """R, puis contrôle de fin d'entrée ; retourne le fragment final."""
        fragment, unused_n = self.R(0)
        self.eat("EOF")
        return fragment

    # Chaque procédure reçoit n (prochain état libre) et retourne
    # (fragment, n_sortant). Le fragment h est hérité par les procédures
    # prime pour garder l'associativité à gauche.

    def R(self, n):
        """R -> T R'."""
        fragment, n1 = self.T(n)
        return self.Rp(fragment, n1)

    def Rp(self, h, n):
        """R' -> '|' T R' | ε. h est l'union déjà construite à gauche."""
        if self.test("|"):
            self.advance()
            fragment, n1 = self.T(n)
            acc, n2 = make_union(h, fragment, n1)
            return self.Rp(acc, n2)
        if self.test(")") or self.test("EOF"):
            return h, n
        self.error()

    def T(self, n):
        """T -> F T'."""
        fragment, n1 = self.F(n)
        return self.Tp(fragment, n1)

    def Tp(self, h, n):
        """T' -> F T' | ε. PREMIER(F) décide de continuer la concaténation."""
        if self.test(*FIRST_F):
            fragment, n1 = self.F(n)
            acc, n1 = make_concat(h, fragment, n1)
            return self.Tp(acc, n1)
        if self.test("|") or self.test(")") or self.test("EOF"):
            return h, n
        self.error()

    def F(self, n):
        """F -> A F'."""
        fragment, n1 = self.A(n)
        return self.Fp(fragment, n1)

    def Fp(self, h, n):
        """F' -> '*' F' | '+' F' | '?' F' | ε. Les postfixés s'enchaînent."""
        if self.test("*"):
            self.advance()
            acc, n1 = make_star(h, n)
        elif self.test("+"):
            self.advance()
            acc, n1 = make_plus(h, n)
        elif self.test("?"):
            self.advance()
            acc, n1 = make_optional(h, n)
        else:
            if self.test(*FIRST_F) or self.test("|") or self.test(")") or self.test("EOF"):
                return h, n
            self.error()
        return self.Fp(acc, n1)

    def A(self, n):
        """A -> '(' R ')' | SYMBOLE | '@'."""
        if self.test("("):
            self.advance()
            fragment, n1 = self.R(n)
            self.eat(")")
            return fragment, n1
        elif self.test("SYMBOLE") or self.test("@"):
            token = self.advance()
            if token.kind == "SYMBOLE":
                return make_symbol(token.value, n)
            return make_epsilon(n)
        else:
            self.error()
