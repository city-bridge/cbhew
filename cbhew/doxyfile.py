""" Doxyfileの操作を行うクラス
"""
class DoxyFile:
    data:str

    def set_data(self,data:str):
        self.data = data

    def load_file(self,file_path:str):
        with open(file_path,"r") as f:
            self.data = f.read()
    
    def save_file(self,file_path:str):
        with open(file_path,"w") as f:
            f.write(self.data)

    def _corp_key_value(self,key:str):
        """ keyとValueのセットの文字列を分割して取得

        Args:
            key (str): 対象のキー

        Raises:
            ValueError: keyが見つからない場合

        Returns:
            _type_: (str,str,str): (keyの前の文字列,keyとvalueの文字列,valueの後の文字列)
        """
        start = self.data.find("\n"+key)
        if start == -1:
            raise ValueError("key not found")
        start = start + 1
        search_start = start

        while True:
            end = self.data.find("\n", search_start)
            if self.data[end - 1] != "\\":
                break
            search_start = end + 1
        
        return (self.data[:start],self.data[start:end],self.data[end:])
    
    def set_key_value(self,key_str:str,value_list:list):
        """ keyの値を設定

        Args:
            key_str (str): keyの文字列
            value_list (list): valueのリスト

        Raises:
            ValueError: keyが見つからない場合
        """
        pre_text, key_val_str, after_text = self._corp_key_value(key_str)
        eq_pos = key_val_str.find("=")
        if eq_pos == -1:
            raise ValueError("'=' not found")
        
        first_line = True
        new_key_val_str = ""
        for val in value_list:
            if first_line:
                line = "{}= {}".format(key_str.ljust(eq_pos, " "), val)
                first_line = False
            else:
                line = " \\\n{}{}".format("".ljust(eq_pos+2, " "), val)
            new_key_val_str += line

        new_key_val_str = new_key_val_str + "\n"
        self.data = pre_text + new_key_val_str + after_text
