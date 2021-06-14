#Object Detecion Libraries
import cv2
import torch
from pathlib import Path
from models.experimental import attempt_load
from utils.datasets import LoadImages
from utils.general import check_img_size, non_max_suppression, scale_coords, set_logging
from utils.plots import colors, plot_one_box
from utils.torch_utils import select_device, time_synchronized

#General Purpose Libraries
import datetime as dt
import time
from time import sleep

#Sensor and Camera Module Libraries 
import smbus
from picamera import PiCamera
from gpiozero import MotionSensor, LED

#A simple python wrapper for the Firebase API.
import pyrebase

#Initialize Firebase
firebaseConfig={"apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": ""}
firebase=pyrebase.initialize_app(firebaseConfig)
db=firebase.database()

#PCF8591 YL-40 Module Definition and Settings
address = 0x48
A0 = 0x40
bus = smbus.SMBus(1)
dark_value=200

#LED Controller Relay Definition and Setting
led = LED(23)
led.on()

#HC-SR501 PIR Module Definition
pir = MotionSensor(24)

#Raspberry Pi Camera Module Definition and Setting
camera = PiCamera()
camera.resolution = (2592, 1944)
camera.framerate = 24
camera.brightness = 50
camera.rotation = 180

#Detecting Objects on the Captured Image from PiCamera by Trained YOLO Model
@torch.no_grad()
def detect():

    save_img = True
    imgsz = 640
    max_det = 1000
    conf_thres = 0.45
    iou_thres = 0.25
    line_thickness=3
    hide_labels=False
    hide_conf=True
    save_conf=True
    augment=True   
    agnostic_nms=True

    # Directories
    path = 'project_files/'
    source = path +'source/image.jpg'
    save_dir = path + 'detected/'
    weights = path + 'model/model.pt'

    # Initialize
    set_logging()
    device = select_device('')
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    names = model.module.names if hasattr(model, 'module') else model.names  # get class names
    if half:
        model.half()  # to FP16
        
    # Set Dataloader
    dataset = LoadImages(source, img_size=imgsz, stride=stride)

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    t0 = time.time()
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment)[0]

        # Apply NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, agnostic=agnostic_nms, max_det=max_det)
        t2 = time_synchronized()

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            p, s, im0, frame = path, '', im0s.copy(), getattr(dataset, 'frame', 0)
            p = Path(p)  # to Path
            save_path = str(save_dir + p.name)  # img.jpg
            txt_path = str(save_dir + 'labels' + p.stem)  # img.txt
            s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                    db.child("ShopList").update({names[int(c)]:int(n)}) #update RealTime Database

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_img:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                        plot_one_box(xyxy, im0, label=label, color=colors(c, True), line_thickness=line_thickness)

            # Print time (inference + NMS)
            print(f'{s}\nDone. ({t2 - t1:.3f}s)')

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
            print(f'Results saved to {save_dir}')

    print(f'Done. ({time.time() - t0:.3f}s)')

def main_loop():

    while True:
        print('Waiting')
        pir.wait_for_motion ()
        print ('Motion Detected')
        pir.wait_for_no_motion ()
        print ('Motion Stopped')
        bus.write_byte(address,A0)
        ldr_value = bus.read_byte(address)
        if (ldr_value > dark_value):
            led.off()
            camera.start_preview()
            sleep(3)
            camera.stop_preview()
            camera.capture('project_files/source/image.jpg')
            led.on()
            detect()

if __name__ == '__main__':
    print('Smart Inventory Tracking with RPi via MobileApp')
    main_loop()
        
        
