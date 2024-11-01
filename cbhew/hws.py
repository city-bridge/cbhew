""".hwsファイルに関する処理
"""
import cbhew.config_file as config_file

class HwsParser:
    root:dict = {}
    def __init__(self):
        pass
    
    def load_hws(self, hws_path:str):
        """hwsのfileからパース
        """
        self.root = config_file.load(hws_path)

    def get_category_contents_table(self,category_name:str)->list:
        """指定のカテゴリを2次元配列で取得
        """
        if category_name not in self.root:
            return []
        return self.root[category_name]

    def get_category_contents_dict_list(self,category_name,key_list)->list:
        """指定のカテゴリを2次元配列で取得し、列に名前を付ける
        """
        result = []        
        table = self.get_category_contents_table(category_name)
        for row in table:
            col_dict = {}
            for key in key_list:
                col_dict[key] = None
            count = 0
            for col in row:
                if count <= len(key_list):
                    col_dict[key_list[count]] = col
                    count = count + 1
            result.append(col_dict)
        return result

    def get_wordspace_detailes(self)->list:
        """[WORKSPACE_DETAILS]の内容取得
        """
        key_list = [
            "name","work_space_path","hws_path","enging","standard"
        ]
        category_name = "WORKSPACE_DETAILS"
        result = self.get_category_contents_dict_list(category_name, key_list)
        return result[0]

    def get_custom_place_holders(self)->list:
        """[CUSTOMPLACEHOLDERS]の内容取得
        """
        key_list=["name","name2","path"]
        category_name = "CUSTOMPLACEHOLDERS"
        result = self.get_category_contents_dict_list(category_name, key_list)
        return result

    def get_projects(self)->list:
        """[PROJECTS]の内容取得
        """
        key_list=["name","path","hwp_path","number"]
        category_name = "PROJECTS"
        result = self.get_category_contents_dict_list(category_name, key_list)
        return result

