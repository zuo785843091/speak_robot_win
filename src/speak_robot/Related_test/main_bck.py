# -*- coding: utf-8 -*
#from multiprocessing import Process, Queue
from SYN7318_handle import *
import threading, os, signal, sys 
import network
import pi_system
import analysis_command
import MP3_player
import pi_email
import chart
from alarm import alarm
import queue
syn7318_q = queue.Queue()
error_q = queue.Queue()
command_entry_q = queue.Queue()

'''
class SYN7318_call_back(object):
    def __init__(self):
        self.is_receive_succeed = False
        self.is_idel_state = False
        self.is_wake_up_succeed = False
        self.is_init_state = False
        self.iat_state = 0
        self.match_rate = 0
        self.entry_id = 1
        self.command_id = -1
'''
# 创建全局ThreadLocal对象:
SYN7318_cb = threading.local()
SYN7318_cb = SYN7318_call_back()
'''
def get_entry_command_id(frame_data):
    SYN7318_cb.match_rate = frame_data[0]
    SYN7318_cb.entry_id = frame_data[0] * 256 + frame_data[1]
    SYN7318_cb.command_id = frame_data[2] * 256 + frame_data[3]
    return SYN7318_cb.match_rate, SYN7318_cb.entry_id, SYN7318_cb.command_id

def get_entry_id(frame_data):
    SYN7318_cb.match_rate = frame_data[0]
    SYN7318_cb.entry_id = frame_data[1] * 256 + frame_data[2]
    return SYN7318_cb.match_rate, SYN7318_cb.entry_id

def iat_call_back_handle(frame_command, frame_data):
    global SYN7318_cb
    if frame_command == IAT_ID_SUCCEED:
        SYN7318_cb.match_rate, SYN7318_cb.entry_id, SYN7318_cb.command_id = get_entry_command_id(frame_data)
    elif frame_command == IAT_NO_ID_SUCCEED:
        SYN7318_cb.match_rate, SYN7318_cb.entry_id = get_entry_id(frame_data)
    elif frame_command == USER_MUTE_TIMEOUT:
        logging.warning('user mute timeout')
    elif frame_command == USER_VOICE_TIMEOUT:
        logging.warning('user voice timeout')
    elif frame_command == IAT_REFUSED1 or frame_command == IAT_REFUSED2:
        logging.warning('iat refused')
    elif frame_command == IAT_ERROR:
        logging.warning('iat error')
    #start_iat(0x00)
        
def analysis_command_data(frame_command, frame_data):
    global SYN7318_cb
    #lock.acquire()
    try:
        if frame_command == RECEIVE_SUCCEED:
            SYN7318_cb.is_receive_succeed = True
        elif frame_command == IDEL_STATE:
            SYN7318_cb.is_idel_state = True
            set_idel_state(SYN7318_cb.is_idel_state)
            logging.debug('idel_state')
        elif frame_command == WAKE_UP_SUCCEED:
            SYN7318_cb.is_wake_up_succeed = True
            logging.info('wake_up_succeed')
        elif frame_command == WAKE_UP_ERROR:
            SYN7318_cb.is_wake_up_succeed = False
            logging.warning('wake_up_failed')
        elif frame_command in IAT_COMMAND_CALL_BACK:
            SYN7318_cb.iat_state = frame_command
            iat_call_back_handle(frame_command, frame_data)
        elif frame_command == RECEIVE_FAILED:
            SYN7318_cb.is_receive_succeed = False
            logging.warning('receive_failed')
        elif frame_command == IAT_WAKE_UP_STATE or \
             frame_command == PLAY_MP3_STATE or \
             frame_command == UPDATE_DICT_STATE or \
             frame_command == TTS_STATE:
            SYN7318_cb.is_idel_state = False
            set_idel_state(SYN7318_cb.is_idel_state)
        elif frame_command == INIT_SUCCEED:
            SYN7318_cb.is_init_state = True
    finally:
        pass
        #lock.release()

def receive_status(error_q):
    is_frame_start = 1
    is_frame_length = 2
    is_frame_command = 3
    is_frame_end = 4
    frame_status = 0
    try:
        while True:
            if not syn7318_q.empty():
                logging.info('syn7318_receive_status ending!')
                break
            count = ser.inWaiting()
            if count  > 0:
                recv = ser.read(count)
                #print('recv=', recv)
                for i in range(0, count):
                    if recv[i] == ord('\xfc') and frame_status == 0:
                        frame_status = is_frame_start
                        frame_length_str = []
                        frame_data = []
                        continue
                    if frame_status == is_frame_start:
                        frame_length_str.append(recv[i])
                        if len(frame_length_str) >= 2:
                            frame_status = is_frame_length
                            frame_length = frame_length_str[0] * 256 + frame_length_str[1]
                        continue
                    elif frame_status == is_frame_length:
                        frame_command = recv[i]
                        if frame_length > 6:
                            frame_status = 0
                            print('receive error!')
                            continue
                        elif frame_length > 1 and frame_length <= 6:
                            frame_status = is_frame_command
                            continue
                        elif frame_length == 1:
                            frame_status = is_frame_end
                    elif frame_status == is_frame_command:
                        frame_data.append(recv[i])
                        if len(frame_data) >= frame_length - 1:
                            frame_status = is_frame_end
                        else:
                            continue
    
                    if frame_status == is_frame_end:
                        analysis_command_data(frame_command, frame_data)
                        frame_status = 0
            time.sleep(0.01)
    except BaseException as e:
        error_q.put([e, 'SYN7318'])
        logging.error('SYN7318 error: %s' %(e))
'''

