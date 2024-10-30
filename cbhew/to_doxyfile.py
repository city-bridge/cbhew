import pathlib
import pkgutil
from cbhew.project_loader import ProjectLoader
from cbhew.doxyfile import DoxyFile

def main(hws_path: str, output_path: str, replace: dict = None, base_doxyfile: str = None):
    """ .hwsファイルからcppcheck gui用の設定ファイル出力

    Args:
        hws_path (str): プロジェクトのパス
        output_path (str): 出力先ディレクトリのパス
        replace (dict, optional): 置換用の辞書
        base_doxyfile (str, optional): ベースとなるDoxyfileのパス
    """
    project_loader = ProjectLoader()
    project_loader.set_replace_dict(replace)
    project_loader.load_project(hws_path)

    hws_configs = project_loader.get_all_configs()
    to_doxyfiles(output_path, hws_configs, base_doxyfile)
    
def to_doxyfiles(output_path: str, hws_configs: list, base_doxyfile: str = None):
    """DoxyFileファイル出力

    Args:
        output_path (str): 出力先ディレクトリのパス
        hws_configs (list): hwsの設定リスト
        base_doxyfile (str, optional): ベースとなるDoxyfileのパス
    """
    output_dir_path = pathlib.Path(output_path)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    for config in hws_configs:
        out_file = output_dir_path / "Doxyfile_{}".format(config["name"])
        to_doxyfile(str(out_file), config, base_doxyfile)

def to_doxyfile(output_file_path:str,hws_config:dict,base_doxyfile:str=None):
    """ DoxyFileファイル出力

    Args:
        output_file_path (str): 出力先ファイルのパス
        hws_config (dict): hewの設定
        base_doxyfile (str): ベースとなるDoxyFileのパス
    """
    doxy = DoxyFile()
    if base_doxyfile != None:
        doxy.load_file(base_doxyfile)
    else:
        doxy.set_data(str(pkgutil.get_data("cbhew","Doxyfile"), encoding='utf-8'))

    doxy.set_key_value("PROJECT_NAME", [hws_config["name"]])
    doxy.set_key_value("OUTPUT_DIRECTORY", [hws_config["name"]])
    doxy.set_key_value("INPUT", [_replace_path(path) for path in hws_config["files"]])
    doxy.set_key_value("INCLUDE_PATH", [_replace_path(path) for path in hws_config["include"]])
    doxy.set_key_value("PREDEFINED", [_replace_path(path) for path in hws_config["define"]])

    doxy.save_file(output_file_path)

def _replace_path(path:str)->str:
    """パスの置換

    Args:
        path (str): 対象のパス
        replace (dict): 置換用の辞書

    Returns:
        str: 置換後のパス
    """

    path = path.replace("\\","/")
    return path
