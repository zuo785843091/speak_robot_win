# -*- coding: utf-8 -*
import os
import time, re
import ctypes
import ruting_robot
import SYN7318


#import queue
#error_q = queue.Queue()

CHANNELS = 1
RATE = 16000
FRAME_TYPE = 16
CHUNK_DURATION_MS = 20       # supports 10, 20 and 30 (ms)

#libpcmpath = os.path.join(os.getcwd(),"record/libalsa_record.so")
#libpcm = ctypes.CDLL(libpcmpath)

class dialogue(object):
    def __init__(self, dict_no):
        self.smart_home_file_path = '../../syn7318_resource/00词典-智能家居.txt'
        self.song_file_path = '../../syn7318_resource/01词典-歌曲.txt'
        self.story_file_path = '../../syn7318_resource/02词典-点播.txt'
        self.system_file_path = '../../syn7318_resource/03词典-用户1.txt'
        self.offline_answer_file_path = '../../syn7318_resource/offline_answer.txt'
        self.SYN7318_dict_smart_home = self.get_dict(self.smart_home_file_path)
        self.SYN7318_list_song = self.get_list(self.song_file_path)
        self.SYN7318_list_story = self.get_list(self.story_file_path)
        self.SYN7318_dict_system = self.get_dict(self.system_file_path)        
        self.offline_answer_list = self.get_list(self.offline_answer_file_path)
        
        self.SYN7318_inv_dict_system = self.invert_dict(self.SYN7318_dict_system)
        self.dialogue_dict = dict_no
        self.command = 0
        
    def invert_dict(self, d):
        return dict((v,k) for k,v in d.items())
    
    def get_dict(self, file_path):
        SYN7318_dict = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()  # 把末尾的'\n'删掉                
                line_list = re.split(r'\s+', line)
                if len(line_list) >= 2:
                    SYN7318_dict[line_list[0]] = int(line_list[1])
        return SYN7318_dict
                
    def get_list(self, file_path):
        SYN7318_list = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()  # 把末尾的'\n'删掉
                SYN7318_list.append(line)
        return SYN7318_list
    
    def offline_mode(self, entry_id):
        offline_answer = self.offline_answer_dict[entry_id]
        SYN7318.serial_tts(offline_answer)
        return offline_answer
    '''
    def online_chart_mode(self):
        pass
        
        is_get_sentence = libpcm.alsa_vad(RATE, FRAME_TYPE, CHANNELS, CHUNK_DURATION_MS)
        if is_get_sentence == 1:
            os.system('./Linux_voice_1.109/bin/iat_sample')
            with open("iat_result.txt", "rb") as f:        
                words = f.read().decode("utf-8")
        
            i = 0
            #real_words = words.strip() #删除空白符（包括'\n', '\r',  '\t',  ' ')
            real_words = []
            while words[i] != '\x00':
                real_words.append(words[i])
                i += 1
            print(real_words)
            
            if words[0] != '\x00':
                new_words = ruting_robot.robot_main(real_words)
                if not self.is_command(new_words):
                    print(new_words)
                    while SYN7318.GPIO.input(SYN7318.BUSY_KEY):
                        time.sleep(1)
                    SYN7318.serial_tts(new_words, False)
    '''
    # 解析在线命令词
    def get_command_entry(self, word, dict_no):
        flag = False
        iat_state = -1
        command_id = 0
        entry_id = 0
        if dict_no == 0x03:
            if word in self.SYN7318_dict_system:
                flag = True
                iat_state = SYN7318.IAT_ID_SUCCEED
                command_id = self.SYN7318_dict_system[word]
            else:
                flag = False
        if dict_no == 0x01:
            if word in self.SYN7318_list_song:
                flag = True
                iat_state = SYN7318.IAT_NO_ID_SUCCEED
                entry_id = self.SYN7318_list_song.index(word)
            else:
                flag = False
        if dict_no == 0x02:
            if word in self.SYN7318_list_story:
                flag = True
                iat_state = SYN7318.IAT_NO_ID_SUCCEED
                entry_id = self.SYN7318_list_story.index(word)
            else:
                flag = False
            
        return flag, iat_state, command_id, entry_id
           
    def online_chart_mode(self, q = ()):
        error_q = q[0]
        command_entry_q = q[1]
        try:
            while True:
                time.sleep(0.5)
                real_words = input('Please enter words: ')
                # 检测是否为命令词，如果是命令词，则解析命令
                is_command, iat_state, command_id, entry_id = self.get_command_entry(real_words, self.dialogue_dict)
                if is_command:
                    command_entry_q.put([iat_state, command_id, entry_id])
                    print('command:', iat_state, command_id, entry_id)
                if real_words[0] != '\x00' and not is_command:
                    new_words = ruting_robot.robot_main(real_words)                    
                    print(new_words)
                    SYN7318.serial_tts(new_words, False)                    
                
        except BaseException as e:
            error_q.put([e, 'online_chart'])
            SYN7318.logging.error('online_chart error: %s' %(e))



'''
d = dialogue()
d.online_chart_mode(error_q)
'''