def robot_init(vol_level, tts_name):
    serial_vol_level(vol_level)
    time.sleep(0.5);
    serial_tts(tts_name, False)   #yi xiao qiang
    serial_tts('哈喽，我是云宝，很高兴为您服务')
    logging.info('哈喽，我是云宝，很高兴为您服务')
    if not network.check_network():
        serial_tts('网络未连接,请检查或设置网络')
        logging.info('网络未连接,请检查或设置网络')

def start_thread(target_t, args_t, name_t):
    status_t = threading.Thread(target=target_t, args=(args_t,), name=name_t)
    status_t.setDaemon(True)
    status_t.start()
    return status_t
    
def check_thread(error_q, command_entry_q):
    if not error_q.empty():
        thread_name = error_q.get()[1]
        if thread_name == 'SYN7813':
            logging.info('restart SYN7318 thread')
            status_t = start_thread(syn7318_handle.receive_status, error_q, 'receive_status_Thread')
        elif thread_name == 'mp3':
            logging.info('restart song thread')
            status_t = start_thread(mp3.play_mp3, error_q, 'MP3_status_Thread')
        elif thread_name == 'email':
            logging.info('restart email thread')
            status_t = start_thread(pi_email.receive_email_t, error_q, 'email_status_Thread')
        elif thread_name == 'alarm':
            logging.info('restart alarm thread')
            status_t = start_thread(pi_alarm.alarm_handle, error_q, 'alarm_status_Thread')
        elif thread_name == 'online_chart':
            logging.info('restart online_chart thread')
            chart_status_t = start_thread(chart_d.online_chart_mode, (error_q, command_entry_q), 'online_chart_status_Thread')
        
def restart_program():
    python = sys.executable 
    os.execl(python, python, * sys.argv)
    
