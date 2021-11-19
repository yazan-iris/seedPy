ByteBuffer
--------------------------
A utility class for placing numbers as bytes in an array in either ByteOrder.BIG_ENDIAN
or ByteOrder.LITTLE_ENDIAN.  You can use put(num) or byte_array[index], when putting numbers
the class takes care of advancing the index as space allows.

.. code-block::

    bb = ByteBuffer.allocate(capacity, byte_order=ByteOrder.LITTLE_ENDIAN)
    bb = ByteBuffer.wrap(bytes, byte_order=ByteOrder.LITTLE_ENDIAN)
or

.. code-block::

    bb = ByteBuffer.allocate(capacity, byte_order=ByteOrder.BIG_ENDIAN)
    bb = ByteBuffer.wrap(bytes, byte_order=ByteOrder.BIG_ENDIAN)

then you can do something like below.
.. code-block::

    bb = ByteBuffer.wrap(bytes, byte_order=ByteOrder.BIG_ENDIAN)
    bb.put_int(1)
    bb.put_int(2)
    bb.put_int(3)

    while bb.available() > 4:
        bb.put_int(int_val)

    bb = ByteBuffer.wrap(bb.to_bytes(), byte_order=ByteOrder.BIG_ENDIAN)
    for i in range(0, len(bb), 4):
        print(bb.get_int())

IntBuffer
--------------------------
A utility class wrapping ByteBuffer for storing integers.
.. code-block::

    ib = IntBuffer.allocate(150, ByteOrder.BIG_ENDIAN)
    arr = array.array("i", range(0, 150))
    for val in arr:
        ib.put(val)
        self.assertEqual(150, ib.capacity)

Steim Codec
--------------------------
Steim is authored by  Dr. Joseph Steim, and is a compression algorithm known for
use within the seismic community, especially in Seed.  It is a delta like compression with additional rules.
For more information Seed the Seed manual.

****
ControlSequence
****
A Control sequence describes how to unpack the number in accordance with the table below:

Steim1:
--------------------------
* control = 00 -> no data.
* control = 01 -> four ints that fits in 1 byte each: -127 <= num <= 128
    #. ex: 1, 1, 1, 1 [00000001 00000001 00000001 00000001]
* control = 10 -> two ints that fits in 2 bytes each: -32768 <= num <= 32767
    #. ex: 1, 1 [00000000 00000001 00000000 00000001]
* control = 11 -> one int, 4 bytes -2,147,483,648 <= num <= 2,147,483,647
    #. ex: 1 [00000000 00000000 00000000 00000001]

****
SteimBucket
****
The SteimBucket is the simplest unit of work.  Samples are added to the bucket
until the bucket is full, they way you use is illustrated below.  Make sure
you check if the sample was added or not, the put method return boolean indicating the
sample was added or not.  If you get back False then the bucket is full, any other error
will trigger SteimError.  When the bucket is full, the bucket is packed into a steim
number.  You get back tuple of the control value needed when unpacking and the number
of samples added in addition to Steim number, which is nothing more than the samples
packed together into one integer.  ex:
[3, 1, 2, 1] -> control=1, value=50397697, number_of_samples=4

.. code-block::

    bucket = Steim1Bucket()|Steim2Bucket()|Steim2Bucket()
    or
    bucket = SteimBucket.instance(EncodingFormat.STEIM_1,
                            EncodingFormat.STEIM_2,
                            EncodingFormat.STEIM_3)
    if not bucket.put(1):
        control, values, number_of_samples = bucket.pack()

****
SteimFrame
****
Steim frames are an arrays of 16 4-bytes long, this is how Steim internal structure is organized.
Each frame has a control value, used to unpack numbers when decompressing.
You have no access to the control value, it is generated for you and occupy the first slot
in the frame (array). The first frame, also known as the header, has 2 special
slots, located at index 1 and 2.  They contain the value of the forward and reverse integration constant,
the first sample and the last respectively.  They are used as (checksum).

.. code-block::

    frame = SteimFrame(byte_order=ByteOrder.LITTLE_ENDIAN|BIG_ENDIAN)
    arr = array.array("i", range(0, 150))
    bucket = Steim1Bucket()
    num = 0
    for sample in arr:
        if frame.is_full():
            break
        if not bucket.put(sample):
            control, values, number_of_samples = bucket.pack()
            num += number_of_samples
            if not frame.append(control, values):
                raise ValueError
            if not bucket.put(sample):
                raise ValueError