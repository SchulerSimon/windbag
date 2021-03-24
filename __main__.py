import pathlib
from windbag import parser

if __name__ == "__main__":
    p = parser.FileParser()
    p.parse(pathlib.Path(__file__).parent.joinpath("windbag", "corpus", "en").absolute())

    print(p.random())

    for x in iter(p):
        print(x)
        break

    print(p.random("internet_search"))


    for _ in range(20):
        print(p.random())
    # path = pathlib.Path(__file__).parent.joinpath("output.txt")
    # with open(path, "w") as f:
    #     for x in iter(p):
    #         f.write(x + "\n")