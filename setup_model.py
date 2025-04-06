import os
import urllib.request
import wfdb
import zipfile
from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_mitbih():
    """Download and setup MIT-BIH dataset"""
    # Create data directory
    data_dir = os.path.join(os.getcwd(), 'data', 'mitbih')
    os.makedirs(data_dir, exist_ok=True)
    
    # MIT-BIH database records
    records = ['100', '101', '102', '103', '104', '105', '106', '107', 
              '108', '109', '111', '112', '113', '114', '115', '116', 
              '117', '118', '119', '121', '122', '123', '124', '200', 
              '201', '202', '203', '205', '207', '208', '209', '210', 
              '212', '213', '214', '215', '217', '219', '220', '221', 
              '222', '223', '228', '230', '231', '232', '233', '234']

    print("Downloading MIT-BIH Arrhythmia Database...")
    for record in tqdm(records, desc="Downloading records"):
        # Download .dat file
        wfdb.dl_database('mitdb', data_dir, [record])

    print(f"\nDataset downloaded to: {data_dir}")
    return data_dir

def main():
    print("Setting up ECGNet training environment...")
    
    # Check requirements
    try:
        import torch
        import wfdb
        import numpy as np
        from sklearn.preprocessing import StandardScaler
    except ImportError as e:
        print(f"Error: Missing required package - {e.name}")
        print("Please install requirements first: pip install -r requirements.txt")
        return

    # Download dataset
    data_dir = download_mitbih()
    
    # Create model checkpoint directory
    os.makedirs('checkpoints', exist_ok=True)
    
    print("\nSetup complete! You can now train the model using:")
    print("python train_ecgnet.py")
    print("\nMake sure to update the data_dir in train_ecgnet.py to:")
    print(f"data_dir = '{data_dir}'")

if __name__ == "__main__":
    main()
