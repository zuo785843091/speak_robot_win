# coding: utf-8
import os
import re
def main():
    print(os.name)
    file_path = '../../syn7318_resource/00词典-智能家居.txt'
    SYN7318_dict_0 = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()  # 把末尾的'\n'删掉
            line_list = re.split(r'\s+', line)
            SYN7318_dict_0[int(line_list[1])] = line_list[0]
            
        print(SYN7318_dict_0)


if __name__ == '__main__':
    main()