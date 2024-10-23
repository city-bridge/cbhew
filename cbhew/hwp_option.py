''' hwpファイル内の[OPTIONS_xxx]の1行分パースするためのモジュール
'''
from lark import Lark
from lark import Transformer
import pkgutil

class HwpOptionTransformer(Transformer):
    data:dict = {}
    now_category:str = None
    def options(self,tree):
        return tree

    def option(self,tree):
        return tree
    
    def value(self,tree):
        return tree[0]
    
    def SIGNED_NUMBER(self,tree):
        return int(tree)
    
    def FLOAT(self,tree):
        return float(tree)

    def ESCAPED_STRING(self,tree):
        return str(tree)
    
    def EMPTY_STRING(self,tree):
        return ""
    
    def KEY_STRING(self, tree):
        return str(tree)


_parser = Lark(str(pkgutil.get_data('cbhew', 'hwp_option.lark'), encoding='utf-8'),
               parser='lalr',
               transformer=HwpOptionTransformer())


def parse(option_data_text:str)->dict:
    """option textを読み込んでparseしてdictに変換

    Args:
        option_data_text (str): option text

    Returns:
        dict: 解析結果
    """
    return _parser.parse(option_data_text)


