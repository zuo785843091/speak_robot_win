# -*- coding: utf-8 -*-
# 配置文件（config）读取与写入
import re

class config_command(object):
    def get_all_config(self, file_path):
        config_data = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if line[0] != '#' and line[0] != '\n':
                    line = line.strip()
                    line_list = re.split(r':', line)
                    config_data[line_list[0]] = line_list[1]
        return config_data
    
    def get_config(self, file_path, paramenter_name):
        paramenter_data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if line[0] != '#' and line[0] != '\n':
                    line = line.strip()
                    line_list = re.split(r':', line)
                    if line_list[0] == paramenter_name:
                        paramenter_data = line_list[1]
        return paramenter_data
    
    def set_config(self, file_path, paramenter_name, value):
        lines = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line_list = re.split(r':', line)
                if line_list[0] == paramenter_name:
                    if type(value) != type(line_list):
                        value = [value]
                    line_list[1] = value
                    line = line_list[0] + ':' + ', '.join(map(str,line_list[1])) + '\n'
                lines.append(line)
        with open(file_path, 'w', encoding='utf-8') as f:
            s = ''.join(lines)
            f.write(s)
            
    @staticmethod
    def get_all_command(content):
        command = []
        data = []
        content_list = re.split(r'\r\n', content)
        for line in content_list:
            if line[0] != '#' and line[0] != '\n':
                line = line.strip() #删除空白符（包括'\n', '\r',  '\t',  ' ')
                line_list = re.split(r':', line)
                command.append(line_list[0])
                if len(line_list) >= 2:
                    data.append(line_list[1])
                else:
                    data.append(' ')
        return command, data
