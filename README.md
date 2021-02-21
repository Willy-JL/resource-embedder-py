# resource-embedder-py

Resource embedder and manager for python

## Manage resources

The manager aspect of this tool is command line:

#### Add files:

`python resources.py add filename`

#### Extract files:

`python resources.py extract filename`

#### Remove files:

`python resources.py remove filename`

#### Show files:

`python resources.py query`

## Use resources

Make sure the file exists, and extract it if it doesn't:

```python
from resources import Resource

Resource.ensure('filename')
  # OR
Resource.ensure('filename', 'name')  # providing a second argument will print "<name> was not found, extracting..." if the file needs to be extracted
```

Alternatively, extract it and delete it after it's been used:

```python
from resources import Resource

with Resource.load('filename') as file:
    # Anything you would do with a normal file
    contents = open(file).read()
  # The temporary extracted file will be deleted after exiting from the "with" block
```

### Credits:

Huge thanks to [this answer](https://stackoverflow.com/a/39350365) on stackoverflow, I basically took that and made it more user friendly.
