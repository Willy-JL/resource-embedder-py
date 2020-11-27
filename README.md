# resource-embedder-py

Resource embedder and manager for python

## Manage resources

The manager aspect of this tool is command line:

#### Add files:

`python resources.py add filename`

And paste the new DATA string in the file

#### Remove files:

`python resources.py remove filename`

And paste the new DATA string in the file

#### Show files:

`python resources.py query`

## Use resources

```python
from resources import Resource

with Resource.load('filename') as file:
    # Anything you would do with a normal file
    contents = open(file).read()
```

### Thanks:

Huge thanks to [this answer](https://stackoverflow.com/a/39350365) on stackoverflow, I basically took that and made it more user friendly.
