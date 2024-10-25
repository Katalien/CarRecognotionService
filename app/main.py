from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
import io
import base64
from ultralytics import YOLO
from typing import List
import cv2
import numpy as np

app = FastAPI()
templates = Jinja2Templates(directory="templates/")
model = YOLO('../model/video_capture_yolo.pt')

@app.get("/", response_class=HTMLResponse)
async def index():
    return templates.TemplateResponse("index.html", {"request": {}})


@app.post("/detect/")
async def detect_images(images: List[UploadFile] = File(...)):
    results = []
    for image in images:
        img = Image.open(image.file)
        img_array = np.array(img)

        detections = model(img_array)

        boxes_output = []
        for box in detections[0].boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            boxes_output.append([x1, y1, x2, y2])
            # Draw bounding box on the image
            cv2.rectangle(img_array, (x1, y1), (x2, y2), (255, 0, 0), 2)

        bbox_img = Image.fromarray(img_array)
        buffered = io.BytesIO()
        bbox_img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        results.append({"image": img_str, "boxes": boxes_output})

    return results