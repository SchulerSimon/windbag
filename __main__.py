import pathlib
import windbag.parser as parser

if __name__ == "__main__":
    p = parser.FileParser()
    p.parse(pathlib.Path(__file__).parent.joinpath("windbag", "corpus", "en").absolute())

    for x in range(10):
        print(p.random())

    # path = pathlib.Path(__file__).parent.joinpath("output.txt")
    # with open(path, "w") as f:
    #     for x in iter(p):
    #         f.write(x + "\n")