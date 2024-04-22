from .NFA import NFA
from collections.abc import Callable
from typing import List
from dataclasses import dataclass

def add_x_to_state(x: int) -> Callable[[int], int]:
    def add_to_state(state: int) -> int:
        return int(state) + x
    return add_to_state


class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')

@dataclass
class Character(Regex):
    character: str
    lowercase = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                      'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    uppercase = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 
                     'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    def __init__(self, character):
        self.character = character

    def thompson(self) -> NFA:
        # pentru cazul in care am un simbol normal
        if (len(self.character) <= 2):
            state0, state1 = 0, 1
            if (len(self.character) >= 2) and (self.character[1] in {'*', '+', '?', '|', '(', ')'}):
                self.character = self.character[1]
            alphabet = {self.character}
            states = {state0, state1}
            initial_state = state0
            transitions = {(state0, self.character): {state1}}
            accept_states = {state1}
            
        # pentru orice numar
        elif (self.character[1] == '0'):
            state0, state1 = 0, 1
            alphabet = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
            states = {state0, state1}
            initial_state = state0
            transitions = {}
            i = 0
            while i < 10:
                transitions[state0, str(i)] = {state1}
                i += 1
            accept_states = {state1}

        # pentru orice litera mica
        elif (self.character[1] == 'a'):
            state0, state1 = 0, 1
            alphabet = set(self.lowercase)
            states = {state0, state1}
            initial_state = state0
            transitions = {}
            for i in self.lowercase:
                transitions[state0, i] = {state1}

            accept_states = {state1}

        # pentru orice litera mare
        elif (self.character[1] == 'A'):
            state0, state1 = 0, 1
            alphabet = set(self.uppercase)
            states = {state0, state1}
            initial_state = state0
            transitions = {}
            for i in self.uppercase:
                transitions[state0, i] = {state1}

            accept_states = {state1}

        return NFA(alphabet, states, initial_state, transitions, accept_states)


