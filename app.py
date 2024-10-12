
from flask import Flask, jsonify

import multiprocessing as mp
from config import VIDEO_SOURCE,MODEL_PATH
from compressed_oxygen_detect import process_video
#焊接考核的穿戴
app = Flask(__name__)

# 全局变量
processes = []
stop_event = mp.Event()
#mp.Array性能较高，适合大量写入的场景
steps = mp.Array('b', [False] * 6)  
#mp.Value适合单个值的场景，性能较慢
manager = mp.Manager()
order = manager.list()#用于存储各个步骤的顺序

def reset_shared_variables():
    # 1. 重置 equipment_cleaning_flag
    for i in range(len(steps)):
        steps[i] = False
    
    # 2. 清空 equipment_cleaning_order
    order[:] = []  # 使用切片来清空 ListProxy
# Define the /wearing_detection endpoint
@app.route('/compressed_oxygen_detection', methods=['GET'])
def compressed_oxygen_detection():

    if not any(p.is_alive() for p in processes):  # 防止重复开启检测服务
        stop_event.clear()

        # 使用本地的 start_events 列表，不使用 Manager
        start_events = []  # 存储每个进程的启动事件

        

        start_event = mp.Event()  # 为每个进程创建一个独立的事件
        start_events.append(start_event)  # 加入 start_events 列表

        process = mp.Process(target=process_video, args=(MODEL_PATH, VIDEO_SOURCE, start_event, stop_event, steps, order))
        processes.append(process)
        process.start()
        print("自救器检测子进程运行中")

        app.logger.info('start_equipment_cleaning_detection')
        reset_shared_variables()

        # 等待所有进程的 start_event 被 set
        for event in start_events:
            event.wait()  # 等待每个进程通知它已经成功启动

        return jsonify({"status": "SUCCESS"}), 200

    else:
        app.logger.info("reset_detection already running")
        return jsonify({"status": "ALREADY_RUNNING"}), 200

    


@app.route('/compressed_oxygen_status', methods=['GET']) 
def compressed_oxygen_status():#开始登录时，检测是否需要复位，若需要，则发送复位信息，否则开始焊接检测
    if len(order)==0:
        app.logger.info('compressed_oxygen_order is none')

        return jsonify({"status": "NONE"}), 200
    
    else:           
        json_array = []
        for step in order:
            json_object = {"step": step}
            json_array.append(json_object)

        app.logger.info(json_array)

        return jsonify({"status": "SUCCESS","data":json_array}), 200

               
@app.route('/end_compressed_oxygen_detection', methods=['GET'])
def end_compressed_oxygen_detection():
    #init_compressed_oxygen_detection()
    stop_inference_internal()
    return jsonify({"status": "SUCCESS"}), 200

    

#停止多进程函数的写法
def stop_inference_internal():
    global processes
    if processes:  # 检查是否有子进程正在运行
        stop_event.set()  # 设置停止事件标志，通知所有子进程停止运行
        # 等待所有子进程结束
        for process in processes:
            if process.is_alive():
                process.join()  # 等待每个子进程结束
                print("自救器子进程运行结束")
        
        processes = []  # 清空进程列表，释放资源
        app.logger.info('detection stopped')
        return True
    else:
        app.logger.info('No inference stopped')
        return False

@app.route('/stop_detection', methods=['GET'])
def stop_inference():
    #global inference_thread
    if stop_inference_internal():
        app.logger.info('detection stopped')
        return jsonify({"status": "DETECTION_STOPPED"}), 200
    else:
        app.logger.info('No_detection_running')
        return jsonify({"status": "No_detection_running"}), 200



if __name__ == '__main__':
    # Start the Flask server
    app.run(debug=False, host='127.0.0.1', port=5007)
