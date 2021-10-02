from Codec.errors import CodecError


class SteimError(CodecError):
    def __init__(self, fmt: str, *args, **kwargs):
        super().__init__(fmt.format(*args, **kwargs))