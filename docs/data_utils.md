# Data utilities

Python scripts for generating schema appropriate data from various contexts.

## How it's organized

Below is a list of python modules and their methods. When in doubt, check the overall [data utils](../flask_jsondash/data_utils/) module for more.

Any module that supports command line usage will be accessible via `python MODULE_NAME.py`. To find out how to use them, just run `python MODULE_NAME.py --help`

## Modules

### `filetree.py`

`get_tree`: build a json representation of a file tree appropriate for creating dendrograms, treemaps and radial dendrograms. See [schemas](schemas.md#D3) for more info on these chart types.
