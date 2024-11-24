import pathlib
import json
import copy
from cbhew.project_loader import ProjectLoader


def main(hws_path:str, output_path:str ,replace:dict = None, base_vscode_config_path:str = None):
    """ .hwsファイルからVSCode用の設定ファイル出力

    Args:
        hws_path (str): プロジェクトのパス
        output_path (str): 出力先のファイルのパス
        replace (dict): 置換用の辞書
        base_vscode_config_path (str): config1つ分の基本設定のパス
    """
    project_loader = ProjectLoader()
    project_loader.set_replace_dict(replace)
    project_loader.load_project(hws_path)

    base_vscode_config = None
    if base_vscode_config_path is not None:
        with open(base_vscode_config_path, "r",encoding='utf-8') as f:
            base_vscode_config = json.load(f)
    
    hws_configs = project_loader.get_all_configs()
    out_json_dict = hew_config_to_vscode(hws_configs, base_vscode_config)
    output_vscode_setting(output_path,out_json_dict)


def output_vscode_setting(output_dir_path:str,config:dict):
    """VSCode設定ファイルを書き込み

    Args:
        output_dir_path (str): 出力先のディレクトリ
        config (dict): VSCode用の設定

    """
    project_path = pathlib.Path(output_dir_path)    
    output_path=project_path / '.vscode'

    #出力先の確認
    output_path.mkdir(exist_ok=True)
    if not output_path.exists():
        raise Exception("{} is not exists".format(output_path))

    if not output_path.is_dir():
        raise Exception("{} is not dir".format(output_path))

    output_file = output_path / 'c_cpp_properties.json'
    out_json_txt = json.dumps(config,indent=4)
    with output_file.open("w",encoding='s-jis') as f:
        f.write(out_json_txt)


def hew_config_to_vscode(config_list:list, base_vscode_config:dict = None)->dict:
    """HEWの設定をVSCode用の設定に変換

    Args:
        config_list (list): HEWの設定
        base_vscode_config (dict): config1つ分の基本設定

    Returns:
        dict: VSCode用の設定
    """
    vscode_configurations = []
    for hwp_conf in config_list:
        vscode_configurations.append(conv_config_hwp_vscode(hwp_conf, base_vscode_config))
    
    json_dict = {
        "version":4,
        "configurations":vscode_configurations
    }
    return json_dict


def conv_config_hwp_vscode(hwp_conf:dict, base_vscode_config:dict = None)->dict:
    """hwpファイルを読み込んでVSCode用の設定ファイルに変換

    Args:
        hwp_conf (dict): _description_
        base_vscode_config (dict): config1つ分の基本設定

    Returns:
        dict: VSCode用の設定ファイル
    """
    conf_dict = _create_base_vscode_config(base_vscode_config)
    conf_dict["name"] = hwp_conf["name"]
    for path in hwp_conf["include"]:
        path = _replace_path(path)
        conf_dict["includePath"].append(path)
    conf_dict["defines"].extend(hwp_conf["define"])
    for path in hwp_conf["preinclude"]:
        path = _replace_path(path)
        conf_dict["forcedInclude"].append(path)
    return conf_dict

def _replace_path(path:str)->str:
    """パスの置換

    Args:
        path (str): 対象のパス

    Returns:
        str: 置換後のパス
    """

    path = path.replace("\\","/")
    return path

def _create_base_vscode_config(base_vscode_config:dict = None) -> dict:
    """VSCode用の設定ファイルのテンプレートを作成

    Returns:
        dict: VSCode用の設定ファイルのテンプレート
    """
    conf_dict = {}
    if base_vscode_config is not None:
        conf_dict = copy.deepcopy(base_vscode_config)

    default_config = {
        "name":"None",
        "includePath":[
            "${workspaceFolder}/**",
        ],
        "forcedInclude":[],
        "defines":[],
        "cStandard": "gnu17",
    }
    for key in default_config:
        if key not in conf_dict:
            conf_dict[key] = default_config[key]

    return conf_dict