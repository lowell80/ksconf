from __future__ import absolute_import, unicode_literals
import os

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



class FilterSemantics(object):
    """
    Really simple cleanup things to make the model easier to work with.  The real work is done in
    the NodeWalker class.
    """
    def string(self, ast):
        return ast.value

    def field(self, ast):
        return ast.field

    def filter_expression(self, ast):
        return ast.filter

    def function(self, ast):
        if ast.name not in known_functions:
            # There's probably a better way to handle this... better exception class maybe?
            raise ValueError("Unknown function named {}.".format(ast.name))
        return ast


class FilterSemanticsModelBuilder(ModelBuilderSemantics, FilterSemantics):
    pass


class FilterWalker(NodeWalker):

    def walk_object(self, node, *args):
        print("WALK OBJECT {}".format(type(node).__name__))
        if hasattr(node, "children") and node.children is not None:
            return [self.walk(c, *args) for c in node.children()]
        else:
            return node

    #def walk_FilterExpression(self, node, data):
    # return self.walk(node.filter, data)

    def walk_FilterChain(self, node, data):
        # Inside a single chain, 'data' is passed sequentially down from filter to filter (like unix pipes)

        children = node.children()
        print("EVALUATING FILTER CHAIN!!!  {}  KIDS=[{}]".format(type(node).__name__, children))
        data = dict(data)      # Shallow copy good enough???
        for child in children:
            print("    Running for {}    DATA[in]={}".format(json.dumps(child.asjson()), data))
            data = self.walk(child, data)
        return data
        #return self.walk(node.filters, data)

#    def walk_FilterExpression(self, node, data):
#        print("WALK FILTER EXPRESSION!")
#        return [ self.walk(c, data) for c in node.children() ]

    def walk_Selection(self, node, data):
        print("WALK SELECTION!")
        return [ self.walk(c, data) for c in node.children() ]

    def walk_AttrSelection(self, node, data):
        # node.key, node.op, node.str
        key = node.key
        s = node.str
        op = node.op

        d2 = {}
        if op in ("=", "=="):
            for stz, d in data.items():
                if d.get(key, None) == s:
                    d2[stz] = d
        print("WALK ATTRSELECTION {!r}".format(node))
        return d2

    def walk_StanzaSelection(self, node, data):
        # node.stanza
        print("Stanza SELECTION:   stanza='{}'".format(node.stanza))
        d2 = {}
        for key, d in data.items():
            if key == node.stanza:
                d2[key] = d
        print("SELECTION:   children:  {}".format(node.children()))
        # How to handle
        return d2

    def walk_Projection(self, node, data):
        # node.projection_args, node.projection_element
        print("PROJECTION:      {}".format(json.dumps(node.asjson())))
        keep_fields = set(node.projection_args)
        o = {}
        for stanza, d in data.items():
            n = {key:value for key,value in d.items() if key in keep_fields}
            if n:
                o[stanza] = n
        return o

    def walk__function(self, node, *args):
        # node.name, node.args
        raise NotImplementedError



class ConfFilterLang(object):
    __grammar = None
    __parser = None

    @property
    def _grammar(self):
        if self.__grammar is None:
            ebnf_file = os.path.join(os.path.dirname(__file__), "filterlang.ebnf")
            self.__grammar = open(ebnf_file).read()
        return self.__grammar

    @property
    def _parser(self):
        if self.__parser is None:
            self.__parser = tatsu.compile(self._grammar, asmodel=True,
                                          semantics=FilterSemanticsModelBuilder())
        return self.__parser

    def evaluate(self, expr, conf):
        model = self._parser.parse(expr)
        walker = FilterWalker()
        return walker.walk(model, conf)

# Singleton
cfl = ConfFilterLang()



def evaluate_filter(expr, conf):
    return cfl.evaluate(expr, conf)




def parse_and_walk_model():
    grammar = cfl._grammar
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
        "mysearch": {
            "search": "| noop",
            "f1": "1",
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
    'f1' == "1" [stanza1]
    """
    #expr = "[stanza1] { 'f1'=\"red\", f3, f2, f19} f1==\"1\" "

    print("EXPR:   {}".format(expr))
    parser = tatsu.compile(grammar)
    ast = parser.parse(expr)
    print("AST:")
    print(json.dumps(ast, indent=4))
    del parser


    print("\n\n")
    print("AST   with ** FilterSemantics() **")
    parser = tatsu.compile(grammar, semantics=FilterSemantics())
    ast = parser.parse(expr)
    print("AST:")
    print(json.dumps(ast, indent=4))
    del parser


    #parser = tatsu.compile(grammar, asmodel=True, semantics=FilterSemantics())

    #parser = tatsu.compile(grammar, asmodel=True, semantics=FilterSemantics()) # ,
    #                       #start="attribute_selection")

    parser = tatsu.compile(grammar, asmodel=True, semantics=FilterSemanticsModelBuilder())
    model = parser.parse(expr) #, parseinfo=True) #, trace=True, colorize=True)

    print("\n\n")
    print("# MODEL OUTPUT:")
    print(model)

    print("\n\n")
    print('# WALKER RESULT IS:')
    print(FilterWalker().walk(model, data))
    print("")



if __name__ == '__main__':
    parse_and_walk_model()
