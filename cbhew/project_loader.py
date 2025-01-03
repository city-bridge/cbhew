import pathlib
import copy
from cbhew.hwp import HwpParser
from cbhew.hws import HwsParser


class ProjectLoader:
    hws: HwsParser = None
    hws_path: pathlib.Path = None
    project_list: list = []
    replace_dict: dict = {}
    def __init__(self):
        pass

    def set_replace_dict(self,replace:dict):
        """置換用の辞書を設定

        Args:
            replace (dict): 置換用の辞書
        """
        if replace is None:
            replace = {}
        self.replace_dict = replace

    def load_project(self, hws_path: str):
        """ .hwsファイルからプロジェクト読み込み

        Args:
            hws_path (str): .hwsのパス
        """
        self.hws_path = pathlib.Path(hws_path)
        self.hws = HwsParser()
        self.hws.load_hws(hws_path)
        for project in self.hws.get_projects():
            hwp_data = HwpParser()
            hwp_data.load_hwp(project["hwp_path"])
            hwp_path = pathlib.Path(project["hwp_path"])
            self.project_list.append({
                "name":project["name"],
                "hwp_path":str(hwp_path),
                "data":hwp_data
            })
    
    def create_hws_replase_dict(self)->dict:
        """hwsの置換用の辞書を取得

        Returns:
            dict: 置換用の辞書
        """
        replace = copy.deepcopy(self.replace_dict)
        work_space = self.hws.get_wordspace_detailes()
        replace["$(WORKSPDIR)"] = work_space["work_space_path"]
        for place in self.hws.get_custom_place_holders():
            replace["$({})".format(place["name"])] = place["path"]
        return replace
    
    def get_all_configs(self)->list:
        """全ての設定を取得

        Returns:
            list: 全ての設定
        """
        result = []
        hws_name = self.hws_path.stem
        for project in self.project_list:
            hwp: HwpParser = project["data"]
            project_details = hwp.get_project_details()
            replace = self.create_hws_replase_dict()
            replace["$(PROJDIR)"] = project_details["project_directory"]
            project_files = hwp.get_project_files()
            files = [x["path"] for x in project_files]
            db_ver = hwp.get_database_version()
            for conf in hwp.get_configurations():
                replace["$(CONFIGDIR)"] = conf["path"]
                if db_ver == "1.0":
                    options = hwp.analyze_config_ver1(conf["name"])
                else:
                    options = hwp.analyze_config_ver2(conf["name"])
                result.append({
                    "name":"{}_{}_{}".format(hws_name, project["name"], conf["name"]),
                    "include":self._replace_path_list(options["INCLUDE"],replace),
                    "define":self._replace_path_list(options["DEFINE"],replace),
                    "preinclude":self._replace_path_list(options["PREINCLUDE"],replace),
                    "files":files
                }) 
        return result

    def _replace_path_list(self,path_list:list,replace:dict)->list:
        """パスのリストの置換

        Args:
            path_list (list): 対象のパスリスト
            replace (dict): 置換用の辞書

        Returns:
            list: 置換後のパスリスト
        """
        result = []
        for path in path_list:
            result.append(self._replace_path(path,replace))
        return result

    def _replace_path(self,path:str,replace:dict)->str:
        """パスの置換

        Args:
            path (str): 対象のパス
            replace (dict): 置換用の辞書

        Returns:
            str: 置換後のパス
        """
        for key in replace:
            path = path.replace(key,replace[key])
        return path
