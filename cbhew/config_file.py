''' .hew .hwsファイルを読み込むためのモジュール
'''
from lark import Lark
from lark import Transformer
import pkgutil

class ConfigTransformer(Transformer):
    data:dict = {}
    now_category:str = None
    def root(self,tree):
        ret = {}
        for name,contents in tree:
            ret[name] = contents
        return ret

    def config(self,tree):
        cate_name = tree[0]
        if len(tree) > 1:
            con = tree[1]
        else:
            con = None
        return (cate_name, con)

    def category_name(self,tree):
        return str(tree[0])
    
    def contents(self,tree):
        ret = []
        for i in tree:
            ret.append(i)
        return ret
    
    def line_space_row(self,tree):
        ret = []
        for i in tree:
            ret.append(i)
        return ret

    def value(self,tree):
        return tree[0]
    
    def SIGNED_NUMBER(self,tree):
        return int(tree)
    
    def FLOAT(self,tree):
        return float(tree)

    def ESCAPED_STRING(self,tree):
        return str(tree).replace("^\"","\"")
    
    def EMPTY_STRING(self,tree):
        return ""

_parser = Lark(str(pkgutil.get_data('cbhew', 'config_file.lark'), encoding='utf-8'),
               parser='lalr',
               transformer=ConfigTransformer())


def load(path):
    """fileを読み込んでparseしてdictに変換
    """
    config_list = None
    with open(path, encoding="s-jis") as file:
        file_text = file.read()
        config_list = _parser.parse(file_text)
    return config_list


