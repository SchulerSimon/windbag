import pathlib
from typing import OrderedDict
from windbag.tokenizer import Tokenizer
from windbag import parser

if __name__ == "__main__":
    p = parser.FileParser()
    index_dict = p.parse(
        pathlib.Path(__file__).parent.joinpath("windbag", "corpus", "en").absolute()
    )

    print(p.random())

    for x in iter(p):
        print(x)
        break

    print(p.random())

    for _ in range(20):
        print(p.random())

    # __date__ is matched first, so this is an ordered Dict
    regex_replace: OrderedDict = OrderedDict(
        {
            "__date__": r"\d{2}.\d{2}.\d{4}|\d{2}.\d{2}",
            "__time__": r"\d{1,2}:\d{2}",
            "__number__": r"-?\d+",
            "__math_operator__": r"\+|\-|\*|\/",
        }
    )
    t = Tokenizer(regex_replace=regex_replace)

    for intent, sentence_list in index_dict.items():
        t.fit_on_sentences(sentence_list)

    print(t.word_index)

    print(t.text_to_sequence("whats the time in Denmark"))
    print(t.text_to_sequence("what is 12 * 100"))
    print(t.text_to_sequence("asdfas dfasdf"))  # [1] = unknown
