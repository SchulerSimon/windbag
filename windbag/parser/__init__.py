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
        """parses a string (_in), matches it with the given intent, and substitutes concepts.

        Args:
            _in (str): the string to parse (in the syntax defined by the readme)
            intent (str): the intent of this sentence
            concepts (dict, optional): a dictionary of concept:concept_string. Defaults to {}.
        """
        _in = _in.format(**concepts)
        node = Sentence()
        self._add(sentence=node, intent=intent)
        node.parse(iter(_in))

    def _add(self, sentence:Sentence, intent:str) -> None:
        """adds a parsed sentence object to this object

        Args:
            sentence (Sentence): the sentence to add to this parser
            intent (str): the intent this sentence should be matched to
        """
        if intent in self.sentences.keys():
            self.sentences[intent].append(sentence)
        else:
            self.sentences.update({intent:[sentence]})

    def __iter__(self) -> str:
        for intent, sentences in self.sentences.items():
            for s in sentences:
                for x in iter(s):
                    yield x.strip(), intent
    
    def random(self, intent:str="") -> str:
        """returns a randomly generated sentence form the parsed sentences

        Args:
            intent (str, optional): if given, only randomly generates form the given intent. Defaults to "".

        Returns:
            str: the str
        """
        if intent == "":
            intent = random.choice(list(self.sentences.keys()))
        temp = random.choice(self.sentences[intent]).random()
        return temp.strip(), intent

    def tree(self, intent:str="") -> None:
        """prints a tree of the sentences this object holds

        Args:
            intent (str, optional): if given, only prints a tree of the sentences for the given intent. Defaults to "".
        """
        if intent == "":
            for intent, sentences in self.sentences.items():
                for s in sentences:
                    print(s, "--" + intent)
        else:
            for s in self.sentences[intent]:
                print(s, "--" + intent)

class ListParser(Parser):
    def parse(self, _in: List, intent:str) -> None:
        """parses from a list of strings, each entry is parsed as new sentence

        Args:
            _in (List): list of strings that follow the syntax that was defined by the readme
            intent (str): the intent this sentence should be matched to

        Raises:
            ValueError: if the given param is not a list
            ValueError: if the contents of the list are not str
        """
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
        """parses all *.intent files in the given directory

        Args:
            _in (pathlib.Path): path to a directory that has *.intent files to parse

        Raises:
            ValueError: if the file is not properly formatted
        """
        _all = [_in.joinpath(f_name) for f_name in os.listdir(_in) if f_name.endswith(".intent")]
        for _path in _all:
            concepts: dict = {}
            with open(_path) as f:
                current_intent: str = ""
                for l in f.readlines():
                    l = l.strip().replace("\n", "")
                    if l == "":
                        continue
                    elif l.startswith("#"):
                        continue
                    elif l.startswith("__"):
                        name, concept = self._parse_concept(l)
                        concepts.update({name:concept})
                    elif l.startswith("--"):
                        current_intent = l[2:].strip()
                    else:
                        if current_intent == "":
                            raise ValueError("provide an intent befor sentences, you do this with --intent_name", f.name)
                        self._parse(l, current_intent, concepts)
        
    def _parse_concept(self, _line: str) -> Tuple[str, str]:
        """parses a concept from a line that starts with __

        Args:
            _line (str): the line of the *.intent file that starts with __

        Raises:
            ParserError: if the line is too short
            ParserError: if whitespaces are in the concept name

        Returns:
            Tuple[str, str]: name of the concept, contents of the concept
        """
        _line = _line.split("=")
        if len(_line) != 2:
            raise ParserError(None, f"error while parsing concept: {str(_line)}")
        name = _line[0].strip()[2:]
        concept = _line[1].strip()
        if " " in name:
            raise ParserError(None, f"whitespaces are not allowed in concept names: {name}")
        return name, concept


