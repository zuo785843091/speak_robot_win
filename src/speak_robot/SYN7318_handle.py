# -*- coding: utf-8 -*
from SYN7318 import *

SYN7318_dict = {'smart_home'	: 0x00,
				'song'		  : 0x01, 
				'story'		 : 0x02, 
				'system'		: 0x03, 
				'number'		: 0x04, 
				'offline_chart' : 0x05}

command_dict = {'no'				 : 0,
				'yes'				: 1,
				'stop'			   : 2,
				'r2'				 : 3,
				'reduce_vol'		 : 4,
				'add_vol'			: 5,
				'set_song'		   : 6,
				'set_story'		  : 7,
				'set_chart'		  : 8,
				'r3'				 : 9,
				'check_net'		  : 10,
				'set_alarm'		  : 11,
				'open_alarm'		 : 12,
				'close_alarm'		: 13,
				'stop_play'		  : 16}

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

class SYN7318_handles(object):
	def __init__(self, SYN7318_cb, syn7318_q):
		self.SYN7318_cb = SYN7318_cb
		self.SYN7318_q = syn7318_q
		
	def get_entry_command_id(self, frame_data):
		match_rate = frame_data[0]
		entry_id = frame_data[0] * 256 + frame_data[1]
		command_id = frame_data[2] * 256 + frame_data[3]
		return match_rate, entry_id, command_id
	
	def get_entry_id(self, frame_data):
		match_rate = frame_data[0]
		entry_id = frame_data[1] * 256 + frame_data[2]
		return match_rate, entry_id
	
	def iat_call_back_handle(self, frame_command, frame_data):
		if frame_command == IAT_ID_SUCCEED:
			self.SYN7318_cb.match_rate, self.SYN7318_cb.entry_id, self.SYN7318_cb.command_id = self.get_entry_command_id(frame_data)
		elif frame_command == IAT_NO_ID_SUCCEED:
			self.SYN7318_cb.match_rate, self.SYN7318_cb.entry_id = self.get_entry_id(frame_data)
		elif frame_command == USER_MUTE_TIMEOUT:
			logging.warning('user mute timeout')
		elif frame_command == USER_VOICE_TIMEOUT:
			logging.warning('user voice timeout')
		elif frame_command == IAT_REFUSED1 or frame_command == IAT_REFUSED2:
			logging.warning('iat refused')
		elif frame_command == IAT_ERROR:
			logging.warning('iat error')
		#start_iat(0x00)

	def offline_command_analysis(self, frame_command, frame_data):
		if frame_command == RECEIVE_SUCCEED:
			self.SYN7318_cb.is_receive_succeed = True
		elif frame_command == IDEL_STATE:
			self.SYN7318_cb.is_idel_state = True
			set_idel_state(self.SYN7318_cb.is_idel_state)
			logging.debug('idel_state')
		elif frame_command == WAKE_UP_SUCCEED:
			self.SYN7318_cb.is_wake_up_succeed = True
			logging.info('wake_up_succeed')
		elif frame_command == WAKE_UP_ERROR:
			self.SYN7318_cb.is_wake_up_succeed = False
			logging.warning('wake_up_failed')
		elif frame_command in IAT_COMMAND_CALL_BACK:
			self.SYN7318_cb.iat_state = frame_command
			self.iat_call_back_handle(frame_command, frame_data)
		elif frame_command == RECEIVE_FAILED:
			self.SYN7318_cb.is_receive_succeed = False
			logging.warning('receive_failed')
		elif frame_command == IAT_WAKE_UP_STATE or \
			 frame_command == PLAY_MP3_STATE or \
			 frame_command == UPDATE_DICT_STATE or \
			 frame_command == TTS_STATE:
			self.SYN7318_cb.is_idel_state = False
			set_idel_state(self.SYN7318_cb.is_idel_state)
		elif frame_command == INIT_SUCCEED:
			self.SYN7318_cb.is_init_state = True
			
	def receive_status(self, error_q):
		is_frame_start = 1
		is_frame_length = 2
		is_frame_command = 3
		is_frame_end = 4
		frame_status = 0

		try:
			while True:
				if not self.SYN7318_q.empty():
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
							self.offline_command_analysis(frame_command, frame_data)
							frame_status = 0
				time.sleep(0.01)
		except BaseException as e:
			error_q.put([e, 'SYN7318'])
			logging.error('SYN7318 error: %s' %(e))