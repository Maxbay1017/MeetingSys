import glob

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, HTTPException, Form, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import re
from utils import calculate_ear, calculate_mar, process_frame, shape_to_np, FACIAL_LANDMARKS_IDXS
# import dlib
import os
# from datetime import datetime
from activateTools import get_hardware_info
from activateTools.ActivationSystem import  ActivationSystem

activation_system = ActivationSystem()
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 首次运行初始化
    if not os.path.exists(activation_system.activation_file):
        fingerprint = get_hardware_info()
        activation_key = activation_system.generate_activation_key(fingerprint)
        activation_system.save_activation(activation_key)
        print("Initial activation completed")

    # 验证激活状态
    if not activation_system.validate_activation():
        raise HTTPException(status_code=403, detail="Activation validation failed")

    yield
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



EYE_AR_THRESH = 0.2
MAR_THRESH = 0.3

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         prev_eye_state = 'open'
#         prev_mouth_state = 'closed'
#         while True:
#             data = await websocket.receive_text()
#             print(f"Received data: {data}")
#             match = re.match(r'data:image/jpeg;base64,(.*)', data)
#             if match:
#                 image_b64 = match.group(1)
#                 image_bytes = base64.b64decode(image_b64)
#                 nparr = np.frombuffer(image_bytes, np.uint8)
#                 frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#                 if frame is not None:
#                     is_mouth_open, mar, ear = process_frame(frame, detector, predictor, EYE_AR_THRESH, MAR_THRESH)
#                     if ear < EYE_AR_THRESH:
#                         if prev_eye_state == 'open':
#                             await websocket.send_json({"event": "blink"})
#                             prev_eye_state = 'closed'
#                     else:
#                         prev_eye_state = 'open'
#                     if mar > MAR_THRESH:
#                         if prev_mouth_state == 'closed':
#                             await websocket.send_json({"event": "mouth_open"})
#                             prev_mouth_state = 'open'
#                     else:
#                         prev_mouth_state = 'closed'
#                     await websocket.send_json({
#                         "is_mouth_open": bool(is_mouth_open),
#                         "mar": float(mar),
#                         "ear": float(ear)
#                     })
#                 else:
#                     print("Failed to decode image")
#             else:
#                 print(f"Invalid data format: {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)

# 创建 speaker 目录
SPEAKER_DIR = "speaker"
if not os.path.exists(SPEAKER_DIR):
    os.makedirs(SPEAKER_DIR)


reg_spks_files = []

# 在 FastAPI 启动时，扫描 speaker 目录下的所有音频文件
@app.on_event("startup")
async def startup_event():
    global reg_spks_files
    reg_spks_files = []  # 清空列表
    # 使用 glob 扫描 speaker 目录下的所有 .wav 文件
    for file_path in glob.glob(os.path.join(SPEAKER_DIR, "**", "*.wav"), recursive=True):
        reg_spks_files.append(file_path)
    print("已加载的音频文件:", reg_spks_files)




@app.post("/upload")
async def upload_audio(file: UploadFile):
    try:
        # 获取文件名中的 username
        username = file.filename.split(".")[0]

        # 创建 username 目录
        user_dir = os.path.join(SPEAKER_DIR, username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # 保存文件到 username 目录
        file_path = os.path.join(user_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return JSONResponse(content={"message": "上传成功", "filename": file.filename})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.post("/api/upload")
async def upload_recording(
    name: str = Form(...),
    audio: UploadFile = File(...)
):
    try:
        # 创建用户目录
        user_dir = os.path.join(SPEAKER_DIR, name)
        os.makedirs(user_dir, exist_ok=True)
        
        # # 生成唯一文件名
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}.wav"
        file_path = os.path.join(user_dir, filename)
        
        # 保存音频文件
        with open(file_path, "wb") as buffer:
            buffer.write(await audio.read())
        
        return JSONResponse({
            "status": "success",
            "message": "录音保存成功",
            "file_path": file_path
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"录音保存失败: {str(e)}"
            }
        )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)