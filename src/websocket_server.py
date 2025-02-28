from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import serial
import json
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ECGManager:
    def __init__(self):
        self.active_connections = []
        self.serial_port = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: str):
        for connection in self.active_connections:
            await connection.send_text(data)

manager = ECGManager()

@app.websocket("/ws/ecg")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        ser = serial.Serial('COM3', 9600)  # Adjust port as needed
        while True:
            if ser.in_waiting:
                ecg_data = ser.readline().decode().strip()
                await manager.broadcast(json.dumps({"ecg_value": float(ecg_data)}))
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        manager.disconnect(websocket)