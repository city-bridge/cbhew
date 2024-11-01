""".hwpファイルに関する処理
"""
import cbhew.config_file as config_file
import cbhew.hwp_option as hwp_option

class HwpParser:
    
    def load_hwp(self, hwp_path:str):
        """hwpのパスからパース
        """
        self.root = config_file.load(hwp_path)

    def get_category_contents_table(self,category_name:str)->list:
        """指定のカテゴリを2次元配列で取得
        """
        if category_name not in self.root:
            return []
        return self.root[category_name]

    def get_category_contents_dict_list(self,category_name:str,key_list:list)->list:
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

    def get_database_version(self)->str:
        """[DATABASE_VERSION]の内容取得
        """
        table = self.get_category_contents_table("DATABASE_VERSION")
        return table[0][0]
    
    def get_project_details(self)->dict:
        """[PROJECT_DETAILS]の内容取得
        """
        key_list = ["name","project_directory","hwp_path","engin", "standard","application","cpu_type","cpu_sub_type"]
        project_details = self.get_category_contents_dict_list("PROJECT_DETAILS", key_list)
        return project_details[0]
    
    def get_project_files(self)->list:
        """[PROJECT_FILES]の内容取得
        """
        key_list = ["path","user","file_type","type"]
        project_files = self.get_category_contents_dict_list("PROJECT_FILES", key_list)
        return project_files

    def get_configurations(self)->list:
        """[CONFIGURATIONS]の内容取得
        """
        key_list = ["name","path"]
        configurations = self.get_category_contents_dict_list("CONFIGURATIONS", key_list)
        return configurations

    def get_options_xxx(self,conf_name:str, id_sort:bool=True)->list:
        """[OPTIONS_xxx]の内容取得
        """
        key_list = ["data","id"]
        category_name = "OPTIONS_" + conf_name
        options_xxx = self.get_category_contents_dict_list(category_name,key_list)
        if id_sort:
            options_xxx = sorted(options_xxx, key=lambda x: x.get('id', 0))
        return options_xxx

    def get_options_xxx_ana(self,conf_name:str)->dict:
        """[OPTIONS_xxx]の内容解析
        """
        result = {
            "DEFINE":[],
            "INCLUDE":[],
            "PREINCLUDE":[]
        }
        options_xxx = self.get_options_xxx(conf_name)
        for options_xxx_line in options_xxx:
            try:
                options = hwp_option.parse(options_xxx_line["data"])
                for values in options:
                    if values[0] == "S" and values[1] == "DEFINE":
                        val = values[2:]
                        result["DEFINE"].extend(val)
                    elif values[0] == "S" and values[1] == "INCLUDE":
                        val = values[2:]
                        result["INCLUDE"].extend(val)
                    elif values[0] == "S" and values[1] == "PREINCLUDE":
                        val = values[2:]
                        result["PREINCLUDE"].extend(val)

            except Exception as e:
                #print(e)
                #raise e
                #parser_optionsに形式が合わないものは無視
                pass
        return result
    
