# -*- coding: utf-8 -*
import logging
#打印到文件
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-4s %(levelname)-8s %(message)s',
                    filename='myapp.log',
                    filemode='w') #DEBUG, INFO, WARNING, ERROR
#打印到终端
# 定义一个Handler打印INFO及以上级别的日志到sys.stderr 
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
# 设置日志打印格式  
formatter = logging.Formatter('%(name)-4s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
# 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)