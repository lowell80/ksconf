from __future__ import absolute_import, unicode_literals

import ksconf.ext.six as six

from ksconf.conf.parser import GLOBAL_STANZA, _format_stanza, default_encoding


"""

POTENTIAL SOURCE OF INSPIRATION:


https://eql.readthedocs.io/en/latest/query-guide/grammar.html



https://github.com/tek/tubbs/tree/cd4c174c31b6c58a6935ca8a5f0f141377a9a04c/tubbs



Checkout hows this example uses 'expr', 'exprlist', 'op' and 'qualop'
https://github.com/palvaro/ldfi-py/blob/be9eea4c3b3fdba4605418c9a9bc07f1d27916dd/parser/dedalus.tatsu

"""

import json
from pprint import pprint

import tatsu
from tatsu.walkers import NodeWalker
from tatsu.model import ModelBuilderSemantics

known_functions = """
append
case
coalesce
if
len
like
lower
ltrim
match
nullif
replace
rtrim
split
substr
time
trim
upper
""".split()


class FilterSemantics(ModelBuilderSemantics):

    def string(self, ast):
        #print("STRING TYPE:   {}".format(type(args[0])))
        return ast.value

    def field(self, ast):
        return ast.field

    def function(self, ast):
        if ast.name not in known_functions:
            # There's probably a better way to handle this... better exception class maybe?
            raise ValueError("Unknown function named {}.".format(ast.name))
        return



class FilterWalker(NodeWalker):

    def walk_object(self, node, *args):
        print("WALK OBJECT {!r}".format(node))
        if hasattr(node, "children") and node.children is not None:
            return [self.walk(c, *args) for c in node.children()]
        else:
            return node

    ''' # Moved to semantics layer...
    def walk_QuotedString(self, node, *args):
        return node.value

    def walk_Field(self, node, *args):
        return node.field
    '''

    def walk_Filter(self, node, data):
        print("FILTER!!!  {}".format(dir(node)))
        return self.walk(node.filters, data)

    def walk_FilterExpression(self, node, data):
        print("WALK FILTER EXPRESSION!")
        return [ self.walk(c, data) for c in node.children() ]

    def walk_Selection(self, node, data):
        print("WALK SELECTION!")
        return [ self.walk(c, data) for c in node.children() ]

    def walk_AttrSelection(self, node, data):
        # node.key, node.op, node.str
        #return self.walk(node.left) + self.walk(node.right)

        #key = self.walk(node.key)
        #s = self.walk(node.str)
        key = node.key
        s = node.str
        op = node.op

        d2 = {}
        if op in ("=", "=="):
            for stz, d in data.items():
                if d.get(key,None) == s:
                    d2[stz] = d

        print("WALK ATTRSELECTION {!r}".format(node))
        return [ ("ATTR-SELECTION", node.op, key, s, d2) ]

    def walk__stanza_selection(self, node, data):
        # node.stanza
        print("Stanza SELECTION:   stanza='{}'".format(node.stanza))

        d2 = {}
        for key, d in data.items():
            if key == node.stanza:
                d2[key] = d
        # How to handle
        return d2

    def walk__projection(self, node, *args):
        # node.projection_args, node.projection_element
        #return self.walk(node.left) * self.walk(node.right)
        pass

    def walk__function(self, node, *args):
        # node.name, node.args
        #return self.walk(node.left) * self.walk(node.right)
        pass


def parse_and_walk_model():
    grammar = open('filterlang.ebnf').read()
    '''
    c = tatsu.to_python_sourcecode(grammar, name="ConfFilteLang", filename="filterlang_grammar.py")
    print(" ==== to_python_sourcecode: ")
    print(c)
    print(" ==== to_python_model: ")
    x = tatsu.to_python_model(grammar, filename="filterlang_model.py")
    print(x)
    '''

    data = {
        "stanza1": {
            "f1": "1",
            "f2": "2",
            "f3": "3",
        },
        "my_search": {
            "search" : "| noop",
            "f1": "true",
        }
    }

    #expr = "3 + 5.1 * ( 10/2 - 20 )"
    #expr='max(5.1, 5, len("hello"), "other", \'somefield\', typeof(2))'

    expr = "[my_search]"

    expr = "/myregex/"
    #### expr = "coalesce('field')"      #,\"value\")"

    expr = "[mysearch]"

    expr = "[mysearch] {'f1', 'f2', 'f3'} f1==\"true\""

    ######expr = "[mysearch] {'f1', f2=o2, 'f3'} f1==\"true\""


    # expr = "[mysearch] [mysearch2] {'f1', 'f2', 'f3'}"

    expr = "'attr2' != \"value\" [bob] {'f1', 'f2', 'f3'}"

    #expr = "{'f1', 'f2', f3=\"true\"}"


    expr = "'attr' == \"value\""
    expr = """
    'f1' == "1"
    """
    expr = "[stanza1]"

    print("EXPR:   {}".format(expr))
    parser = tatsu.compile(grammar)
    ast = parser.parse(expr)
    print("AST:")
    print(json.dumps(ast, indent=4))
    del parser


    print("")
    print("AST WITH FilterSemantics()")

    parser = tatsu.compile(grammar, semantics=FilterSemantics())
    ast = parser.parse(expr)
    print("AST:")
    pprint(ast, indent=4)
    del parser


    #parser = tatsu.compile(grammar, asmodel=True, semantics=FilterSemantics())

    #parser = tatsu.compile(grammar, asmodel=True, semantics=FilterSemantics()) # ,
    #                       #start="attribute_selection")

    parser = tatsu.compile(grammar, asmodel=True, semantics=FilterSemantics())
    model = parser.parse(expr) #, parseinfo=True) #, trace=True, colorize=True)



    print('# WALKER RESULT IS:')
    print(FilterWalker(data).walk(model, data))
    print("")

    print("# MODEL OUTPUT:")
    print(model)
    print("")


 # parseInfo=True
 #   print(model[0].rule)



if __name__ == '__main__':
    parse_and_walk_model()
