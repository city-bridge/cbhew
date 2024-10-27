import pathlib
import pkgutil
import xml.etree.ElementTree as ET
from cbhew.project_loader import ProjectLoader

def main(hws_path:str,output_path:str,replace:dict={}):
    """ .hwpファイルからcppcheck gui用の設定ファイル出力

    Args:
        hws_path (str): プロジェクトのパス
        replace (dict): 置換用の辞書
    """
    project_loader = ProjectLoader()
    project_loader.set_replace_dict(replace)
    project_loader.load_project(hws_path)

    hws_configs = project_loader.get_all_configs()
    to_cppcheck(output_path,hws_configs)
    
def to_cppcheck(output_dir_path_str:str, hws_configs:list):
    out_base = pathlib.Path(output_dir_path_str)
    out_base.mkdir(exist_ok=True)

    for conf in hws_configs:
        tree = ET.ElementTree(load_base_project())
        root = tree.getroot()
        includedir_ele = root.find("includedir")
        if includedir_ele == None:
            includedir_ele = ET.SubElement(root,"includedir")
        for inc_path in conf["include"]:
            print(inc_path)
            dir_ele = ET.SubElement(includedir_ele,"dir")
            dir_ele.attrib["name"] = inc_path

        defines_ele = root.find("defines")
        if defines_ele == None:
            defines_ele = ET.SubElement(root,"defines")
        for def_name in conf["define"]:
            def_ele = ET.SubElement(defines_ele,"define")
            def_ele.attrib["name"] = def_name
        
        paths_ele = root.find("paths")
        if paths_ele == None:
            paths_ele = ET.SubElement(root,"paths")
        for src_dir in to_src_dir_list(conf["files"]):
            path_ele = ET.SubElement(paths_ele,"dir")
            path_ele.attrib["name"] = src_dir

        builddir_ele = root.find("builddir")
        builddir_ele.text = conf["name"]

        out_name = out_base / "{}.cppcheck".format(conf["name"])
        tree.write(str(out_name))

def load_base_project()->ET.Element:
    xml_bytes = pkgutil.get_data('cbhew', 'baseproject.cppcheck')
    xml_text = str(xml_bytes,encoding='utf-8')
    return ET.fromstring(xml_text)

def to_src_dir_list(file_list:list)->list:
    ret = []
    for file_path in file_list:
        dir_path = str(pathlib.Path(file_path).parent)
        if not dir_path in ret:
            ret.append(dir_path)
    return ret