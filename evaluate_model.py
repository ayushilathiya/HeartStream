import torch
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from src.models.ecgnet import ECGNet
from src.models.data_loader import get_data_loaders

def load_trained_model(model_path, num_classes=5, device='cuda'):
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            "Please ensure you have trained the model first using train_ecgnet.py"
        )
    
    model = ECGNet(num_classes=num_classes)
    model.load_state_dict(torch.load(model_path))
    model = model.to(device)
    model.eval()
    return model

def plot_confusion_matrix(cm, class_names, save_path):
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(save_path)
    plt.close()

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Check multiple possible model locations
    possible_paths = [
        'best_model.pth',  # Root directory
        os.path.join('models', 'best_model.pth'),  # models subdirectory
        os.path.join(os.getcwd(), 'best_model.pth'),  # Absolute path
        os.path.join(os.getcwd(), 'models', 'best_model.pth')  # Absolute path in models dir
    ]
    
    # Find first available model file
    model_path = None
    for path in possible_paths:
        if os.path.exists(path):
            model_path = path
            print(f"Found model at: {path}")
            break
    
    if model_path is None:
        st.error("Model file not found! Please ensure the model file exists.")
        print("Searched in following locations:")
        for path in possible_paths:
            print(f"- {os.path.abspath(path)}")
        return
    
    try:
        model = load_trained_model(model_path, device=device)
        print(f"Successfully loaded model from {model_path}")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return
    
    # Load test data
    data_dir = os.path.join(os.getcwd(), 'data', 'mitbih')
    _, test_loader = get_data_loaders(data_dir, batch_size=32)
    
    # Make predictions
    predictions = []
    true_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.numpy())
    
    # Convert to numpy arrays
    predictions = np.array(predictions)
    true_labels = np.array(true_labels)
    
    # Calculate metrics
    class_names = ['Normal', 'LBBB', 'RBBB', 'APB', 'PVC']
    cm = confusion_matrix(true_labels, predictions)
    report = classification_report(true_labels, predictions, target_names=class_names)
    
    # Create results directory
    os.makedirs('results', exist_ok=True)
    
    # Save confusion matrix plot
    plot_confusion_matrix(cm, class_names, 'results/confusion_matrix.png')
    
    # Save detailed report
    with open('results/detailed_evaluation.txt', 'w') as f:
        f.write("Classification Report:\n")
        f.write(report)
        f.write("\n\nConfusion Matrix:\n")
        f.write(str(cm))
    
    print("\nEvaluation completed!")
    print("\nClassification Report:")
    print(report)
    print("\nResults saved in 'results' directory")

if __name__ == "__main__":
    main()
