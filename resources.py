import sys
import zlib
import base64
import pickle
import pathlib
import contextlib
import pickletools


class Resource:

    """Manager for resources that would normally be held externally."""

    MODE = "clipboard"  # either "clipboard" or ".txt file", determines how you receive your new data strings
    WIDTH = 119
    __CACHE = None
    DATA = b''

    @classmethod
    def add(cls, *paths):
        """Include paths in the pre-generated DATA block up above."""
        if cls.DATA != b'':
            cls.__preload()
        cls.__generate_data(paths, cls.__CACHE.copy())

    @classmethod
    def remove(cls, *paths):
        """Remove paths from the pre-generated DATA block up above."""
        cls.__preload()
        cls.__remove_data(paths, cls.__CACHE.copy())

    @classmethod
    def __generate_data(cls, paths, buffer):
        """Load paths into buffer and output DATA code for the class."""
        for path in map(pathlib.Path, paths):
            if not path.is_file():
                raise ValueError('{!r} is not a file'.format(path))
            key = path.name
            if key in buffer:
                raise KeyError('{!r} has already been included'.format(key))
            with path.open('rb') as file:
                buffer[key] = file.read()
        pickled = pickle.dumps(buffer, pickle.HIGHEST_PROTOCOL)
        optimized = pickletools.optimize(pickled)
        compressed = zlib.compress(optimized, zlib.Z_BEST_COMPRESSION)
        encoded = base64.b85encode(compressed)
        cls.__output_data(encoded)

    @classmethod
    def __remove_data(cls, paths, buffer):
        """Remove paths from buffer and output DATA code for the class."""
        for key in paths:
            if key not in buffer:
                raise KeyError('{!r} is not included'.format(key))
            with pathlib.Path(key).open('wb') as file:
                file.write(buffer[key])
            del buffer[key]
        pickled = pickle.dumps(buffer, pickle.HIGHEST_PROTOCOL)
        optimized = pickletools.optimize(pickled)
        compressed = zlib.compress(optimized, zlib.Z_BEST_COMPRESSION)
        encoded = base64.b85encode(compressed)
        cls.__output_data(encoded)

    @classmethod
    def __output_data(cls, encoded):
        if cls.MODE == ".txt file":
            with open('resource_data.txt', 'w') as f:
                f.write("    DATA = b'''")
                for offset in range(0, len(encoded), cls.WIDTH):
                    f.write("\\\n" + encoded[
                        slice(offset, offset + cls.WIDTH)].decode('ascii'))
                f.write("'''")
            print('Saved new DATA block to resource_data.txt!')
        elif cls.MODE == "clipboard":
            out = "    DATA = b'''"
            for offset in range(0, len(encoded), cls.WIDTH):
                out += "\\\n" + encoded[
                    slice(offset, offset + cls.WIDTH)].decode('ascii')
            out += "'''"
            import pyperclip
            pyperclip.copy(out)
            print('Copied new DATA block to clipboard!')

    @staticmethod
    def __print(line):
        """Provides alternative printing interface for simplicity."""
        sys.stdout.write(line)
        sys.stdout.flush()

    @classmethod
    def query(cls):
        """Query all items in resource manager."""
        cls.__preload()
        for key in cls.__CACHE:
            cls.__print(key + '\n')

    @classmethod
    @contextlib.contextmanager
    def load(cls, name, delete=True):
        """Dynamically loads resources and makes them usable while needed."""
        cls.__preload()
        if name not in cls.__CACHE:
            raise KeyError('{!r} cannot be found'.format(name))
        path = pathlib.Path(name)
        with path.open('wb') as file:
            file.write(cls.__CACHE[name])
        yield path
        if delete:
            path.unlink()

    @classmethod
    def __preload(cls):
        """Warm up the cache if it does not exist in a ready state yet."""
        if cls.__CACHE is None:
            decoded = base64.b85decode(cls.DATA)
            decompressed = zlib.decompress(decoded)
            cls.__CACHE = pickle.loads(decompressed)

    def __init__(self):
        """Creates an error explaining class was used improperly."""
        raise NotImplementedError('class was not designed for instantiation')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'query':
            Resource.query()
        else:
            print('Invalid argument!')
    elif len(sys.argv) == 3:
        file = sys.argv[2]
        if sys.argv[1] == 'add':
            Resource.add(file)
        elif sys.argv[1] == 'remove':
            Resource.remove(file)
        else:
            print('Invalid argument!')
    else:
        print('Specify add / remove / query!')
