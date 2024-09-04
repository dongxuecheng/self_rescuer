import threading
from flask import Flask, jsonify
from compressed_oxygen_detect import init_compressed_oxygen_detection,start_compressed_oxygen_detection
from globals import inference_thread, stop_event,lock,redis_client

#焊接考核的穿戴
app = Flask(__name__)


# Define the /wearing_detection endpoint
@app.route('/compressed_oxygen_detection', methods=['GET'])
def compressed_oxygen_detection():
    global inference_thread#当全局变量需要重新赋值时，需要用global关键字声明

    if inference_thread is None or not inference_thread.is_alive():
        stop_event.clear()#stop_event不用global声明，因为不需要重新赋值，他只是调用了其方法，并没有重新赋值
        
        start_events = []#给每个线程一个事件，让我知道某个线程是否开始检测
        inference_thread = threading.Thread(target=start_compressed_oxygen_detection,args=(start_events,))
        inference_thread.start()
        init_compressed_oxygen_detection()

        # 等待所有YOLO线程开始检测，两个线程检测完毕时，才返回SUCCESS
        for event in start_events:
            event.wait()

        app.logger.info('start_compressed_oxygen_detection')
        return jsonify({"status": "SUCCESS"}), 200
    
    else:
        app.logger.info("start_compressed_oxygen_detection already running")   
        return jsonify({"status": "ALREADY_RUNNING"}), 200
    


@app.route('/compressed_oxygen_status', methods=['GET']) 
def compressed_oxygen_status():#开始登录时，检测是否需要复位，若需要，则发送复位信息，否则开始焊接检测
    #global inference_thread
    if not redis_client.exists('compressed_oxygen_order'):
        app.logger.info('compressed_oxygen_order is none')

        return jsonify({"status": "NONE"}), 200
    
    else:           
        compressed_oxygen_order = redis_client.lrange("compressed_oxygen_order", 0, -1)
        json_array = []
        for step in compressed_oxygen_order:
            json_object = {"step": step}
            json_array.append(json_object)

        app.logger.info(json_array)

        return jsonify({"status": "SUCCESS","data":json_array}), 200

               
@app.route('/end_compressed_oxygen_detection', methods=['GET'])
def end_wearing_exam():
    init_compressed_oxygen_detection()
    return jsonify({"status": "SUCCESS"}), 200

    

def stop_inference_internal():
    global inference_thread
    if inference_thread is not None and inference_thread.is_alive():
        stop_event.set()  # 设置停止事件标志，通知推理线程停止运行
        inference_thread.join()  # 等待推理线程结束
        inference_thread = None  # 释放线程资源
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

# @app.route('/images/<filename>')
# def get_image(filename):
#     app.logger.info('get_image'+filename)
#     #pdb.set_trace()
#     return send_from_directory('static/images', filename)


if __name__ == '__main__':

    # Start the Flask server
    app.run(debug=False, host='127.0.0.1', port=5007)
