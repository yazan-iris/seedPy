import os
from builtins import open as bltn_open


class SeedError(Exception):
    """Base exception."""
    pass


class ExtractError(SeedError):
    """General exception for extract errors."""
    pass


class ReadError(SeedError):
    """Exception for unreadable tar archives."""
    pass


class CompressionError(SeedError):
    """Exception for unavailable compression methods."""
    pass


class SeedFile(object):
    error_level = 1  # If 0, fatal errors only appear in debug

    # messages (if debug >= 0). If > 0, errors
    # are passed to the caller as exceptions.

    def __init__(self, name=None, mode="r", fileobj=None, format=None,
                 tarinfo=None, dereference=None, ignore_zeros=None, encoding=None,
                 errors="surrogateescape", pax_headers=None, debug=None,
                 error_level=None, copybufsize=None):
        """Open an (uncompressed) tar archive `name'. `mode' is either 'r' to
                   read from an existing archive, 'a' to append data to an existing
                   file or 'w' to create a new file overwriting an existing one. `mode'
                   defaults to 'r'.
                   If `fileobj' is given, it is used for reading or writing data. If it
                   can be determined, `mode' is overridden by `fileobj's mode.
                   `fileobj' is not closed, when TarFile is closed.
                """
        modes = {"r": "rb", "a": "r+b", "w": "wb", "x": "xb"}
        if mode not in modes:
            raise ValueError("mode must be 'r', 'a', 'w' or 'x'")
        self.mode = mode
        self._mode = modes[mode]

        if not fileobj:
            if self.mode == "a" and not os.path.exists(name):
                # Create nonexistent files in append mode.
                self.mode = "w"
                self._mode = "wb"
            fileobj = bltn_open(name, self._mode)
            self._extfileobj = False
        else:
            if (name is None and hasattr(fileobj, "name") and
                    isinstance(fileobj.name, (str, bytes))):
                name = fileobj.name
            if hasattr(fileobj, "mode"):
                self._mode = fileobj.mode
            self._extfileobj = True
        self.name = os.path.abspath(name) if name else None
        self.fileobj = fileobj

        # Init attributes.
        if format is not None:
            self.format = format
        if tarinfo is not None:
            self.tarinfo = tarinfo
        if dereference is not None:
            self.dereference = dereference
        if ignore_zeros is not None:
            self.ignore_zeros = ignore_zeros
        if encoding is not None:
            self.encoding = encoding
        self.errors = errors

        if pax_headers is not None and self.format == PAX_FORMAT:
            self.pax_headers = pax_headers
        else:
            self.pax_headers = {}

        if debug is not None:
            self.debug = debug
        if error_level is not None:
            self.error_level = error_level

        # Init datastructures.
        self.copybufsize = copybufsize
        self.closed = False
        self.members = []  # list of members as TarInfo objects
        self._loaded = False  # flag if all members have been read
        self.offset = self.fileobj.tell()
        # current position in the archive file
        self.inodes = {}  # dictionary caching the inodes of
        # archive members already added

        try:
            if self.mode == "r":
                self.firstmember = None
                self.firstmember = self.next()

            if self.mode == "a":
                # Move to the end of the archive,
                # before the first empty block.
                while True:
                    self.fileobj.seek(self.offset)
                    try:
                        tarinfo = self.tarinfo.fromtarfile(self)
                        self.members.append(tarinfo)
                    except EOFHeaderError:
                        self.fileobj.seek(self.offset)
                        break
                    except HeaderError as e:
                        raise ReadError(str(e))

            if self.mode in ("a", "w", "x"):
                self._loaded = True

                if self.pax_headers:
                    buf = self.tarinfo.create_pax_global_header(self.pax_headers.copy())
                    self.fileobj.write(buf)
                    self.offset += len(buf)
        except:
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True
            raise

    def __del__(self):
        if hasattr(self, "closed") and not self.closed:
            self.close()

    def close(self):
        """Close the _Stream object. No operation should be
           done on it afterwards.
        """
        if self.closed:
            return

        self.closed = True
        try:
            if self.mode == "w" and self.comptype != "tar":
                self.buf += self.cmp.flush()

            if self.mode == "w" and self.buf:
                self.fileobj.write(self.buf)
                self.buf = b""
                if self.comptype == "gz":
                    self.fileobj.write(struct.pack("<L", self.crc))
                    self.fileobj.write(struct.pack("<L", self.pos & 0xffffFFFF))
        finally:
            if not self._extfileobj:
                self.fileobj.close()

    def tell(self):
        """Return the stream's file pointer position.
        """
        return self.pos

    def seek(self, pos=0):
        """Set the stream's file pointer to pos. Negative seeking
           is forbidden.
        """
        if pos - self.pos >= 0:
            blocks, remainder = divmod(pos - self.pos, self.bufsize)
            for i in range(blocks):
                self.read(self.bufsize)
            self.read(remainder)
        else:
            raise StreamError("seeking backwards is not allowed")
        return self.pos


    @classmethod
    def open(cls, name=None, mode="r", fileobj=None, **kwargs):
        """Open a seed file for reading, writing or appending. Return
                   an appropriate SeedFile class.

                   mode:
                   'r' or 'r:*' open for reading with transparent compression
                   'r:'         open for reading exclusively uncompressed
                   'r:gz'       open for reading with gzip compression
                   'r:bz2'      open for reading with bzip2 compression
                   'r:xz'       open for reading with lzma compression
                   'a' or 'a:'  open for appending, creating the file if necessary
                   'w' or 'w:'  open for writing without compression
                   'w:gz'       open for writing with gzip compression
                   'w:bz2'      open for writing with bzip2 compression
                   'w:xz'       open for writing with lzma compression

                   'x' or 'x:'  create a tarfile exclusively without compression, raise
                                an exception if the file is already created
                   'x:gz'       create a gzip compressed tarfile, raise an exception
                                if the file is already created
                   'x:bz2'      create a bzip2 compressed tarfile, raise an exception
                                if the file is already created
                   'x:xz'       create an lzma compressed tarfile, raise an exception
                                if the file is already created

                   'r|*'        open a stream of tar blocks with transparent compression
                   'r|'         open an uncompressed stream of tar blocks for reading
                   'r|gz'       open a gzip compressed stream of tar blocks
                   'r|bz2'      open a bzip2 compressed stream of tar blocks
                   'r|xz'       open an lzma compressed stream of tar blocks
                   'w|'         open an uncompressed stream for writing
                   'w|gz'       open a gzip compressed stream for writing
                   'w|bz2'      open a bzip2 compressed stream for writing
                   'w|xz'       open an lzma compressed stream for writing
                """

        if not name and not fileobj:
            raise ValueError("nothing to open")

        if mode in ("r", "r:*"):
            # Find out which *open() is appropriate for opening the file.
            def not_compressed(comptype):
                return cls.OPEN_METH[comptype] == 'taropen'

            for comptype in sorted(cls.OPEN_METH, key=not_compressed):
                func = getattr(cls, cls.OPEN_METH[comptype])
                if fileobj is not None:
                    saved_pos = fileobj.tell()
                try:
                    return func(name, "r", fileobj, **kwargs)
                except (ReadError, CompressionError):
                    if fileobj is not None:
                        fileobj.seek(saved_pos)
                    continue
            raise ReadError("file could not be opened successfully")

        elif ":" in mode:
            filemode, comptype = mode.split(":", 1)
            filemode = filemode or "r"
            comptype = comptype or "tar"

            # Select the *open() function according to
            # given compression.
            if comptype in cls.OPEN_METH:
                func = getattr(cls, cls.OPEN_METH[comptype])
            else:
                raise CompressionError("unknown compression type %r" % comptype)
            return func(name, filemode, fileobj, **kwargs)

        elif "|" in mode:
            filemode, comptype = mode.split("|", 1)
            filemode = filemode or "r"
            comptype = comptype or "tar"

            if filemode not in ("r", "w"):
                raise ValueError("mode must be 'r' or 'w'")

            stream = _Stream(name, filemode, comptype, fileobj, bufsize)
            try:
                t = cls(name, filemode, stream, **kwargs)
            except:
                stream.close()
                raise
            t._extfileobj = False
            return t

        elif mode in ("a", "w", "x"):
            return cls.seed_open(name, mode, fileobj, **kwargs)

        raise ValueError("undiscernible mode")

    @classmethod
    def seed_open(cls, name, mode="r", fileobj=None, **kwargs):
        """Open uncompressed tar archive name for reading or writing.
        """
        if mode not in ("r", "a", "w", "x"):
            raise ValueError("mode must be 'r', 'a', 'w' or 'x'")
        return cls(name, mode, fileobj, **kwargs)


def is_seed_file(name):
    """Return True if name points to a tar archive that we
       are able to handle, else return False.

       'name' should be a string, file, or file-like object.
    """
    try:
        if hasattr(name, "read"):
            t = open(fileobj=name)
        else:
            t = open(name)
        t.close()
        return True
    except SeedError:
        return False


open = SeedFile.open
