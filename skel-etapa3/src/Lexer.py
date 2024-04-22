from .Regex import *
from .DFA import DFA

class Lexer:
    nfa_list: list[tuple[str, NFA]]
    dfa_list: list[tuple[str, DFA]]

    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.nfa_list = []
        self.dfa_list = []
        # Metoda pe care am ales-o este sa construiesc o lista de dfa-uri
        # si sa verific daca un cuvant este acceptat in oricare dintre dfa-uri
        counter = 1
        for token, regex in spec:
            nfa = parse_regex(regex).thompson().remap_states(add_x_to_state(x = counter))
            self.nfa_list.append((token, nfa))
            self.dfa_list.append((token, nfa.subset_construction()))
            counter = counter + len(nfa.K)
        

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        token_list: list[tuple[str, str]] 
        token_element: tuple[str, str]
        token_list = []
        
        original_word = word
        
        # Pentru a ma deplasa in cuvant
        counter = 1
        # Pentru a retine numarul de caractere care este acceptat
        token_counter = 1
        # Pentru a calcula numarul de caractere la erori
        character_counter = 0

        while word:
            token_element = ()
            reached_eof = False
            while counter <= len(word):
                # iau cate counter litere din cuvant si verific daca sunt acceptate in oricare
                # dintre dfa-uri
                partial_word = word[:counter]
                for (token, dfa) in self.dfa_list:
                    if (dfa.accept(partial_word)):
                        token_element = (token, partial_word)
                        token_counter = counter
                        break

                counter += 1 

            if token_element == ():

                word_counter = 0
                reached_eof = False
                for (token, dfa) in self.dfa_list:
                    if dfa.reach_sink_state(word) == -1:
                        reached_eof = True
                    if dfa.reach_sink_state(word) != -1 and word_counter < dfa.reach_sink_state(word):
                        word_counter = dfa.reach_sink_state(word)

                word_copy = original_word[:character_counter + word_counter]
                line_counter = word_copy.count('\n')
                character_counter = character_counter + word_counter - (word_copy.rfind('\n') + 1)

                if reached_eof:
                    token_element = ("", "No viable alternative at character EOF, line " + str(line_counter))
                else:
                    print(len(word))
                    token_element = ("", "No viable alternative at character " + str(character_counter) + ", line " + str(line_counter))
                token_list.clear()
                token_list.append(token_element)
                return token_list

            else:
                # adaugarea token-urilor in lista care trebuie returnata de functie
                character_counter += token_counter
                token_list.append(token_element)
                word = word[token_counter:]
                counter = 1
                token_counter = 1
        return token_list