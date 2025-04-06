# ECG Analysis Constants
SAMPLING_RATE = 250  # Hz
WINDOW_SIZE = 250    # 1 second window
MAX_DATA_POINTS = 200
HISTORY_SIZE = 100   # Number of predictions to keep in history
UPDATE_INTERVAL = 1000  # Update interval in milliseconds

# Confidence Thresholds
MIN_CONFIDENCE_THRESHOLD = 0.5
ALERT_CONFIDENCE_THRESHOLD = 0.7

# Critical Conditions that need alerts
CRITICAL_CONDITIONS = ['PVC', 'LBBB', 'RBBB']
