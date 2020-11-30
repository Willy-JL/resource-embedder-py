import sys
import zlib
import base64
import pickle
import pathlib
import contextlib
import pickletools


class Resource:

    """Manager for resources that would normally be held externally."""

    MODE = "auto update"  # options: "auto update" or "clipboard" or ".txt file", determines how you receive your new data strings
    __CACHE = {}
    DATA = {}

    @classmethod
    def add(cls, path):
        """Include paths in the DATA line up above."""
        if path in cls.DATA:
            print("Already in data!")
        else:
            cls.__generate_data(path)

    @classmethod
    def remove(cls, path):
        """Remove paths from the DATA line up above."""
        if path not in cls.DATA:
            print("Item not in data!")
        else:
            cls.__remove_data(path)

    @classmethod
    def extract(cls, path):
        """Extract paths from the DATA line up above."""
        if path not in cls.DATA:
            print("Item not in data!")
        else:
            cls.__remove_data(path, remove=False)

    @classmethod
    def __generate_data(cls, name):
        """Encode item and output new DATA line for the class."""
        path = pathlib.Path(name)
        if not path.is_file():
            raise ValueError('{!r} is not a file'.format(name))
        key = name
        if key in cls.DATA:
            raise KeyError('{!r} has already been included'.format(key))
        with path.open('rb') as file:
            content = file.read()
        pickled = pickle.dumps({key: content}, pickle.HIGHEST_PROTOCOL)
        optimized = pickletools.optimize(pickled)
        compressed = zlib.compress(optimized, zlib.Z_BEST_COMPRESSION)
        encoded = base64.b85encode(compressed)
        cls.DATA[key] = encoded
        cls.__output_data()

    @classmethod
    def __remove_data(cls, path, remove=True):
        """Remove item and output new DATA line for the class."""
        key = path
        if key not in cls.DATA:
            raise KeyError('{!r} is not included'.format(key))
        with pathlib.Path(key).open('wb') as file:
            if key not in cls.__CACHE:
                cls.__preload(key)
            file.write(cls.__CACHE[key][key])
        if remove:
            del cls.DATA[key]
            cls.__output_data()
        else:
            print(f'Extracted {path}!')

    @classmethod
    def __output_data(cls):
        """Output DATA dict line."""
        out = "    DATA"
        out += " = {"
        for i, key in enumerate(cls.DATA):
            out += f"'{key}': {cls.DATA[key]}{', ' if i != len(cls.DATA)-1 else ''}"
        out += "}\n"
        if cls.MODE == ".txt file":
            with open('resource_data.txt', 'w') as f:
                f.write(f"\n{out}")
            print('Saved new DATA line to resource_data.txt! Replace the existing DATA line in ' + __file__[__file__.rfind("\\" if sys.platform == "win32" else "/")+1:] + '!')
        elif cls.MODE == "clipboard":
            import pyperclip
            pyperclip.copy(f"\n{out}")
            print(f'Copied new DATA line to clipboard! Replace the existing DATA line in ' + __file__[__file__.rfind("\\" if sys.platform == "win32" else "/")+1:] + '!')
        elif cls.MODE == "auto update":
            with open(__file__) as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith('    DATA = {'):
                    lines[i] = out
            with open(__file__, 'w') as f:
                f.writelines(lines)
            print(f'Updated ' + __file__[__file__.rfind("\\" if sys.platform == "win32" else "/")+1:] + ' with new DATA line!')

    @staticmethod
    def __print(line):
        """Provides alternative printing interface for simplicity."""
        sys.stdout.write(line)
        sys.stdout.flush()

    @classmethod
    def query(cls):
        """Query all items in resource manager."""
        if cls.DATA == {}:
            print('Nothing to show!')
            return
        for key in cls.DATA:
            cls.__print(key + '\n')

    @classmethod
    @contextlib.contextmanager
    def load(cls, name, delete=True):
        """Dynamically loads resources and makes them usable while needed."""
        if name not in cls.DATA:
            raise KeyError('{!r} cannot be found'.format(name))
        if name not in cls.__CACHE:
            cls.__preload(name)
        path = pathlib.Path(name)
        with path.open('wb') as file:
            file.write(cls.__CACHE[name][name])
        yield path
        if delete:
            path.unlink()

    @classmethod
    def __preload(cls, path):
        """Load item in cache if it does not exist in a ready state yet."""
        if path not in cls.__CACHE:
            decoded = base64.b85decode(cls.DATA[path])
            decompressed = zlib.decompress(decoded)
            cls.__CACHE[path] = pickle.loads(decompressed)

    def __init__(self):
        """Creates an error explaining that the class was used improperly."""
        raise NotImplementedError('class was not designed for instantiation')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'query':
            Resource.query()
        else:
            print('Invalid argument!')
    elif len(sys.argv) == 3:
        file_name = sys.argv[2]
        if sys.argv[1] == 'add':
            Resource.add(file_name)
        elif sys.argv[1] == 'extract':
            Resource.extract(file_name)
        elif sys.argv[1] == 'remove':
            Resource.remove(file_name)
        else:
            print('Invalid argument!')
    else:
        print('Specify [ add / extract / remove / query ]!')
