class Fragment:

    def __init__(self, init, fin, transitions):
        self.init = init
        self.fin = fin
        self.transitions = transitions

    def states(self):
        result = {self.init, self.fin}
        for source, label, target in self.transitions:
            result.add(source)
            result.add(target)
        return sorted(result)


def make_symbol(character, n):
    """a: i --a--> f."""
    return Fragment(n, n + 1, [(n, character, n + 1)]), n + 2


def make_epsilon(n):
    """@: i --epsilon--> f."""
    return Fragment(n, n + 1, [(n, None, n + 1)]), n + 2


def make_union(left, right, n):
    """r|s: two new states and four epsilon links."""
    init = n
    fin = n + 1
    edges = list(left.transitions) + list(right.transitions)
    edges += [
        (init, None, left.init),
        (init, None, right.init),
        (left.fin, None, fin),
        (right.fin, None, fin),
    ]
    return Fragment(init, fin, edges), n + 2


def make_concat(left, right, n):
    """rs: one epsilon link fin(left) -> init(right), no new state."""
    edges = list(left.transitions)
    edges.append((left.fin, None, right.init))
    edges.extend(right.transitions)
    return Fragment(left.init, right.fin, edges), n


def make_star(fragment, n):
    """r*: two new states and the loop fin(r) -> init(r)."""
    init = n
    fin = n + 1
    edges = list(fragment.transitions)
    edges += [
        (init, None, fragment.init),
        (fragment.fin, None, fin),
        (fragment.fin, None, fragment.init),
        (init, None, fin),
    ]
    return Fragment(init, fin, edges), n + 2


def make_plus(fragment, n):
    """r+ = r r*: only the loop fin -> init, no second copy of r."""
    edges = list(fragment.transitions)
    edges.append((fragment.fin, None, fragment.init))
    return Fragment(fragment.init, fragment.fin, edges), n


def make_optional(fragment, n):
    """r? = r|@: only the epsilon edge init -> fin, no second copy of r."""
    edges = list(fragment.transitions)
    edges.append((fragment.init, None, fragment.fin))
    return Fragment(fragment.init, fragment.fin, edges), n
