import os
import random
import pathlib
from typing import Dict, List, Tuple

from .parser_error import ParserError
from .nodes import Sentence

class Parser:
    def __init__(self) -> None:
        self.sentences:Dict[str, List[Sentence]] = {}

    def _parse(self, _in: str, intent:str, concepts: dict = {}) -> None:
        _in = _in.format(**concepts)
        node = Sentence()
        self._add(sentence=node, intent=intent)
        node.parse(iter(_in))

    def _add(self, sentence, intent) -> None:
        if intent in self.sentences.keys():
            self.sentences[intent].append(sentence)
        else:
            self.sentences.update({intent:[sentence]})

    def __iter__(self) -> str:
        for intent, sentences in self.sentences.items():
            for s in sentences:
                for x in iter(s):
                    yield x #+ " --" + intent
    
    def random(self, intent:str="", print_intent:bool=False) -> str:
        if intent == "":
            intent = random.choice(list(self.sentences.keys()))
        temp = random.choice(self.sentences[intent]).random() 
        if print_intent:
            temp += "--" + intent
        return temp

    def tree(self, intent:str="") -> None:
        if intent == "":
            for intent, sentences in self.sentences.items():
                for s in sentences:
                    print(s, "--" + intent)
        else:
            for s in self.sentences[intent]:
                print(s, "--" + intent)

class ListParser(Parser):
    def parse(self, _in: List, intent:str) -> None:
        if isinstance(_in, list):
            for s in _in:
                if not isinstance(s, str):
                    raise ValueError(s, "is not of type string")
                self._parse(s, intent)
        else:
            raise ValueError("provide a list of strings")

class FileParser(Parser):
    def __init__(self) -> None:
        super().__init__()
        self.concepts = {}

    def parse(self, _in: pathlib.Path):
        _all = [_in.joinpath(f_name) for f_name in os.listdir(_in) if f_name.endswith(".intent")]
        for _path in _all:
            with open(_path) as f:
                current_intent = ""
                for l in f.readlines():
                    l = l.strip().replace("\n", "")
                    if l == "":
                        continue
                    elif l.startswith("#"):
                        continue
                    elif l.startswith("__"):
                        name, concept = self.parse_concept(l)
                        self.concepts.update({name:concept})
                    elif l.startswith("--"):
                        current_intent = l[2:].strip()
                    else:
                        if current_intent == "":
                            raise ValueError("provide an intent befor sentences, you do this with --intent_name", f.name)
                        self._parse(l, current_intent, self.concepts)
        
    def parse_concept(self, _line: str) -> Tuple[str, str]:
        _line = _line.split("=")
        if len(_line) != 2:
            raise ParserError(None, f"error while parsing concept: {str(_line)}")
        name = _line[0].strip()[2:]
        concept = _line[1].strip()
        if " " in name:
            raise ParserError(None, f"whitespaces are not allowed in concept names: {name}")
        return name, concept


