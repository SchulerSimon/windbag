# windbag
#### (slang) - an exhaustively talkative person; person who talks too much

windbag is a language that allowes you to script lots of example input sentences. The goal is to generate training-sets for intent recognition. It comes with a parser and its own file-format. Have a look at the [corpus](windbag/corpus/) if you are interested in writingn your own scripts

<details>
<summary>Motivation</summary>
I was looking into creating datasets to train a NN to extract the **intent** of given sentences. I was trying to create large sets of sentences that reflect possible ways to issue a command or ask a question. For example: "Show me a black and white picture of a cat", "give pictures of Londons east", "close the door in the kitchen", "switch off the tv" and many more. 

Ill be using [context-free grammar (CFG)](https://en.wikipedia.org/wiki/Context-free_grammar)s and [parser](https://en.wikipedia.org/wiki/Parsing#Parser)s. Great way for me to refresh my knowledge from university.

## example
It would be nice to have a parser that accepts script-like sentences like:
```
[show|give] (me) [a ([black and white|color|winter|summer]) picture|([black and white|color|winter|summer]) pictures] of [[a cat|cats]|Berlin (in the summer)|[London|Londons [downtown|city center|east]]]
```
And what I want as a result is a list of ALL possible sentences from the script-like input. 
Id like to have choices of a or b: `[a|b]` 
And optionals that evaluate to c or nothing: `(c)`

Another feature that I want, is to reuse some of the already given concepts: `{concept}`. 
For example, if I dont want to retype the concept of picture_type (`[black and white|color|winter|summer]`), it would be nice to have a syntax that is able to parse these concepts and then expand upon these aswell:
```
__picture_type = [black and white|color|winter|summer]

--pictures
[show|give] (me) [a ({picture_type}) picture|({picture_type}) pictures] of [[a cat|cats]|Berlin (in the summer)|[London|Londons [downtown|city center|east]]]
```
The above should be able to be parsed by the Parser.

## *.intent files
Just because I can, I descided to "invent" my own file-type that has the ending `.intent` and that is structured as follows:

`internet_search.intent`
```
# this is a comment (comments are denoted by #)

# first we define concepts (concepts are denoted by __)
__place = [amazon|wikipedia|google|youtube|spottify|facebook|reddit|netflix|twitch|twitter|instagram]
__topic = [oranges|vacuums|lets plays|videos|streams|films|posts|tweets|pictures|songs|music]

# then we give a name for the intent (intent names are denoted by --)
--internet_search

# and then we give example sentences in the script-like format
[could|would] you ([please|pls]) [search for|look up] {topic} [in|at] {place}
what dose {place} say [to|about] {topic}
([please|pls]) look up {topic} [in|at] {place}
([please|pls]) show me {topic} [in|at] {place}
```

please keep in mind that the goal is **not to produce sentences that are super duper correct**. The goal is to have a tool to easily generate lots of examples of what users might input into a chatbot/helperbot.
</details>

## usage
### parsing lists of sentences
```python
from windbag import parser
p = parser.ListParser()
p.parse(["drive to the [left|right]", "why so (terribly) serious"], intent="some_intent_name")
# yields one of the possible sentences
print(p.random()) 
```

### parsing from files in a directory
```python
from windbag import parser
p = parser.FileParser()
# searches for all *.intent files in that directory
p.parse(pathlib.Path(__file__).parent.joinpath("windbag", "corpus", "en").absolute())
# yields one of the possible sentences
print(p.random()) 
```

### iterating over all possible sentences
```python
from windbag import parser
p = parser.FileParser()
p.parse(pathlib.Path(__file__).parent.joinpath("windbag", "corpus", "en").absolute())
# yields ALL the sentences (carefull, might me a LOT)
for output in iter(p): 
  print(output) 
```

### show the tree of parsed sentences
```python
from windbag import parser
p = parser.ListParser()
p.parse(["drive to the [left|right]", "why so (terribly) serious"], intent="some_intent_name")
# prints a tree like structure of all the parsed sentences
p.tree()
```
```
-> Sentence()
   |-> Literal(drive to the)
   |-> Choices()
   |   |-> Choice()
   |   |   |-> Literal(left)
   |   |-> Choice()
   |   |   |-> Literal(right) --some_intent_name
-> Sentence()
   |-> Literal(why so)
   |-> Optional()
   |   |-> Literal(terribly)
   |-> Literal(serious) --some_intent_name
```

## syntax
Now it is probably a good idea to define the syntax a little better. 

Lets define some **operators**:

### optionals `(a)`
`(a)` means optional, this should evaluate into exactly two sentences/subsentences. One contains a, the other dosent. 
```
(please) open the door 
-> open the door
-> please open the door
``` 

### choices `[a|b]`
`[a|b]` means there is a choice of a and b. In this example it should evalueate into exactly two sentences/subsentences
```
drive to the [left|right]
-> drive to the left
-> drive to the right
```

### concepts `{type}`
`{weather}` means that we want to reuse the concept of weather. This should evaluate into exactly one sentence/subsentence that contains weather
```
__weather = [hot|cold|mild|sunny|cloudy|freezing]

today is a {weather} day
-> today is a [hot|cold|mild|sunny|cloudy|freezing] day
``` 
They start with two underscores. They also allow the syntax of optionals and choices.


## requirements of the parser
**Nesting should always be possible**
```
x (a (b) c)
-> x 
-> x a c
-> x a b c
```
**Nesting choices dosent do much, but it should work non the less**
```
x [a|[b|c]]
-> x a
-> x b
-> x c
```
**The same rules apply if concepts, optionals and choices are nested**
```
__animal = [frog|cat|dog]
__city = [Berlin|London|Paris]
__topics = [statistics|pictures|links]

Show me [{animal}|{city}] {topic}
```

**Whitespaces are somewhat complicated.** For now I just ommited the concept of spaces, but for sentences that is something that needs to be considered. **They need to be preserved** when not direcly next to one of the syntax-operators `()[]|{}`
```
what [day|month|year] is it
-> whatdayis it # obviously wrong
-> what day is it # more like it

why ([so serious|are you happy])
-> why soserious # obviously wrong
-> why so serious # more like it
-> why areyouhappy # obviously wrong
-> why are you happy # more like it
```

## wrong syntax
The next thing to look at is when the parser should not parse input. 

**Opening brackets should always be closed**
```
[a|b(]
-> expected ) at [a|b(]
                    ~~~
```

**Whitespace/empty choices/optionals should raise a parser error**
```
[a|(b)|c]
-> expected choice at [a|(b)|c]
                        ~~~~~

[a| |c]
-> expected choice at [a| |c]
                        ~~~

a ( )
-> expected optional at a ( )
                          ~~~
```

## definition of the grammer
<details>
<summary>grammer</summary>

if you never heard of Context-free grammars, have a look at the [wikipedia article](https://en.wikipedia.org/wiki/Context-free_grammar)


In this case, 
**G** = (**V**, **T**, **P**, *S*)
with 

**T** = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "!", """, "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", " ", "-", ".", "/", ":", ";", "<", "=", ">", "?", "@", "[", "]", "\", "^", "_", "`", "{", "}", "|", "~"}

**V** = {"(", ")", "[", "]", "{", "}"}

**P** = {
1: *S* -> *S* *S*,
2: *S* -> (*S*),
3: *S* -> [*K*],
4: *S* -> {*S*},
5: *S* -> *any number of symbols of* **T**,
6: *K* -> *S* | *S*
}

I'll try my best to explain this. Lets say we want to create a word that is represented by this grammar. We start with *S* and then just continue choosing a relation in **P** that can be used until we have no S left. 

I have put the number of the relation (the ones in **P**) over it to make it easier to understand.

```
  1      5         2           1             5              5
S -> S S -> show S -> show S S -> show (S) S -> show (me) S -> show (me) a picture
```
First we use the first relation to go from "*S*" to "*S* *S*", then we use 4th relation to go from "*S* *S*" to "show *S*", then we use the second relation to go from "show *S*" to "show *S* *S*" and so forth.  

</details>

## implementation
Because the grammar **G** is an [LL(k)](https://en.wikipedia.org/wiki/LL_parser) grammer, we can use a predictive LL-Parser to parse the input. I chose to use a recursive-predictive parser. You can take a look at [parser.py](sentence_expander/parser.py)

Another challange was to prevent huge amounts of memory usage. Especially when you work with sentences that are long and have lots of choices etc. it might become a problem to store everything in memory. So to account for that I implemented all classes as iterators. So we dont need to store all the output, but can rather generated it when needed.

I also wanted to have a random function, that spits out a randomly generated sentence (of the possible ones). 

## performance

<details>
<summary>performance</summary>

### parsing
For parsing the runtime should be in ***O(n)*** with n beeing the number of characters in the input.

### generating sentences
For generating sentences the runtime should be ***O(log(k))*** (same as binary search tree traversal) with k beeing the number of operators in the given sentence. 

### memory usage
Due to the fact that sentences are represented by a tree-like structure internally, the memory usage should be around ***O(k)*** with k beeing the number of operators in the input. This is not the case when you store all the possible outputs of the parsed sentence. That should be more like ***O(n^K)*** with n beeing the number of characters and k beeing the number of operators in the input.

</details>

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Id be really happy if you take the time to just write one sentence in the already existing [corpus](sentence_expander/corpus/) of this project 

## License

This work is dual-licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.html) and [GPL 2.0](https://spdx.org/licenses/GPL-2.0-or-later.html) (or any later version).
You can choose between one of them if you use this work.

`SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later`