# ❤️ HeartStream: AI-Enhanced ECG Monitoring

A real-time AI-powered ECG monitoring system combining IoT hardware, cloud integration, and machine learning for cardiac health insights.

<p align="center">
  <a href="https://github.com/ayushilathiya/HeartStream/issues"><img src="https://img.shields.io/github/issues/ayushilathiya/HeartStream"></a> 
  <a href="https://github.com/ayushilathiya/HeartStream/stargazers"><img src="https://img.shields.io/github/stars/ayushilathiya/HeartStream"></a>
  <a href="https://github.com/ayushilathiya/HeartStream/network/members"><img src="https://img.shields.io/github/forks/ayushilathiya/HeartStream"></a>
  <a href="https://github.com/ayushilathiya/HeartStream/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg">
  </a>
</p>

<p align="center">
  <a href="#-features">Features</a> |
  <a href="#-tech-stack">Tech Stack</a> |
  <a href="#-installation">Installation</a> |
  <a href="#-hardware-setup">Hardware Setup</a> |
  <a href="#-project-structure">Project Structure</a> |
  <a href="#-author">Author</a>
</p>

<p align="center">
  <a href="https://heartstream.streamlit.app"><img src="https://github.com/ayushilathiya/HeartStream/raw/main/docs/demo.gif" alt="HeartStream Demo"></a>
</p>

---

## 🌟 Features

* Real-time ECG signal acquisition using AD8232 + ESP8266
* 250Hz signal sampling & ThingSpeak cloud upload
* R-peak detection and BPM monitoring
* Streamlit-based frontend dashboard
* AI-powered arrhythmia classification (Normal, LBBB, RBBB, PVC, APB)
* 99.7% model accuracy trained on MIT-BIH Arrhythmia Dataset
* Confusion matrix and visual ECG analysis

## 🛠️ Tech Stack

* **Hardware**: AD8232 ECG Sensor, ESP8266 NodeMCU
* **Cloud**: ThingSpeak API
* **Frontend**: Streamlit
* **Backend**: Python (ECG signal processing, BPM calc, WebSockets)
* **AI Model**: Custom ResNet/ECGNet trained on MIT-BIH

## 🚀 Installation

#### Requirements 📋

* Python 3.8+
* Streamlit 1.30.0+
* `requests`, `websocket-client`, `matplotlib`, `scikit-learn`

#### Getting Started 📝

1. Clone the repository:

```bash
https://github.com/ayushilathiya/HeartStream.git
cd HeartStream
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

---

## 🔌 Hardware Setup

### Components Used:

* **ECG Sensor**: AD8232
* **WiFi Module**: ESP8266 NodeMCU
* **Electrodes**: 3-lead
* **Cloud API**: ThingSpeak (2 fields: ECG value, BPM)

### Connections:

| AD8232 Pin | ESP8266 Pin |
| ---------- | ----------- |
| OUT        | A0          |
| GND        | GND         |
| 3.3V       | 3V3         |

### Upload ESP8266 Code:

* Use Arduino IDE or PlatformIO
* Set WiFi, ThingSpeak API, and WebSocket logic as in `/esp8266/heartstream.ino`

### Output:

* ECG values streamed to ThingSpeak + WebSocket
* BPM calculated on-the-fly

---

## 🧠 AI Model Performance

* **Dataset**: MIT-BIH Arrhythmia
* **Samples used**: 48,000+ labeled ECG segments
* **Accuracy**: 99.7%
* **Classes**: Normal, LBBB, RBBB, PVC, APB

<p align="center">
  <img src="https://github.com/ayushilathiya/HeartStream/raw/main/docs/confusion_matrix.png" width="500"/>
</p>

---

## 🗂️ Project Structure

```
HeartStream/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── /esp8266/               # ESP8266 Arduino code for ECG read + WebSocket + ThingSpeak
│   └── heartstream.ino
├── /models/                # Trained AI model (ResNet, ECGNet, etc.)
├── /utils/                 # Signal processing utilities, BPM calculation
├── /data/                  # Sample ECG data (optional)
├── /docs/                  # Images, demo GIFs, confusion matrix, readme assets
└── README.md
```

---

## 👩‍💻 Author

**Ayushi Lathiya**
Electronics & Communication Engineer | Embedded Systems & AI Researcher
🔗 [Portfolio](https://ayushilathiya.xyz) | 🌐 [Live Demo](https://heartstream.streamlit.app) | 💻 [GitHub](https://github.com/ayushilathiya)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
