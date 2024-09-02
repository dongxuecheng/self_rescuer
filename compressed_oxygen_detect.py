import torch
import cv2
import threading
from datetime import datetime
from ultralytics import YOLO
from globals import stop_event,redis_client
from config import SAVE_IMG_PATH,POST_IMG_PATH1,VIDEO_SOURCE,MODEL_PATH


def init_compressed_oxygen_detection():
    pass

def start_compressed_oxygen_detection(start_events):
        
    event = threading.Event()
    start_events.append(event)
    thread = threading.Thread(target=process_video, args=(MODEL_PATH,VIDEO_SOURCE,event))
    thread.daemon=True
    thread.start()
    thread.join()


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


            results = model.predict(frame,conf=0.6,verbose=False)

            for r in results:
                boxes = r.boxes.xyxy  # 提取所有检测到的边界框坐标
                confidences = r.boxes.conf  # 提取所有检测到的置信度
                classes = r.boxes.cls  # 提取所有检测到的类别索引

                
                for i in range(len(boxes)):
                    x1, y1, x2, y2 = boxes[i].tolist()
                    confidence = confidences[i].item()
                    cls = int(classes[i].item())
                    label = model.names[cls]
                    print("label:",label)
                #pass
                
                    
                start_event.set()    


        else:
            # Break the loop if the end of the video is reached
            break

        # Release the video capture object and close the display window
    cap.release()
    
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    del model


