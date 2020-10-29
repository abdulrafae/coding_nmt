from tree import TreeNode
import bisect
import math

def huffman_initial_count(message_count, digits):
    """
    Return the number of messages that must be grouped in the first layer for
    Huffman Code generation.

    See the section "Generalization" in ./notes.md for details.

    :message_count: Positive integral message count.
    :digits: Integer >= 2 representing how many digits are to be used in codes.
    :returns: The number of messages that _must_ be grouped in the first level
              to form a `digit`-ary Huffman tree.

    """

    if message_count <= 0:
        raise ValueError("cannot create Huffman tree with <= 0 messages!")
    if digits <= 1:
        raise ValueError("must have at least two digits for Huffman tree!")

    if message_count == 1:
        return 1

    return 2 + (message_count - 2) % (digits - 1)

def combine_and_replace(nodes, n):
    """
    Combine n nodes from the front of the low-to-high list into one whose key is
    the sum of the merged nodes. The new node's data is set to None, then
    inserted into its proper place in the list.

    Note: The sum of keys made here is the smallest such combination.

    In the contradictory style of Huffman, if any set of nodes were chosen
    except for the first n, then changing a node not in the first n to one that
    is from the first n would reduce the sum of their keys. Thus the smallest
    sum is made from the first n nodes.

    :nodes: A list of TreeNodes.
    :n: Integer < len(nodes).
    :returns: Low-to-high list that combines the last n nodes into one.

    """
    group = nodes[:n]
    combined = TreeNode(sum(node.key for node in group), None, group)
    nodes = nodes[n:]
    bisect.insort(nodes, combined)

    return nodes

def huffman_nary_tree(probabilities, digits):
    """Return a Huffman tree using the given number of digits.

    This `digits`-ary tree is always possible to create. See ./notes.md.

    :probabilities: List of tuples (symbol, probability) where probability is
                    any floating point and symbol is any object.
    :digits: Integral number of digits to use in the Huffman encoding. Must be
             at least two.
    :returns: TreeNode that is the root of the Huffman tree.

    """
    if digits <= 1:
        raise ValueError("must have at least 2 digits!")

    if len(probabilities) == 0:
        raise ValueError("cannot create a tree with no messages!")

    if len(probabilities) == 1:
        symbol, freq = probabilities[0]
        if freq != 1:
            print("The probabilities sum to {} (!= 1)...".format(freq))
        if math.isclose(probabilities[0].key, 1.0):
            print("(but they are close)")

        return TreeNode(freq, symbol)

    # TreeNode does rich comparison on key value (probability), so we can
    # pass this right to sorted().
    probabilities = [TreeNode(freq, symbol) for (symbol, freq) in probabilities]
    probabilities = sorted(probabilities)

    # Grab the required first set of messages.
    initial_count = huffman_initial_count(len(probabilities), digits)
    probabilities = combine_and_replace(probabilities, initial_count)

    # If everything is coded correctly, this loop is guaranteed to terminate
    # due to the initial number of messages merged.
    while len(probabilities) != 1:
        # Have to grab `digits` nodes from now on to meet an optimum code requirement.
        probabilities = combine_and_replace(probabilities, digits)

    if probabilities[0].key != 1:
        print("The probabilities sum to {} (!= 1)...".format(probabilities[0].key))
        if math.isclose(probabilities[0].key, 1.0):
            print("(but they are close)")

    return probabilities.pop()

def indicies_to_code(path, digits):
    """Convert the path into a string.

     We join the indices directly, from most to least significant, keeping
     leading zeroes.
     Examples:
       [1, 2, 3] -> "123"
       [7, 2, 10] -> "72a"
       [0, 2, 1] ->  "021"
    """
    combination = ""
    for index in path:
        if index < 0:
            raise ValueError("cannot accept negative path indices (what went wrong?)")
        if index >= digits:
            raise ValueError("cannot have an index greater than the number of digits!")

        combination += baseN(index, digits)

    return combination

def huffman_nary_dict(probabilities, digits):
    """Return a dictionary that decodes messages from the nary Huffman tree.

    This gives a method of _decoding_, but not _encoding_. For that, an inverse
    dictionary will need to be created. See inverse_dict().

    :probabilities: List of tuples (symbol, probability) where probability is
                    any floating point and symbol is any object.
    :digits: Integral number of digits to use in the Huffman encoding. Must be
             at least two.
    :returns:  A dictionary of {code: message} keys, where "code" is a string
               of digits representing the Huffman encoding for the given
               message.

    """
    def visit(node, path, decoding_dict):
        # The goal here is to visit each node, passing the path taken to get there
        # as well. When we reach a leaf, then we know that we're at a message, so
        # we can turn the path into digits (in an arbitrary but consistent way) and
        # add it to the dict.
        # Here, the "path" is the list of indices for children that we have to
        # access to get to the needed node. In binary, paths would be lists of
        # 0s and 1s.
        # We modify the passed in dictionary, so no returning is needed.
        # See: https://stackoverflow.com/questions/986006.
        if len(node.children) == 0:
            code = indicies_to_code(path, digits)
            decoding_dict[code] = node.data
        else:
            for k, child in enumerate(node.children):
                path.append(k)
                visit(child, path, decoding_dict)
                path.pop()

    root = huffman_nary_tree(probabilities, digits)
    decoding_dict = dict()
    visit(root, [], decoding_dict)

    return decoding_dict

def inverse_dict(original):
    """Return a dictionary that is the inverse of the original.

    Given the pair original[key] = value, the returned dictionary will give
    ret[value] = key. It is important to keep two separate dictionaries in case
    there is key/value collision. Trying to insert a value that matches a key
    as a key will overwrite the old key.

    Example:
        original = {"a": "b", "foo": "a"}
        original["a"] = "foo" # Lost pair {"a": "b"}.

    :original: Dictionary.
    :returns: Inverse dictionary of `original`.

    """
    ret = dict()

    for key, value in original.items():
        ret[value] = key

    return ret

# http://stackoverflow.com/a/2267428
def baseN(num,b,numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

def ascii_encode(string):
    """Return the 8-bit ascii representation of `string` as a string.

    :string: String.
    :returns: String.

    """
    def pad(num):
        binary = baseN(num, 2)
        padding = 8 - len(binary)
        return "0"*padding + binary
    return "".join(pad(ord(c)) for c in string)

class HuffmanCode(object):

    """Encode and decode messages with a constructed Huffman code."""

    def __init__(self, probabilities, digits):
        """Create the Huffman dictionaries needed for encoding and decoding.

        :probabilities: List of (message, frequency) tuples.
        :digits: Number of digits to use in the Huffman encoding.

        """
        self.probabilities = probabilities
        self.huffman = huffman_nary_dict(probabilities, digits)
        self.inv_huffman = inverse_dict(self.huffman)

    def encode(self, messages):
        """Encode each item in `messages` with the stored Huffman code.

        Raises a KeyError if there is a message in `messages` that is not in
        the inverse Huffman dictionary.

        :messages: List of messages to be encoded.
        :returns: String of digits that represents Huffman encoding.

        """
        return "".join(self.inv_huffman[message] for message in messages)

    def decode(self, string):
        """Decode the given string with the stored Huffman dictionary.

        :string: String encoded with the stored inverse Huffman dictionary.
        :returns: String.

        """

        decode = ""
        while string:
            # Huffman codes are prefix free, so read until we find a code.
            for index in range(len(string)+1):
                if string[:index] in self.huffman:
                    break
            code = string[:index]
            decode += self.huffman[code]
            string = string[index:]

        return decode
