import numpy as np


#CLIENT_URL = 'http://172.16.20.23:8081/'

SAVE_IMG_PATH = '/mnt/xcd/code/ai_test/static/images'  # 图片保存在服务器的实际位置

POST_IMG_PATH1 = 'http://172.16.20.163:5001/images'  # 通过端口映射post发送能够访问的位置 焊接考核科目1
POST_IMG_PATH2 = 'http://172.16.20.163:5002/images' #焊接考核科目2

VIDEO_SOURCE = '/mnt/xcd/code/ai_test/static/videos/1.mp4'  # 视频源路径
#焊接考核视频流
# Define paths to RTSP streams


MODEL_PATH="/mnt/xcd/code/ai_test/weights/ch1_welding_switch_813.pt"