try:
    SYN7318_dict = {'smart_home'    : 0x00,
                    'song'          : 0x01, 
                    'story'         : 0x02, 
                    'system'        : 0x03, 
                    'number'        : 0x04, 
                    'offline_chart' : 0x05}
    
    command_dict = {'no'                 : 0,
                    'yes'                : 1,
                    'stop'               : 2,
                    'r2'                 : 3,
                    'reduce_vol'         : 4,
                    'add_vol'            : 5,
                    'set_song'           : 6,
                    'set_story'          : 7,
                    'set_chart'          : 8,
                    'r3'                 : 9,
                    'check_net'          : 10,
                    'set_alarm'          : 11,
                    'open_alarm'         : 12,
                    'close_alarm'        : 13,
                    'stop_play'          : 16}
    
    running_mode_dict = {'system_mode'       : 0,
                         'set_network'       : 1,
                         'set_alarm'         : 2,
                         'set_song'          : 3,
                         'set_story'         : 4,
                         'set_online_chart'  : 5,
                         'set_offline_chart' : 6}
    
    current_run_mode = running_mode_dict['system_mode']
    #初始词典
    current_dict_no = SYN7318_dict['system']
    #创建在线聊天
    chart_d  = chart.dialogue(current_dict_no)
    pi_sys   = pi_system.pi_system()
    mp3      = MP3_player.player(current_dict_no, 'song')
    pi_alarm = alarm(current_dict_no)
    syn7318_handle = SYN7318_handles(SYN7318_cb, syn7318_q)
    # 打开SYN7318返回处理线程
    receive_status_t      = start_thread(syn7318_handle.receive_status, error_q, 'receive_status_Thread')
    # 打开 mp3 处理线程
    song_status_t         = start_thread(mp3.play_mp3, error_q, 'MP3_status_Thread')
    # 打开 email 处理进程
    email_status_t        = start_thread(pi_email.receive_email_t, error_q, 'email_status_Thread')
    # 打开 alarm 处理进程
    alarm_status_t        = start_thread(pi_alarm.alarm_handle, error_q, 'alarm_status_Thread')
    # 打开 online_chart 处理进程
    online_chart_status_t = start_thread(chart_d.online_chart_mode, (error_q, command_entry_q), 'online_chart_status_Thread')
    #初始化机器人
    #robot_init(int(pi_sys.config_data['vol_level']), pi_sys.config_data['tts_name'])
    #初次开机设为唤醒模式
    SYN7318_cb.is_wake_up_succeed = True
    start_time = time.time()
    stop_wake_up()
    while True:
        check_thread(error_q, command_entry_q)
        #pi_sys.net_flag = network.check_network()
        if not pi_email.email_q.empty():         # 处理邮件信息
            [email_command, email_data] = pi_email.email_q.get()            
            analysis_command.analysis_content(email_command, email_data, pi_sys, mp3, pi_alarm)
        
        if not command_entry_q.empty():          # 在线命令词解析
            [SYN7318_cb.iat_state, SYN7318_cb.command_id, SYN7318_cb.entry_id] = command_entry_q.get()
        
        # 离线识别
        if SYN7318_cb.is_wake_up_succeed:
            time.sleep(0.5)
            logging.info('inquiry status')
            status_inquiry()
            time.sleep(0.5)
            if SYN7318_cb.is_idel_state:    # 防止打断当前的语音播放，只能等语音播放结束后才能接受下一个命令
                if pi_sys.net_flag == False:
                    start_iat(current_dict_no)
                    while SYN7318_cb.iat_state == 0:
                        time.sleep(0.2)
            #SYN7318_cb.iat_state = int(input('iat_state:'))
            #SYN7318_cb.command_id = int(input('command_id:'))
            #SYN7318_cb.entry_id = int(input('entry_id:'))
            if SYN7318_cb.iat_state == IAT_ID_SUCCEED:
                if SYN7318_cb.command_id == command_dict['no'] or \
                   SYN7318_cb.command_id == command_dict['yes']:
                    is_certain_command = SYN7318_cb.command_id
                elif SYN7318_cb.command_id == command_dict['reduce_vol'] or \
                     SYN7318_cb.command_id == command_dict['add_vol']:
                    vol_level = int(pi_sys.config_data['vol_level']) + (SYN7318_cb.command_id - 4.5) * 2
                    pi_sys.config_data['vol_level'] = str(vol_level)
                    serial_vol_level(vol_level)
                elif SYN7318_cb.command_id == command_dict['set_song']:
                    current_run_mode = running_mode_dict['set_song']
                    mp3.init_player(1, current_dict_no, 'song')                
                elif SYN7318_cb.command_id == command_dict['set_story']:
                    current_run_mode = running_mode_dict['set_story']
                    mp3.init_player(1, current_dict_no, 'story')
                elif SYN7318_cb.command_id == command_dict['set_chart']:
                    serial_tts('你想和我说什么呢')
                    if not network.check_network():   # 离线模式
                        #offline
                        current_run_mode = running_mode_dict['set_offline_chart']
                    else:                             # 在线模式
                        #offline
                        pass
                        #chart_t = threading.Thread(target=chart_modal, name='chart_modal');
                elif SYN7318_cb.command_id == command_dict['check_net']:
                    network.net_work_status()
                elif SYN7318_cb.command_id == 0x11 or SYN7318_cb.command_id == 0x12 or SYN7318_cb.command_id == 0x13:
                    pass
                    #alarm.alarm.set_alarm(SYN7318_cb.command_id)
                elif SYN7318_cb.command_id == command_dict['stop_play']:
                    mp3.stop_play()
                    current_run_mode = running_mode_dict['system_mode']
                else:
                    pass
            elif SYN7318_cb.iat_state == IAT_NO_ID_SUCCEED:
                if current_dict_no == SYN7318_dict['system']:
                    chart_d.offline_chart_mode(SYN7318_cb.entry_id)
                elif current_dict_no == SYN7318_dict['story']:
                    pass
            else:
                pass

            #set_alarm_mode()
            if SYN7318_cb.iat_state == IAT_NO_ID_SUCCEED or SYN7318_cb.iat_state == IAT_ID_SUCCEED:
                if current_run_mode == running_mode_dict['set_song']:                
                    mp3.mp3_play_mode(SYN7318_cb.command_id, SYN7318_cb.entry_id)
                    current_dict_no = mp3.current_dict_no
                    chart_d.dialogue_dict = current_dict_no
                elif current_run_mode == running_mode_dict['set_story']:
                    mp3.mp3_play_mode(SYN7318_cb.command_id, SYN7318_cb.entry_id)
                    current_dict_no = mp3.current_dict_no
                    chart_d.dialogue_dict = current_dict_no
            SYN7318_cb.command_id = -1
            is_certain_command = -1
            SYN7318_cb.iat_state = 0
            
            # 超过一段时间没有正确的语音识别需要重新唤醒
            if time.time() - start_time > 60 * 100:                
                SYN7318_cb.is_wake_up_succeed = False
                start_wake_up(wake_up_name_dict['云宝'])
                
finally:
    syn7318_q.put(1)
    pi_alarm.alarm_q.put(1)
    receive_status_t.join()
    #story_status_t.join()
    #song_status_t.join()
    #email_status_t.join()
    #alarm_status_t.join()
    stop_wake_up()
    ser.close()    
    print('thread %s ended.' % threading.current_thread().name)
    restart_program()
    os.kill(os.getpid(), signal.SIGTERM)
