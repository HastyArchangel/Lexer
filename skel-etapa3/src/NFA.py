from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def __init__(self, states: set[str], states_set: set[STATE], initial_state: STATE, transitions: dict[tuple[STATE, str], set[STATE]], accept_states: set[STATE]):
        self.S = states
        self.K = states_set
        self.q0 = initial_state
        self.d = transitions
        self.F = accept_states
        

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        eps_set = {state}
        has_to_loop = True
        while has_to_loop:
            has_to_loop = False
            for key, value in self.d.items():
                for s in value:
                    if key[1] == '' and key[0] in eps_set and s not in eps_set:
                        eps_set.add(s)
                        has_to_loop = True
        return eps_set

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        states = set()  
        accept_states = set()  
        processed_states = set()  
        transitions = dict()  
        initial_closure = self.epsilon_closure(self.q0)
        processing_queue = [initial_closure]

        while processing_queue:
            current_state = processing_queue.pop(0)
            if current_state in processed_states:
                continue

            states.add(frozenset(current_state))
            processed_states.add(frozenset(current_state))

            if any(accept_state in current_state for accept_state in self.F):
                accept_states.add(frozenset(current_state))

            # Calculez starile urmatoare din starea curenta
            for symbol in self.S:
                next_states = set()
                for state in current_state:
                    next_states.update(self.d.get((state, symbol), set()))

                next_closure = set()
                for next_state in next_states:
                    next_closure.update(self.epsilon_closure(next_state))

                transitions[frozenset(current_state), symbol] = frozenset(next_closure)

                processing_queue.append(next_closure)

        return DFA(S=self.S, K=states, q0=frozenset(initial_closure), d=transitions, F=accept_states)

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], OTHER_STATE]) -> 'NFA[OTHER_STATE]':
        remapped_states = {f(state) for state in self.K}
        remapped_transitions = {(f(src), symbol): {f(dest) for dest in dest_states}
                                for (src, symbol), dest_states in self.d.items()}
        remapped_accept_states = {f(state) for state in self.F}

        return NFA(self.S, remapped_states, f(self.q0), remapped_transitions, remapped_accept_states)