import torch
import cv2
import threading
from datetime import datetime
from ultralytics import YOLO
from globals import stop_event,redis_client,steps,hand_box,head_box
from config import VIDEO_SOURCE,MODEL_PATH


def init_compressed_oxygen_detection():
    for i, step in enumerate(steps):
        redis_client.set(f"compressed_oxygen_step_{i+1}",'False')

def start_compressed_oxygen_detection(start_events):
        
    event = threading.Event()
    start_events.append(event)
    thread = threading.Thread(target=process_video, args=(MODEL_PATH,VIDEO_SOURCE,event))
    thread.daemon=True
    thread.start()
    thread.join()

def IoU(box1, box2):
    '''
    计算两个矩形框的交并比
    :param box1: list,第一个矩形框的左上角和右下角坐标
    :param box2: list,第二个矩形框的左上角和右下角坐标
    :return: 两个矩形框的交并比iou
    '''
    x1 = max(box1[0], box2[0])   # 交集左上角x
    x2 = min(box1[2], box2[2])   # 交集右下角x
    y1 = max(box1[1], box2[1])   # 交集左上角y
    y2 = min(box1[3], box2[3])   # 交集右下角y
 
    overlap = max(0., x2-x1) * max(0., y2-y1)
    union = (box1[2]-box1[0]) * (box1[3]-box1[1]) \
            + (box2[2]-box2[0]) * (box2[3]-box2[1]) \
            - overlap
 
    return overlap/union

def process_video(model_path, video_source, start_event):

    
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_source)
    while cap.isOpened():
    # Read a frame from the video
        success, frame = cap.read()
        if stop_event.is_set():#控制停止推理
            break
        if success:
            
            if cap.get(cv2.CAP_PROP_POS_FRAMES) % 10 != 0:#跳帧检测，
                continue

            global step,hand_box,head_box
            results = model.predict(frame,conf=0.6,verbose=False)

            for r in results:
                boxes = r.boxes.xyxy  # 提取所有检测到的边界框坐标
                confidences = r.boxes.conf  # 提取所有检测到的置信度
                classes = r.boxes.cls  # 提取所有检测到的类别索引

                head_box=[0,0,0,0]
                hand_box=[0,0,0,0]
                for i in range(len(boxes)):
                    x1, y1, x2, y2 = boxes[i].tolist()
                    confidence = confidences[i].item()
                    cls = int(classes[i].item())
                    label = model.names[cls]
                    #print("label:",label)

                    if(label=='head'):head_box=[x1,y1,x2,y2]
                    if(label=='hand'):hand_box=[x1,y1,x2,y2]

                    if(label=='aerostat_gasbag'):
                        steps[0]=True
                        print("steps[0]:",steps[0])
                        if(IoU(head_box,[x1,y1,x2,y2])>0.1):
                            steps[2]=True
                            print("steps[2]:",steps[2])

                    if(label=='neckband'):
                        if(IoU(head_box,[x1,y1,x2,y2])>0.1):
                            steps[1]=True
                            print("steps[1]:",steps[1])


                    if(label=='valve'):
                        if(IoU(hand_box,[x1,y1,x2,y2])>0.1):
                            steps[2]=True
                            print("steps[2]:",steps[2])
                    
                    if(label=='air make-up'):
                        steps[0]=True
                        if(IoU(hand_box,[x1,y1,x2,y2])>0.1):
                            steps[4]=True
                            print("steps[4]:",steps[4])

                    if(label=='nose clip'):
                        if(IoU(head_box,[x1,y1,x2,y2])>0.1):
                            steps[5]=True
                            print("steps[5]:",steps[5])
                

                for i, step in enumerate(steps):
                    if step and redis_client.get(f"compressed_oxygen_step_{i+1}")=='False':
                        redis_client.rpush("compressed_oxygen_order", f"{i+1}")
                        redis_client.set(f"compressed_oxygen_step_{i+1}",'True')

                start_event.set()    


        else:
            # Break the loop if the end of the video is reached
            break

        # Release the video capture object and close the display window
    cap.release()
    
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    del model


