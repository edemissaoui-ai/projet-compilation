from collections import namedtuple
#au lieu d'utiliser des classes et pour la lisibilté
token = namedtuple('token', ['kind', 'value','pos'])
class LexError(Exception):
    def __init__(self, pos, message):
        super().__init__(message)
        self.pos = pos
        self.message = message
#Une exception personnalisée pour les erreurs lexicales. Elle garde la position et le message

OPERATORS = set("|*+?()@") #les operateurs


def tokenize(text):
    tokens = []
    for i, c in enumerate(text, start=1):
        if c in OPERATORS:
            tokens.append(token(c, c, i))
        elif c.isascii() and c.isalnum(): # si un caractere ou un symbole
            tokens.append(token("SYMBOLE", c, i))
        else:
            raise LexError(i, f"Erreur à la position {i} : caractère invalide {c!r}")
    tokens.append(token("EOF", "", len(text) + 1))#jeton EOF
    return tokens