
from Codec import EncodingFormat, Encoder
from Codec.Steim import Steim2Encoder, Steim3Encoder, Steim1Encoder
from buffer import ByteOrder


def get(encoding_format: EncodingFormat, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN) -> Encoder:
    if not encoding_format:
        raise ValueError
    elif encoding_format == EncodingFormat.STEIM_1:
        return Steim1Encoder(byte_order=byte_order)
    elif encoding_format == EncodingFormat.STEIM_2:
        return Steim2Encoder(byte_order=byte_order)
    elif encoding_format == EncodingFormat.STEIM_3:
        return Steim3Encoder(byte_order=byte_order)
    else:
        raise ValueError
