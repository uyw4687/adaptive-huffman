import sys
import getopt
from node import Node
import time

class FGK(object):
    def __init__(self):
        super(FGK, self).__init__()
        self.NYT = Node(symbol="NYT")
        self.root = self.NYT
        self.nodes = []
        self.seen = [None] * 256

    def get_code(self, s, node, code=''):
        if node.left is None and node.right is None:
            return code if node.symbol == s else ''
        else:
            temp = ''
            if node.left is not None:
                temp = self.get_code(s, node.left, code+'0')
            if not temp and node.right is not None:
                temp = self.get_code(s, node.right, code+'1')
            return temp

    def find_largest_node(self, weight):
        for n in reversed(self.nodes):
            if n.weight == weight:
                return n

    def swap_node(self, n1, n2):
        i1, i2 = self.nodes.index(n1), self.nodes.index(n2)
        self.nodes[i1], self.nodes[i2] = self.nodes[i2], self.nodes[i1]

        tmp_parent = n1.parent
        n1.parent = n2.parent
        n2.parent = tmp_parent

        if n1.parent.left is n2:
            n1.parent.left = n1
        else:
            n1.parent.right = n1

        if n2.parent.left is n1:
            n2.parent.left = n2
        else:
            n2.parent.right = n2

    def insert(self, s):
        node = self.seen[ord(s)]

        if node is None:
            spawn = Node(symbol=s, weight=1)
            internal = Node(symbol='', weight=1, parent=self.NYT.parent,
                left=self.NYT, right=spawn)
            spawn.parent = internal
            self.NYT.parent = internal

            if internal.parent is not None:
                internal.parent.left = internal
            else:
                self.root = internal

            self.nodes.insert(0, internal)
            self.nodes.insert(0, spawn)

            self.seen[ord(s)] = spawn
            node = internal.parent

        while node is not None:
            largest = self.find_largest_node(node.weight)

            if (node is not largest and node is not largest.parent and
                largest is not node.parent):
                self.swap_node(node, largest)

            node.weight = node.weight + 1
            node = node.parent

    def encode(self, text):

        t1 = time.time()
        
        result = ''

        for s in text:
            if self.seen[ord(s)]:
                result += self.get_code(s, self.root)
            else:
                result += self.get_code('NYT', self.root)
                result += bin(ord(s))[2:].zfill(8)

            self.insert(s)

        t2 = time.time()

        return result, (t2-t1)

    def get_symbol_by_ascii(self, bin_str):
        return chr(int(bin_str, 2))

    def decode(self, text):
        
        t1 = time.time()

        result = ''

        symbol = self.get_symbol_by_ascii(text[:8])
        result += symbol
        self.insert(symbol)
        node = self.root

        i = 8
        while i < len(text):
            node = node.left if text[i] == '0' else node.right
            symbol = node.symbol

            if symbol:
                if symbol == 'NYT':
                    symbol = self.get_symbol_by_ascii(text[i+1:i+9])
                    i += 8

                result += symbol
                self.insert(symbol)
                node = self.root

            i += 1

        t2 = time.time()

        return result, (t2-t1)


def main(argv):
    try:
        opts, _ = getopt.getopt(argv, "e:d:")
    except getopt.GetoptError:
        sys.exit(2)

    text = None
    result = None
    for opt, arg in opts:
        if opt == '-e':
            orig = 0
            with open(arg) as f:
                text = f.read()
                orig = len(text)
            
            result,exec_time = FGK().encode(text)

            size_compressed = int((len(result)-1)/8)+1
            size_original = orig*8
            ratio = size_compressed/size_original*100
            
            with open("encoded.adaptivehuffman", "w") as dest:
                dest.write(result)

            print("[+] Compression finished in %.5f seconds"% exec_time )
            print("[+] Compression ratio  %.1f"% ratio )

        elif opt == '-d':
            with open(arg) as f:
                text = f.read()

            result,exec_time = FGK().decode(text)

            with open("decoded.adaptivehuffman", "w") as dest:
                dest.write(result)
            
            print("[+] Decompression finished in %.5f seconds"% exec_time )

if __name__ == '__main__':
    main(sys.argv[1:])
