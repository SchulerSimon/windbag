class ParserError(Exception):
    def __init__(self, _t=None, *args: object) -> None:
        if _t is None:
            super().__init__(*args)
        else:
            self.remaining_input = ""
            for t in _t:
                self.remaining_input += t
            if len(self.remaining_input) > 47:
                super().__init__(
                    args[0] + f". Remaining input:'{self.remaining_input[:47]}...'"
                )
            else:
                super().__init__(args[0] + f". Remaining input:'{self.remaining_input}'")
