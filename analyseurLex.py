from collections import namedtuple
#au lieu d'utiliser des classes et pour la lisibilté
token = namedtuple('token', ['kind', 'value','pos'])
class errlexic(Exception):
    def __init__(self, pos, message):
        super().__init__(message)
        self.pos = pos
        self.message = message
#Une exception personnalisée pour les erreurs lexicales. Elle garde la position et le message(pour le mode panique quest bonus)

OPERATORS = set("|*+?()@") #les operateurs


def tokenize(text):
    tokens = []
    for i, c in enumerate(text, start=1):
        if c in OPERATORS:
            tokens.append(token(c, c, i))
        elif c.isascii() and c.isalnum(): # si un caractere ou un symbole
            tokens.append(token("SYMBOLE", c, i))
        else:
            raise errlexic(i, f"Erreur à la position {i} : caractère invalide {c!r}")
    tokens.append(token("EOF", "", len(text) + 1)) #jeton EOF
    return tokens

    @property #pour eciter l'appel avec parenthese
    def cur(self):
        return self.tokens[self.i]

    def test(self, *kinds):
        """Teste le lookahead et mémorise ce qui était attendu."""
        self.expected.update(kinds)
        return self.cur.kind in kinds

    def advance(self):
        self.i += 1
        self.expected = set()

    def eat(self, kind):
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

    # une procédure par non-terminal 
    def R(self):
        self.T()
        self.Rp()

    def Rp(self):
        if self.test("|"):
            self.advance()
            self.T()
            self.Rp()
       

    def T(self):
        self.F()
        self.Tp()

    def Tp(self):
        if self.test(*FIRST_F):
            self.F()
            self.Tp()
        # sinon epsilon

    def F(self):
        self.A()
        self.Fp()

    def Fp(self):
        if self.test("*", "+", "?"):
            self.advance()
            self.Fp()
        #cas du epsilon

    def A(self):
        if self.test("("):
            self.advance()
            self.R()
            self.eat(")")
        elif self.test("SYMBOLE") or self.test("@"):
            self.advance()
        else:
            self.error()  # case vide

    def parse(self):
        self.R()
        self.eat("EOF")  


