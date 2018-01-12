# -*- coding: utf-8 -*
from config_command import config_command
import time
import random
import SYN7318
import logging
logging.basicConfig(level=logging.INFO)

class MP3_mode(config_command):
    def __init__(self, run_times, dict_no, mp3_type = 'song'):
        if mp3_type == 'song':
            self.name = 'song'
            self.config_path = '../config/song_config'
            self.list_path = '../../syn7318_resource/01词典-歌曲.txt'
            self.file_path = 'E:/1-歌曲/'
            self.dict_file_no = 0x01
        elif mp3_type == 'story':
            self.name = 'story'
            self.config_path = '../config/story_config'
            self.list_path = '../../syn7318_resource/02词典-点播.txt'
            self.file_path = 'E:/2-故事/'
            self.dict_file_no = 0x02
        self.index = int(self.get_config(self.config_path, 'index'))        
        self.play_mode = self.get_config(self.config_path, 'play_mode')
        self.list = self.get_list(self.list_path)
        self.file_number = len(self.list)
        self.run_times = run_times
        self.dict_no = dict_no
        self.play_flag = False
    
    def get_list(self, file_path):
        file_list = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()  # 把末尾的'\n'删掉
                file_list.append(line)
        return file_list
    
    def mp3_play_mode(self, command_id, entry_id):
        if self.run_times == 1:
            SYN7318.serial_tts('是否需要点播')
            print('是否需要点播')
            self.play_flag = False
            self.run_times = 2
        elif self.run_times == 2:
            if command_id == 0x01:
                SYN7318.serial_tts('请选择播放内容')
                print('请选择播放内容')
                self.dict_no = self.dict_file_no
                self.run_times = 3
            elif command_id == 0x00:
                self.play_flag = True
            else:                
                SYN7318.serial_tts('请说需要或者不需要')
                print('请说需要或者不需要')
        elif self.run_times == 3:
            if entry_id > self.file_number:
                SYN7318.serial_tts('不好意思，名字不对，请重新确认')
                print('不好意思，名字不对，请重新确认')
                self.run_times = 3
            else:
                self.dict_no = 0x03
                self.index = entry_id
                self.play_flag = True

    def play_mp3(self, error_q):
        try:
            while True:
                #print(self.config_path)
                if self.play_flag:
                    if self.play_mode == '1': #顺序播放
                        self.index += 1
                        if self.index > self.file_number:
                            self.index = 1
                            self.play_flag = False
                    elif self.play_mode == '2': #循环播放
                        self.index = self.index % self.file_number + 1
                    elif self.play_mode == '3': #随机播放
                        self.index = random.randint(1, self.file_number)
                    elif self.play_mode == '4': #单曲循环
                        self.index = self.index
                    elif self.play_mode == '5': #单曲模式
                        self.play_flag = False
                    #把index写入文件
                    self.set_config(self.config_path, 'index', self.index)
                    file_name = self.list[self.index - 1]
                    file_name = self.file_path + file_name + '.mp3'
                    logging.info(file_name)
                    SYN7318.play_mp3(file_name, True)
                time.sleep(3)
        except BaseException as e:
            error_q.put([e, self.name])
            logging.error('%s error: %s' %(self.name, e))

    def set_play_mode(self, play_mode):
        self.play_mode = play_mode
        self.set_config(self, self.config_path, 'play_mode', self.play_mode)
        
    def stop_play(self):
        SYN7318.stop_play()
        self.play_flag = False
'''
song1 = MP3_mode(1, 2, 'story')
print(song1.list)
print(song1.play_mode)
print(song1.index)
print(song1.index)
'''
    