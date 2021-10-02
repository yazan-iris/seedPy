class CodecError(SyntaxError):
    """An error when parsing an XML document.

    In addition to its exception value, a ParseError contains
    two extra attributes:
        'code'     - the specific exception code
        'position' - the line and column of the error

    """

    def __init__(self, message: str):
        super().__init__(message)
    pass



