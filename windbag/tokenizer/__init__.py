import re

from typing import Dict, List, Pattern
from windbag.parser.nodes import Literal, Node, Sentence


class Tokenizer:
    def __init__(
        self, unknown: str = "__unk__", regex_replace: Dict[str, str] = {}
    ) -> None:
        self.word_index: Dict[str, int] = {}
        self.counter = 2
        self.unknown = unknown
        self.word_index[unknown] = 1

        self.regex_replace: Dict[str, Pattern] = regex_replace
        for replace, regex in regex_replace.items():
            regex_replace[replace] = re.compile(regex)

    def fit_on_sentences(self, sentences: List[Sentence]) -> Dict[str, int]:
        """fits this tokenizer on a given list of sentences

        Args:
            sentences (List[Sentence]): a list of windbag.parser.nodes.Sentence

        Returns:
            Dict[str, int]: token:number
        """
        for sentence in sentences:
            self.fit_on_sentence(sentence)

    def fit_on_sentence(self, sentence: Sentence) -> Dict[str, int]:
        """fits this tokenizer on a given sentence

        Args:
            sentence (Sentence): windbag.parser.nodes.Sentence

        Returns:
            Dict[str, int]: token:number
        """
        for node in sentence.nodes:
            self.fit_on_node(node)

    def fit_on_node(self, node: Node) -> None:
        """fits this tokeinzer on a node

        Args:
            node (Node): windbag.parser.nodes.Node
        """
        if isinstance(node, Literal):
            self._add(node.data)
        else:
            for n in node.nodes:
                self.fit_on_node(n)

    def _add(self, data: str) -> None:
        words = data.split(" ")
        for w in words:
            w = self._replace(w)
            if w in self.word_index.keys():
                pass
            else:
                self.word_index[w] = self.counter
                self.counter += 1

    def _replace(self, word: str) -> str:
        for replace, regex in self.regex_replace.items():
            match = regex.match(word)
            if match is not None:
                return replace
        return word

    def text_to_sequence(self, text: str) -> List[int]:
        """takes a " " separated text and returns a list of tokens for that sentence

        Args:
            text (str): a text

        Returns:
            List[int]: list of tokens (int)
        """
        words = text.split(" ")
        temp = []
        for w in words:
            w = self._replace(w)
            try:
                temp.append(self.word_index[w])
            except KeyError:
                temp.append(self.word_index[self.unknown])
        return temp
