class TreeNode(object):

    """Node with an arbitrary number of children.

    This is implemented exclusively for Huffman tree generation in code.py.
    As such, it's missing a lot of features, but that's okay. Don't use it for
    a "real" tree."""

    def __init__(self, key, data, children=[]):
        """Create the node with the given key, data, and children.

        :key: Any object that can be compared.
        :data: Any object.
        :children: Possibly empty list of TreeNodes.

        """
        self.key = key
        self.data = data
        self.children = children

    def print_(self):
        """Print the tree rooted at the node in tabular form.
        :returns: Nothing.

        """
        def _print(node, level):
            print("\t"*level + str((node.key, node.data)))
            for child in node.children:
                _print(child, level + 1)
        _print(self, 0)

    def __eq__(self, other):
        """Test equality with another node."""
        return self.key == other.key

    def __ne__(self, other):
        """Test inequality with another node."""
        return self.key != other.key

    def __lt__(self, other):
        """Test the less than inequality with another node."""
        return self.key < other.key

    def __le__(self, other):
        """Test the less than or equal to inequality with another node."""
        return self.key <= other.key

    def __gt__(self, other):
        """Test the greater than inequality with another node."""
        return self.key > other.key

    def __ge__(self, other):
        """Test the greater than or equal to inequality with another node."""
        return self.key >= other.key
