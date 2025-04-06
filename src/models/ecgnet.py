import torch
import torch.nn as nn

class ECGNet(nn.Module):
    def __init__(self, num_classes=5):
        super(ECGNet, self).__init__()
        
        # First Convolutional Block
        self.conv1 = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        
        # Second Convolutional Block
        self.conv2 = nn.Sequential(
            nn.Conv1d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        
        # Third Convolutional Block
        self.conv3 = nn.Sequential(
            nn.Conv1d(64, 128, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        
        # Calculate FC input size dynamically
        self.fc_input_size = self._get_fc_input_size()
        
        # Fully Connected Layers
        self.fc = nn.Sequential(
            nn.Linear(self.fc_input_size, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
        
    def _get_fc_input_size(self):
        # Create dummy input to calculate size
        x = torch.randn(1, 1, 250)  # Assuming input size of 250
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        return x.numel() // x.shape[0]  # Get flattened size
        
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = x.view(x.size(0), -1)  # Flatten
        x = self.fc(x)
        return x
