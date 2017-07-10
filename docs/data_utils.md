# Data utilities

Python scripts for generating schema appropriate data from various contexts.

## How it's organized

Below is a list of python modules and their methods. When in doubt, check the overall [data utils](../flask_jsondash/data_utils/) module for more.

Any module that supports command line usage will be accessible via `python MODULE_NAME.py`. To find out how to use them, just run `python MODULE_NAME.py --help`, or look at the source.

## Modules

### `filetree.py`

`get_tree`: build a json representation of a filesystem tree appropriate for creating dendrograms, treemaps and radial dendrograms. See [schemas](schemas.md#d3) for more info on these chart types.

### `filetree_digraph.py`

`get_dotfile_tree`: build a [dotfile](http://www.graphviz.org/doc/info/lang.html) representation of a filesystem tree appropriate for creating graphs and digraphs. See [schemas](schemas.md#graph) for more info on these chart types.

### `wordcloud.py`

`get_word_freq_distribution`: create a counter with word frequencies.

`format_4_wordcloud`: create wordcloud friendly config from words.
