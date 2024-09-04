import threading
# 全局变量来控制推理线程
import redis
import time
# 连接到 Redis 服务器
redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0,decode_responses=True)

inference_thread = None
stop_event = threading.Event()
lock=threading.Lock()

###############焊接考核
#为True时，表示某一步骤完成,并保存图片post
steps = [False] * 6
head_box=[0,0,0,0]
hand_box=[0,0,0,0]

# 压缩氧
# 1 = 外壳去掉
# 2 = 脖带戴好 
# 3 = 咬口具
# 4 = 氧气瓶开启
# 5 = 补气
# 6 = 带鼻夹

