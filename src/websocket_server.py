from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import serial
import json
import asyncio
import torch
import numpy as np
from collections import deque
from src.models.ecgnet import ECGNet
import os

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
        self.buffer = deque(maxlen=250)  # Buffer for 1 second of data at 250Hz
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model()
        self.class_names = ['Normal', 'LBBB', 'RBBB', 'APB', 'PVC']
        
    def load_model(self):
        try:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'best_model.pth')
            model = ECGNet(num_classes=5)
            model.load_state_dict(torch.load(model_path, map_location=self.device))
            model = model.to(self.device)
            model.eval()
            print(f"Model loaded successfully from {model_path}")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
            
    def preprocess_data(self, data):
        # Normalize the data similar to training
        data = np.array(data)
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            std = 1
        normalized = (data - mean) / std
        return torch.FloatTensor(normalized).reshape(1, 1, -1)
        
    async def analyze_ecg(self, data):
        if len(self.buffer) < 250:
            return None
            
        try:
            with torch.no_grad():
                # Preprocess
                processed_data = self.preprocess_data(list(self.buffer))
                processed_data = processed_data.to(self.device)
                
                # Get model prediction
                outputs = self.model(processed_data)
                probabilities = torch.softmax(outputs, dim=1)
                prediction = torch.argmax(outputs, dim=1).item()
                confidence = probabilities[0][prediction].item()
                
                result = {
                    "prediction": self.class_names[prediction],
                    "confidence": float(confidence),
                    "probabilities": {
                        name: float(prob) 
                        for name, prob in zip(self.class_names, probabilities[0].tolist())
                    },
                    "alert": prediction != 0 and confidence > 0.7  # Alert for non-normal with high confidence
                }
                return result
        except Exception as e:
            print(f"Analysis error: {e}")
            return None

manager = ECGManager()

@app.websocket("/ws/ecg")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        ser = serial.Serial('COM3', 115200)  # Updated baud rate
        while True:
            if ser.in_waiting:
                ecg_data = float(ser.readline().decode().strip())
                manager.buffer.append(ecg_data)
                
                analysis = await manager.analyze_ecg(manager.buffer)
                response = {
                    "ecg_value": ecg_data,
                    "analysis": analysis
                }
                await manager.broadcast(json.dumps(response))
            await asyncio.sleep(0.004)  # Adjusted for 250Hz (1/250)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        manager.disconnect(websocket)