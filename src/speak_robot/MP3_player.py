# -*- coding: utf-8 -*
from config_command import config_command
import time
import random
import SYN7318
from logging_config import *

d_play_statue = {'stop' : 0, 'pause' : 1, 'play' : 2}

class player(config_command):
    def __init__(self, current_dict_no, mp3_type = 'song'):
        if mp3_type == 'song':
            self.config_path = '../config/song_config'
            self.list_path = '../../syn7318_resource/01词典-歌曲.txt'
            self.file_path = 'E:/1-歌曲/'
        elif mp3_type == 'story':
            self.config_path = '../config/story_config'
            self.list_path = '../../syn7318_resource/02词典-点播.txt'
            self.file_path = 'E:/2-故事/'
        self.play_index = int(self.get_config(self.config_path, 'play_index'))
        self.play_mode = self.get_config(self.config_path, 'play_mode')
        self.play_list = self.get_list(self.list_path)

        self.totle_file_num = len(self.play_list)        
        self.play_statue = d_play_statue['stop']
        
        self.run_times = 1
        self.current_dict_no = current_dict_no		

    def init_player(self, run_times, current_dict_no, mp3_type = 'song'):
        if mp3_type == 'song':
            self.config_path = '../config/song_config'
            self.list_path = '../../syn7318_resource/01词典-歌曲.txt'
            self.file_path = 'E:/1-歌曲/'
        elif mp3_type == 'story':
            self.config_path = '../config/story_config'
            self.list_path = '../../syn7318_resource/02词典-点播.txt'
            self.file_path = 'E:/2-故事/'
        self.play_index = int(self.get_config(self.config_path, 'play_index'))        
        self.play_mode = self.get_config(self.config_path, 'play_mode')
        self.play_list = self.get_list(self.list_path)
        self.totle_file_num = len(self.play_list)        
        self.play_statue = d_play_statue['stop']        
        self.run_times = run_times
        self.current_dict_no = current_dict_no
    
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
            logging.info('是否需要点播')
            self.play_flag = False
            self.run_times = 2
        elif self.run_times == 2:
            if command_id == 0x01:
                SYN7318.serial_tts('请选择播放内容')
                logging.info('请选择播放内容')
                self.dict_no = 0x01
                self.run_times = 3
            elif command_id == 0x00:
                self.play_flag = True
            else:                
                SYN7318.serial_tts('请说需要或者不需要')
                logging.info('请说需要或者不需要')
        elif self.run_times == 3:
            if entry_id > self.total_file_num:
                SYN7318.serial_tts('不好意思，名字不对，请重新确认')
                logging.info('不好意思，名字不对，请重新确认')
                self.run_times = 3
            else:
                self.play_index = entry_id
                self.play_flag = True

    def play_mp3(self, error_q):
        try:
            wart_for_complete = True
            while True:
                #print(self.config_path)
                if self.play_statue == d_play_statue['play']:
                    if self.play_mode == '1': #顺序播放
                        self.play_index += 1
                        if self.play_index > self.total_file_num:
                            self.play_index = 1
                            self.play_flag = False
                    elif self.play_mode == '2': #循环播放
                        self.play_index = self.play_index % self.total_file_num + 1
                    elif self.play_mode == '3': #随机播放
                        self.play_index = random.randint(1, self.total_file_num)                    
                    elif self.play_mode == '4': #单曲循环
                        self.play_index = self.play_index
                    elif self.play_mode == '5': #单曲模式
                        self.play_flag = False
                    #把index写入文件
                    self.set_config(self.config_path, 'play_index', self.play_index)
                    file_name = self.list[self.play_index - 1]
                    file_name = self.file_path + file_name + '.mp3'
                    logging.info(file_name)
                    #Wait for play complete
                    '''
    				if wart_for_complete:
    					while not GPIO.input(BUSY_KEY):
    						time.sleep(0.5)
    				'''
    
                    if wart_for_complete:
                        while not SYN7318.is_idel_state:
                            time.sleep(0.5)
                            SYN7318.play_mp3(file_name, False)
                time.sleep(2)
        except BaseException as e:
            error_q.put([e, 'mp3'])
            logging.error('mp3 error: %s' %(e))
            
    def set_play_mode(self, play_mode):
        self.play_mode = play_mode
        self.set_config(self, self.config_path, 'play_mode', self.play_mode)
        
    def stop_play(self):
        SYN7318.stop_play()
        self.play_statue = d_play_statue['stop']
        #initialize play paramentes
        '''
		
		'''

    def pause_play(self):
        SYN7318.stop_play()
        self.play_statue = d_play_statue['pause']


    def start_play(self):
        self.play_statue = d_play_statue['play']

    