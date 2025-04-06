import wfdb
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
import os

class MITBIHDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.records = []
        self.labels = []
        
        # Load all records
        record_files = [f for f in os.listdir(data_dir) if f.endswith('.hea')]
        
        for record in record_files:
            # Remove .hea extension
            record_name = record[:-4]
            record_path = os.path.join(data_dir, record_name)
            
            # Read record
            signals, fields = wfdb.rdsamp(record_path)
            ann = wfdb.rdann(record_path, 'atr')
            
            # Process signals into segments
            segments = self._process_signals(signals, ann)
            
            self.records.extend(segments)
            self.labels.extend([self._get_beat_label(symbol) for symbol in ann.symbol])
            
        # Convert to numpy arrays
        self.records = np.array(self.records)
        self.labels = np.array(self.labels)
        
        # Standardize the data
        scaler = StandardScaler()
        self.records = scaler.fit_transform(self.records.reshape(-1, self.records.shape[-1])).reshape(self.records.shape)
        
    def _process_signals(self, signals, ann, window_size=250):
        """Extract windows around each annotation"""
        segments = []
        for sample in ann.sample:
            start = max(0, sample - window_size//2)
            end = min(len(signals), sample + window_size//2)
            segment = signals[start:end, 0]  # Using first channel only
            
            # Pad if necessary
            if len(segment) < window_size:
                segment = np.pad(segment, (0, window_size - len(segment)))
                
            segments.append(segment)
        return segments
    
    def _get_beat_label(self, symbol):
        """Convert beat annotations to numeric labels"""
        # MIT-BIH beat types
        beat_types = {
            'N': 0,  # Normal beat
            'L': 1,  # Left bundle branch block beat
            'R': 2,  # Right bundle branch block beat
            'A': 3,  # Atrial premature beat
            'V': 4,  # Premature ventricular contraction
        }
        return beat_types.get(symbol, 0)  # Default to normal if unknown
    
    def __len__(self):
        return len(self.records)
    
    def __getitem__(self, idx):
        signal = self.records[idx]
        label = self.labels[idx]
        
        if self.transform:
            signal = self.transform(signal)
            
        # Add channel dimension and convert to tensor
        signal = torch.FloatTensor(signal).unsqueeze(0)
        return signal, label

def get_data_loaders(data_dir, batch_size=32, train_split=0.8):
    dataset = MITBIHDataset(data_dir)
    
    # Split into train and validation
    train_size = int(train_split * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    return train_loader, val_loader
