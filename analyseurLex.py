from collections import namedtuple

# token = (kind, value, pos). Positions are 0-based: the position of a token
# is the index of its first character in the input string (EOF = len(text)).
token = namedtuple('token', ['kind', 'value', 'pos'])


class errlexic(Exception):
    """Gardée pour compatibilité ; les erreurs de syntaxe passent par ParseError."""

    def __init__(self, pos, message):
        super().__init__(message)
        self.pos = pos
        self.message = message


OPERATORS = set("|*+?()@")


def tokenize(text):
    tokens = []
    for i, c in enumerate(text):
        if c in OPERATORS:
            tokens.append(token(c, c, i))
        elif c.isascii() and c.isalnum():
            tokens.append(token("SYMBOLE", c, i))
        else:
            # Unknown characters become ordinary tokens: the parser reports
            # them with the same French "expected tokens" message.
            tokens.append(token(c, c, i))
    tokens.append(token("EOF", "", len(text)))
    return tokens