@dataclass
class Concat(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        nfa_left = self.left.thompson()
        nfa_right = self.right.thompson()
        
        # Dau remap la nfa-ul din dreapta pentru a face loc celui din stanga
        nfa_right = nfa_right.remap_states(add_x_to_state(x = len(nfa_left.K)))

        alphabet = nfa_left.S | nfa_right.S
        states = nfa_left.K | nfa_right.K
        initial_state = nfa_left.q0
        transitions = nfa_left.d | nfa_right.d
        accept_states = nfa_right.F
        # Se iau starile, alfabetul si tranzitiile de la cele 2 nfa-uri

        for state in nfa_left.F:
            if (state, '') not in transitions:                               
                transitions[state, ''] = {nfa_right.q0} 
            else:
                transitions[state, ''].add(nfa_right.q0)
        # Se face legatura intre cele 2 nfa-uri

        return NFA(alphabet, states, initial_state, transitions, accept_states)
    
@dataclass
class Union(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        nfa_left = self.left.thompson()
        nfa_right = self.right.thompson()

        nfa_left = nfa_left.remap_states(add_x_to_state(x = 2))
        # Dau remap pentru a face loc la 2 stari 
        nfa_right = nfa_right.remap_states(add_x_to_state(x = len(nfa_left.K) + 2))
        # Aici, 2 stari + nfa-ul din stanga

        state0, state1 = 0, 1
        alphabet = nfa_left.S | nfa_right.S
        states = nfa_left.K | nfa_right.K | {state0} | {state1}
        initial_state = state0
        transitions = nfa_left.d | nfa_right.d
        accept_states = {state1}
        
        for state in nfa_left.F:
            if (state, '') not in transitions:                               
                transitions[state, ''] = {state1} 
            else:
                transitions[state, ''].add(state1)
        # Pentru nfa-ul din stanga, se face legatura cu starea finala
        

        for state in nfa_right.F:
            if (state, '') not in transitions:                               
                transitions[state, ''] = {state1} 
            else:
                transitions[state, ''].add(state1)
        # La fel si pentru cel din dreapta

        transitions[state0, ''] = {nfa_left.q0, nfa_right.q0}
        # Si legatura dintre q0 catre fiecare nfa

        return NFA(alphabet, states, initial_state, transitions, accept_states)

@dataclass
class Star(Regex):
    middle: Regex

    def thompson(self) -> NFA[int]:
        nfa_middle = self.middle.thompson()

        nfa_middle = nfa_middle.remap_states(add_x_to_state(x = 2))
        
        state0, state1 = 0, 1
        alphabet = nfa_middle.S
        states = nfa_middle.K | {state0} | {state1}
        initial_state = state0
        transitions = nfa_middle.d
        accept_states = {state1}

        # Adaug tranzitia catre inceput, pentru a permite posibilitatea de repetare
        for state in nfa_middle.F:
            if (state, '') not in transitions:                               
                transitions[state, ''] = {nfa_middle.q0} 
            else:
                transitions[state, ''].add(nfa_middle.q0)
            transitions[state, ''].add(state1) 
            # Legatura catre final

        transitions[state0, ''] = {nfa_middle.q0, state1}
        # Saltul catre sfarsit (cazul in care nu e niciun simbol, decat epsilon) si calea catre inceputul nfa-ului middle

        return NFA(alphabet, states, initial_state, transitions, accept_states)
    
@dataclass
class Plus(Regex):
    middle: Regex

    def thompson(self) -> NFA[int]:
        nfa_middle = self.middle.thompson()

        nfa_middle = nfa_middle.remap_states(add_x_to_state(x = 2))
        
        state0, state1 = 0, 1

        alphabet = nfa_middle.S
        states = nfa_middle.K | {state0} | {state1}
        initial_state = state0
        transitions = nfa_middle.d
        accept_states = {state1}

        for state in nfa_middle.F:
            if (state, '') not in transitions:                               
                transitions[state, ''] = {nfa_middle.q0} 
            else:
                transitions[state, ''].add(nfa_middle.q0)
            transitions[state, ''].add(state1) 
        # Totul este la fel, doar ca lipseste saltul catre final
        transitions[state0, ''] = {nfa_middle.q0}

        return NFA(alphabet, states, initial_state, transitions, accept_states)
    
@dataclass
class Question(Regex):
    middle: Regex

    def thompson(self) -> NFA[int]:
        nfa_middle = self.middle.thompson()

        nfa_middle = nfa_middle.remap_states(add_x_to_state(x = 2))
        
        state0, state1 = 0, 1

        alphabet = nfa_middle.S 
        states = nfa_middle.K | {state0} | {state1}
        initial_state = state0
        transitions = nfa_middle.d
        accept_states = {state1}

        for state in nfa_middle.F:
            if (state, '') not in transitions:                               
                transitions[state, ''] = {state1} 
            else:
                transitions[state, ''].add(state1)
            # Lipseste saltul catre q0-ul nfa-ului middle
        transitions[state0, ''] = {nfa_middle.q0, state1}

        return NFA(alphabet, states, initial_state, transitions, accept_states)


def tokenize(regex: str) -> List[str]:
    # Aceasta functie imparte stringul dat in simboluri utile. 
    # Totul este de dimensiune 1 mai putin cele cu \ si [0-9] [a-z] [A-Z]
    tokens = []
    i = 0
    while i < len(regex):
        if regex[i] in {'*', '+', '?', '|', '(', ')'}:
            tokens.append(regex[i])
        elif regex[i] == '\\':
            if regex[i + 1] in {'*', '+', '?', '|', '(', ')'}:
                tokens.append(regex[i:i+2])
                i += 1
            else:
                tokens.append(regex[i+1:i+2])
                i += 1
        elif regex[i] == '[':
            tokens.append(regex[i:i+5])
            i += 4
        elif regex[i] != ' ':
            tokens.append(regex[i])
        i += 1
    return tokens

def parse_regex(regex: str) -> Regex:
    tokens = tokenize(regex)
    return parse_sequence(tokens, 0)[0]

def parse_sequence(tokens: List[str], index: int) -> tuple[Regex, int]:
    # functia de parcurgere a unei secvente

    # Functie posibil utila pentru debug pe viitor, irelevanta acum
    if index >= len(tokens) or tokens[index] == ')':
        return Character(''), index

    regex, index = parse_single(tokens, index)

    while index < len(tokens) and tokens[index] != ')':
        if tokens[index] == '|':
            # Parsez stanga union-ului
            left_regex = regex
            # Sar peste token-ul '|' si parsez in continuare
            right_regex, index = parse_sequence(tokens, index + 1)
            # Creez un union intre regex-ul din stanga si din dreapta
            regex = Union(left_regex, right_regex)
        else:
            # Continui sa concatenez
            next_regex, index = parse_single(tokens, index)
            regex = Concat(regex, next_regex)
    return regex, index

def parse_single(tokens: List[str], index: int) -> tuple[Regex, int]:
    if tokens[index] == '(':
        # Paranteza deschisa inseamna inceputul unei secvente
        regex, index = parse_sequence(tokens, index + 1)
        if index >= len(tokens) or tokens[index] != ')':
            raise ValueError("Prea multe paranteze")
        index += 1
    else:
        # Creez un caracter din token-ul la care sunt
        regex = Character(tokens[index])
        index += 1

    # Daca simbolul care urmeaza este *, + sau ?, inseamna ca regexului de pana acum,
    # fie de dimeniune 1, fie de dimensiunea data de parse_sequence trebuie sa ii fie
    # aplicat Star, Plus sau Question
    if index < len(tokens) and tokens[index] in {'*', '+', '?'}:
        if tokens[index] == '*':
            regex = Star(regex)
        elif tokens[index] == '+':
            regex = Plus(regex)
        elif tokens[index] == '?':
            regex = Question(regex)
        index += 1
    return regex, index
