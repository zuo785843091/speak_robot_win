# -*- coding: utf-8 -*
from SYN7318_handle import *
import threading, queue, os, signal 
import network
import pi_system
import analysis_command
import MP3_player
import pi_email
import chart
from alarm import alarm

running_mode_dict = {'system_mode'       : 0,
                     'set_network'       : 1,
                     'set_alarm'         : 2,
                     'set_song'          : 3,
                     'set_story'         : 4,
                     'set_online_chart'  : 5,
                     'set_offline_chart' : 6}

# 创建消息队列
syn7318_q               = queue.Queue()
error_q                 = queue.Queue()
oline_command_entry_q   = queue.Queue()
alarm_q                 = queue.Queue()

# 创建全局ThreadLocal对象:
SYN7318_cb              = threading.local()
SYN7318_cb              = SYN7318_call_back()

def robot_init(vol_level, tts_name):
    serial_vol_level(vol_level)
    time.sleep(0.5);
    serial_tts(tts_name, False)   #yi xiao qiang
    serial_tts('哈喽，我是云宝，很高兴为您服务')
    logging.info('哈喽，我是云宝，很高兴为您服务')
    if not network.check_network():
        serial_tts('网络未连接,请检查或设置网络')
        logging.info('网络未连接,请检查或设置网络')
    
def check_thread(error_q, oline_command_entry_q):
    if not error_q.empty():
        thread_name = error_q.get()[1]
        if thread_name == 'SYN7813':
            logging.info('SYN7318 thread restarted')
            status_t = pi_sys.start_thread(syn7318_handle.receive_status, error_q, 'receive_status_Thread')
        elif thread_name == 'mp3':
            logging.info('mp3 thread restarted')
            status_t = pi_sys.start_thread(mp3.play_mp3, error_q, 'MP3_status_Thread')
        elif thread_name == 'email':
            logging.info('email thread restarted')
            status_t = pi_sys.start_thread(pi_email.receive_email_t, error_q, 'email_status_Thread')
        elif thread_name == 'alarm':
            logging.info('alarm thread restarted')
            status_t = pi_sys.start_thread(pi_alarm.alarm_handle, error_q, 'alarm_status_Thread')
        elif thread_name == 'online_chart':
            logging.info('online_chart thread restarted')
            chart_status_t = pi_sys.start_thread(chart_d.online_chart_mode, (error_q, oline_command_entry_q), 'online_chart_status_Thread')
    
    
try:
    
    current_run_mode = running_mode_dict['system_mode']
    #初始词典
    current_dict_no = SYN7318_dict['system']
    #创建在线聊天
    chart_d  = chart.dialogue(current_dict_no)
    pi_sys   = pi_system.pi_system()
    mp3      = MP3_player.player(current_dict_no, 'song')
    pi_alarm = alarm(current_dict_no, alarm_q)
    syn7318_handle = SYN7318_handles(SYN7318_cb, syn7318_q)
    # 打开SYN7318返回处理线程
    receive_status_t      = pi_sys.start_thread(syn7318_handle.receive_status, error_q, 'receive_status_Thread')
    # 打开 mp3 处理线程
    song_status_t         = pi_sys.start_thread(mp3.play_mp3, error_q, 'MP3_status_Thread')
    # 打开 email 处理进程
    email_status_t        = pi_sys.start_thread(pi_email.receive_email_t, error_q, 'email_status_Thread')
    # 打开 alarm 处理进程
    alarm_status_t        = pi_sys.start_thread(pi_alarm.alarm_handle, error_q, 'alarm_status_Thread')
    # 打开 online_chart 处理进程
    online_chart_status_t = pi_sys.start_thread(chart_d.online_chart_mode, (error_q, oline_command_entry_q), 'online_chart_status_Thread')
    #初始化机器人
    #robot_init(int(pi_sys.config_data['vol_level']), pi_sys.config_data['tts_name'])
    #初次开机设为唤醒模式
    SYN7318_cb.is_wake_up_succeed = True
    start_time = time.time()
    stop_wake_up()
    while True:
        check_thread(error_q, oline_command_entry_q)
        #pi_sys.net_flag = network.check_network()
        if not pi_email.email_q.empty():         # 处理邮件信息
            [email_command, email_data] = pi_email.email_q.get()            
            analysis_command.analysis_content(email_command, email_data, pi_sys, mp3, pi_alarm)
        
        if not oline_command_entry_q.empty():          # 在线命令词解析
            [SYN7318_cb.iat_state, SYN7318_cb.command_id, SYN7318_cb.entry_id] = oline_command_entry_q.get()
        
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
            '''
                      模拟离线识别
            SYN7318_cb.iat_state = int(input('iat_state:'))
            SYN7318_cb.command_id = int(input('command_id:'))
            SYN7318_cb.entry_id = int(input('entry_id:'))
            '''
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
                    serial_tts('好啊，你想和我说什么呢')
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
    syn7318_q.put(1)          # 发送SYN7318处理线程结束信号
    alarm_q.put(1)   # 发送alarm线程结束信号
    receive_status_t.join()   # 等待SYN7318处理线程结束，释放串口
    stop_wake_up()
    ser.close()
    print('thread %s ended.' % threading.current_thread().name)
    pi_sys.restart_program()  # 程序异常退出时重新启动程序
    os.kill(os.getpid(), signal.SIGTERM)
