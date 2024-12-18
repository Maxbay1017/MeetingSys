from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import numpy as np
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储已知人脸的编码和对应的名字
known_face_encodings = []
known_face_names = []

@app.post("/register")
async def register_face(name: str = Form(...), file: UploadFile = File(...)):
    if file.content_type.startswith("image/") is False:
        raise HTTPException(status_code=400, detail="File is not an image")

    image = face_recognition.load_image_file(file.file)
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) == 0:
        raise HTTPException(status_code=400, detail="No face detected in the image")

    face_encoding = face_encodings[0]
    known_face_encodings.append(face_encoding)
    known_face_names.append(name)

    return JSONResponse(content={"message": "Face registered successfully"})

@app.post("/recognize")
async def recognize_face(file: UploadFile = File(...)):
    if file.content_type.startswith("image/") is False:
        raise HTTPException(status_code=400, detail="File is not an image")

    image = face_recognition.load_image_file(file.file)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    results = []

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        results.append({"name": name, "confidence": 1 - face_distances[best_match_index]})

    return JSONResponse(content={"faces": results})
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)