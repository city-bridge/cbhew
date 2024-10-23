import pathlib
import json
from cbhew.hwp import HwpParser
from cbhew.hws import HwsParser
import logging

logger = logging.getLogger(__name__)

def main(project_path:str,replace:dict={}):
    """ .hwpファイルからVSCode用の設定ファイル出力

    Args:
        project_path (str): プロジェクトのパス
        replace (dict): 置換用の辞書
    """
    logging.basicConfig(level=logging.INFO)
    hws_path, output_file = check_project(project_path)
    logger.info("load hwp:%s",hws_path)
    logger.info("output file:%s",output_file)
    out_json_dict = convert_hws_to_dict(hws_path,replace)
    out_json_txt = json.dumps(out_json_dict,indent=4)
    with output_file.open("w",encoding='s-jis') as f:
        f.write(out_json_txt)

def check_project(project_path_str:str):
    """プロジェクトのパスをチェック

    Args:
        project_path_str (str): プロジェクトのパス

    Returns:
        _type_: hwsファイルのパスと出力先のファイルのパス
    """
    project_path = pathlib.Path(project_path_str)    
    output_path=project_path / '.vscode'

    if not project_path.exists():
        raise Exception("{} is not exists".format(project_path))
    
    if not project_path.is_dir():
        raise Exception("{} is not dir".format(project_path))

    #hwsファイルの検索    
    hws_path = search_hws(project_path)
    if hws_path == None:
        raise Exception("not hws file")

    #出力先の確認
    output_path.mkdir(exist_ok=True)
    if not output_path.exists():
        raise Exception("{} is not exists".format(output_path))

    if not output_path.is_dir():
        raise Exception("{} is not dir".format(output_path))

    output_file = output_path/"c_cpp_properties.json"
    
    return (hws_path, output_file)

def search_hws(search_path_str:str)->pathlib.Path:
    """hwsファイルを検索する

    Args:
        search_path_str (str): 検索するディレクトリ

    Returns:
        pathlib.Path: hwsファイルのパス
    """
    search_path = pathlib.Path(search_path_str)
    result = None
    for child in search_path.glob("**/*.hws"):
        result = str(child)
#        break
    return result

def convert_hws_to_dict(hws_path:pathlib.Path, replace:dict)->dict:
    """hwsファイルを読み込んでVSCode用の設定ファイルに変換

    Args:
        hws_path (pathlib.Path): hwsファイルのパス
        replace (dict): 置換用の辞書

    Returns:
        dict: VSCode用の設定ファイル
    """
    parser = HwsParser()
    parser.load_hws(hws_path)
    json_dict = {
        "configurations":[],
        "version":4
    }
    create_replace_dict(parser,replace)
    for project in parser.get_projects():
        hwp_path = pathlib.Path(project["hwp_path"])
        logger.info("hwp path:%s",hwp_path)
        replace["$(PROJDIR)"] = str(hwp_path.parent)
        for conf in convert_hwp_to_config(project["name"],hwp_path,replace):
            json_dict["configurations"].append(conf)
            
    return json_dict

def create_replace_dict(hws_parser:HwsParser,replace:dict):
    """置換用の辞書を作成

    Args:
        hws_parser (HwsParser): hwsファイルのパーサー
        replace (dict): 置換用の辞書

    """    
    work_space = hws_parser.get_wordspace_detailes()
    replace["$(WORKSPDIR)"] = work_space["work_space_path"].replace("\\","/")

    for place in hws_parser.get_custom_place_holders():
        replace["$({})".format(place["name"])] = place["path"].replace("\\","/")

def replace_path(path:str,replace:dict)->str:
    """パスの置換

    Args:
        path (str): 対象のパス
        replace (dict): 置換用の辞書

    Returns:
        str: 置換後のパス
    """
    for key in replace:
        path = path.replace(key,replace[key])
    path = path.replace("\\","/")
    return path

def convert_hwp_to_config(project_name:str, hwp_path:pathlib.Path, replace:dict)->list:
    """hwpファイルを読み込んでVSCode用の設定ファイルに変換

    Args:
        project_name (str): プロジェクトの名前
        hwp_path (pathlib.Path): hwpファイルのパス
        replace (dict): 置換用の辞書

    Returns:
        list: VSCode用の設定ファイルのリスト
    """
    parser = HwpParser()
    parser.load_hwp(hwp_path)
    config_list = []

    db_ver = parser.get_database_version()
    conf_list = parser.get_configurations()
    for conf in conf_list:
        if db_ver == "1.0":
            conf_dict = _conv_config_ver1_0(project_name,replace, parser, conf)
        else:
            conf_dict = _conv_config_ver2_0(project_name,replace, parser, conf)
        config_list.append(conf_dict)
    return config_list

def _conv_config_ver2_0(project_name:str,replace:dict,parser:HwpParser, conf:dict)->dict:
    """hwpファイルを読み込んでVSCode用の設定ファイルに変換

    Args:
        project_name (str): プロジェクトの名前
        replace (dict): 置換用の辞書
        parser (HwpParser): パーサー
        conf (dict): _description_

    Returns:
        dict: VSCode用の設定ファイル
    """
    conf_name = "None"
    if "name" in conf:
        conf_name = conf["name"]
    conf_dict = {
        "name":"{}_{}".format(project_name,conf_name),
        "includePath":[
            "${workspaceFolder}/**",
        ],
        "forcedInclude":[],
        "defines":[],
        "cStandard": "gnu17",
    }
    result = parser.get_options_xxx_ana(conf_name)
    if "INCLUDE" in result:
        for path in result["INCLUDE"]:
            path = replace_path(path,replace)
            conf_dict["includePath"].append(path)
    if "DEFINE" in result:
        conf_dict["defines"].extend(result["DEFINE"])
    if "PREINCLUDE" in result:
        for path in result["PREINCLUDE"]:
            path = replace_path(path,replace)
            conf_dict["forcedInclude"].append(path)
    return conf_dict

def _conv_config_ver1_0(project_name:str,replace:dict,parser:HwpParser, conf:dict)->dict:
    """hwpファイルを読み込んでVSCode用の設定ファイルに変換

    Args:
        project_name (str): プロジェクトの名前
        replace (dict): 置換用の辞書
        parser (HwpParser): _description_
        conf (dict): _description_

    Returns:
        dict: VSCode用の設定ファイル
    """
    conf_name = "None"
    if "name" in conf:
        conf_name = conf["name"]
    conf_dict = {
        "name":"{}_{}".format(project_name,conf_name),
        "includePath":[
            "${workspaceFolder}/**",
        ],
        "forcedInclude":[],
        "defines":[],
        "cStandard": "gnu17",
    }
    result = parser.get_options_xxx_ana(conf)
    if "INCLUDE" in result:
        for path in result["INCLUDE"]:
            path = replace_path(path,replace)
            conf_dict["includePath"].append(path)
    if "DEFINE" in result:
        conf_dict["defines"].extend(result["DEFINE"])
    if "PREINCLUDE" in result:
        for path in result["PREINCLUDE"]:
            path = replace_path(path,replace)
            conf_dict["forcedInclude"].append(path)
    return conf_dict



