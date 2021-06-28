"""
Definition:
- Follow(X) = {t | S -> * \\beta X t \\delta}

Intuition:
- if X -> A B then First(B) "is a subset" of Follow(A) and
  - Follow(X) "is a subset" of Follow(B)
    - if B -> * \\varepsilon then Follow(X) "is a subset" of Follow(A
- if S is the start symbol, then $ "is an element" of Follow(S)

"""

from firstsets import FirstSet


def create_grammar(grammar: str):
    result = {}
    for line in grammar.split('\n'):
        if not line or ":" not in line:
            continue

        lhs, rhs = line.split(":")
        lhs = lhs.strip()
        rhs = [v.strip() for v in rhs.split("|")]

        result[lhs] = rhs

    return result


def format_set(token_set: set):
    result = []
    for v in token_set:
        result.append(f'"{v}"')
    return "{ " + ", ".join(result) + " }"


class FollowSet:
    def __init__(self, grammar):
        self.grammar: dict = create_grammar(grammar)
        self.firstset = FirstSet(grammar)

    def check_is_terminal(self, input_string: str):
        return input_string not in self.grammar.keys()

    def compute(self, input_string: str):
        """
        Algorithm Sketch:
        - $ "is an element" of Follow(S)
        - First(\\beta) - {\\varepsilon} "is a subset" of Follow(X)
            - For each production A -> \\alpha X \\beta
        - Follow(A) "is a subset" of Follow(X)
            - For each production A -> \\alpha X \\beta where
                \\varepsilon "is an element" of First(\\beta)

        An algorithm to compute the FOLLOW sets:

        - see: http://www.cs.ecu.edu/karl/5220/spr16/Notes/Top-down/follow.html
        - Start with FOLLOW(N) = {} for every nonterminal N. Then perform the
          following steps until none of the FOLLOW sets can be enlarged any
          more.
          - Add $ to FOLLOW(S), where S is the start nonterminal.
          - If there is a production A → αBβ, then add every token that is
            in FIRST(β) to FOLLOW(B). (Do not add ε to FOLLOW(B).
          - If there is a production A → αB, then add all members of
            FOLLOW(A) to FOLLOW(B). (If t can follow A, then there must be
            a sentential form β A t γ Using production A → αB gives
            sentential form β α B t γ, where B is followed by t.)
        - If there is a production A → αBβ where FIRST(β) contains ε, then
            add all members of FOLLOW(A) to FOLLOW(B).
            (Reasoning is like rule 3. Just erase β.)

        """
        derivations = {}

        tokens_list = []

        for v in self.grammar.values():
            for vi in v:
                tokens_list.append(vi.split(' '))

        for non_terminals in self.grammar.keys():
            derivations[non_terminals] = ['$']
            for tokens in tokens_list:
                if non_terminals not in tokens:
                    continue

                i = tokens.index(non_terminals)

                try:
                    token = tokens[i + 1]
                except:
                    continue

                if self.check_is_terminal(token):
                    derivations[non_terminals].extend([token])
                    continue

                derivations[non_terminals].extend(self.firstset.compute(token))

        result = derivations[input_string]

        for tokens in self.grammar[input_string]:
            try:
                token = tokens.split(' ')[1]
            except:
                continue

            if self.check_is_terminal(token):
                result.extend([token])
                continue

            result.extend(derivations[token])

        return set(result) - {'\\varepsilon'}


def test_follow_set():
    grammar = """
    E: T X
    T: ( E ) | int Y
    X: + E | \\varepsilon
    Y: * T | \\varepsilon
    """
    followset = FollowSet(grammar)
    for s, expected in [
        ('E', {'$', ')'}),
        ('X', {'$', ')'}),
        ('T', {'+', '$', ')'}),
        ('Y', {'+', '$', ')'}),
    ]:
        print(f'FollowSet("{s}") = {format_set(expected)}', end=" >>> ")
        result = followset.compute(s)
        print(f"Result: {result}, Expected: {expected}")
        assert result == expected


if __name__ == '__main__':
    test_follow_set()
