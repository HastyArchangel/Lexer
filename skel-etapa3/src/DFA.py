from collections.abc import Callable
from dataclasses import dataclass

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        current_state = self.q0
        has_to_loop = True
        while word and has_to_loop:
            has_to_loop = False
            for key, value in self.d.items():
                if word.startswith(str(key[1])) and key[0] == current_state:
                    word = word[len(key[1]):]
                    current_state = value
                    has_to_loop = True 
                    
        if len(word) == 0 and current_state in self.F:
            return True
        return False
    
    def reach_sink_state(self, word: str) -> int:
        current_state = self.q0
        index = 0
        while word:
            has_transition = False
            for key, value in self.d.items():
                if word.startswith(str(key[1])) and key[0] == current_state and value != frozenset():
                    word = word[len(key[1]):]
                    current_state = value
                    has_transition = True
                    index += len(key[1])
                    break

            if not has_transition:
                return index

        return -1 

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        pass
