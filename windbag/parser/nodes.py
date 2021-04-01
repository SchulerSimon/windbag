import itertools
import random
from typing import Iterable
from .parser_error import ParserError
from .vocabular import *


class Node:
    def __init__(self) -> None:
        self.sep = "   |"
        self.nodes = []
        self.data = ""

    def __repr__(self) -> str:
        temp = "-> " + self.__class__.__name__ + f"({self.data})"
        for n in self.nodes:
            temp += f"\n" + str(n).replace("->", f"{self.sep}->")
        return temp


class Sentence(Node):
    def __init__(self) -> None:
        super().__init__()

    def __iter__(self) -> str:
        for y in itertools.product(*[iter(n) for n in self.nodes]):
            yield "".join(y)

    def random(self) -> str:
        return "".join([n.random() for n in self.nodes])

    def parse(self, _t: Iterable) -> Iterable:
        """parses an iterable of chars

        Args:
            _t (Iterable): chars to parse by this method

        Raises:
            ParserError: when _t contains a char that is not in the vocabulary defined by the grammer
            ParserError: when a closing bracket or | is found with no matching opening bracket
        """
        while (t := next(_t, None)) != None:
            if t not in vocabular:
                raise ParserError(_t, f"symbol '{t}' not allowed")
            child = None
            if t == " ":
                pass
            elif t in "{)]}|":
                raise ParserError(_t, f"unexpected '{t}'")
            elif t == "(":
                child = Optional()
                _t = child.parse(_t)
            elif t == "[":
                child = Choices()
                _t = child.parse(_t)
            else:
                child = Literal()
                _t = child.parse(itertools.chain([t], _t))
            if child != None:
                self.nodes.append(child)


class Literal(Node):
    def __init__(self) -> None:
        super().__init__()

    def __iter__(self) -> str:
        yield self.data + " "

    def random(self) -> str:
        return self.data + " "

    def parse(self, _t: Iterable) -> Iterable:
        """parses a Literal, stops parsing when one of the terminals is the next item

        Args:
            _t (Iterable): the iterable of chars to parse

        Raises:
            ParserError: when the given symbol is not allowed in a literal

        Returns:
            Iterable: iterable without the literal, containing the item that stopped parsing for literal
        """
        while (t := next(_t, None)) != None:
            if t not in vocabular:
                raise ParserError(_t, f"symbol '{t}' not allowed in literal")
            if t in terminals:
                self.data = self.data.strip()
                return itertools.chain([t], _t)
            else:
                self.data += t

        self.data = self.data.strip()
        return iter([])


class Optional(Node):
    def __init__(self) -> None:
        super().__init__()

    def __iter__(self) -> str:
        for y in itertools.chain(*[iter(n) for n in self.nodes]):
            yield "".join(y)
        yield ""

    def random(self) -> str:
        if bool(random.getrandbits(1)):
            return ""
        else:
            return "".join([n.random() for n in self.nodes])

    def parse(self, _t: Iterable) -> Iterable:
        """parses an Optional, stopps when the closing bracket ) is reached.

        Args:
            _t (Iterable): the iterable of chars to parse

        Raises:
            ParserError: if the next symbol is not allowed
            ParserError: if the next symbol is unexpected, (closing brackets except for ")")
            ParserError: if the iterable is empty and no closing bracket was found

        Returns:
            Iterable: the iterable of chars without the contents of this optional
        """
        while (t := next(_t, None)) != None:
            if t not in vocabular:
                raise ParserError(_t, f"symbol '{t}' not allowed")
            child = None
            if t == ")":
                return _t
            elif t in "{]}|":
                raise ParserError(_t, f"unexpected '{t}'")
            elif t == "(":
                child = Optional()
                _t = child.parse(_t)
            elif t == "[":
                child = Choices()
                _t = child.parse(_t)
            else:
                child = Literal()
                _t = child.parse(itertools.chain([t], _t))
            if child != None:
                self.nodes.append(child)
        raise ParserError(_t, "expected ')'")


class Choices(Node):
    def __init__(self) -> None:
        super().__init__()

    def __iter__(self) -> str:
        for y in itertools.chain(*[iter(n) for n in self.nodes]):
            yield "".join(y)

    def random(self) -> str:
        return random.choice(self.nodes).random()

    def parse(self, _t: Iterable) -> Iterable:
        """parses a Choices structure, denoted by [a|b]

        Args:
            _t (Iterable): iterable of chars to be parsed

        Raises:
            ParserError: if the next symbol is not allowed
            ParserError: if the next symbol is a closing bracket (except "]")
            ParserError: if the iterable is empty and no closing bracket was found

        Returns:
            Iterable: the iterable of chars without the contents of this Choices
        """
        while (t := next(_t, None)) != None:
            if t not in vocabular:
                raise ParserError(_t, f"symbol '{t}' not allowed")
            child = None
            if t == ")}":
                raise ParserError(_t, f"unexpected '{t}'")
            elif t == "]":
                return _t
            elif t == "|":
                continue
            else:
                child = Choice()
                _t = child.parse(itertools.chain([t], _t))
            if child != None:
                self.nodes.append(child)
        raise ParserError(_t, "expected ']'")


class Choice(Node):
    def __init__(self) -> None:
        super().__init__()

    def __iter__(self) -> str:
        for y in itertools.product(*[iter(n) for n in self.nodes]):
            yield "".join(y)

    def random(self) -> str:
        return "".join([n.random() for n in self.nodes])

    def parse(self, _t: Iterable) -> Iterable:
        """parses a choice (a choice is one of the options in choices)

        Args:
            _t (Iterable): iterable of chars to be parsed

        Raises:
            ParserError: if the next symbol is not allowed
            ParserError: if the next symbol is a closing bracket (except "]")

        Returns:
            Iterable: the iterable of chars without the contents of this Choices
        """
        while (t := next(_t, None)) != None:
            if t not in vocabular:
                raise ParserError(_t, f"symbol '{t}' not allowed")
            child = None
            if t == "{)}":
                raise ParserError(_t, f"unexpected '{t}'")
            elif t == "]":
                return itertools.chain([t], _t)
            elif t == "(":
                child = Optional()
                _t = child.parse(_t)
            elif t == "[":
                child = Choices()
                _t = child.parse(_t)
            elif t == "|":
                return itertools.chain([t], _t)
            else:
                child = Literal()
                _t = child.parse(itertools.chain([t], _t))
            if child != None:
                self.nodes.append(child)
