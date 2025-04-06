import torch
import os
import json
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
from src.models.ecgnet import ECGNet
from src.models.data_loader import get_data_loaders
from src.models.trainer import train_model, evaluate_model

def main():
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Initialize model
    model = ECGNet(num_classes=5)  # 5 classes for different beat types
    
    # Get data loaders
    data_dir = os.path.join(os.getcwd(), 'data', 'mitbih')  # Updated data path
    train_loader, val_loader = get_data_loaders(data_dir, batch_size=32)
    
    # Create models directory if it doesn't exist
    model_dir = os.path.join(os.getcwd(), 'models')
    os.makedirs(model_dir, exist_ok=True)
    
    # Train model
    trained_model, history = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        num_epochs=50,
        learning_rate=0.001,
        device=device
    )
    
    # Save final model with absolute path
    model_path = os.path.join(model_dir, 'best_model.pth')
    torch.save(trained_model.state_dict(), model_path)
    print(f"Model saved to: {model_path}")
    
    # Evaluate model
    test_results = evaluate_model(trained_model, val_loader, device)
    
    # Generate classification report
    class_names = ['Normal', 'LBBB', 'RBBB', 'APB', 'PVC']
    report = classification_report(
        test_results['true_labels'],
        test_results['predictions'],
        target_names=class_names,
        output_dict=True
    )
    
    # Save evaluation results
    results = {
        'test_accuracy': test_results['test_accuracy'],
        'test_loss': test_results['test_loss'],
        'classification_report': report,
        'confusion_matrix': confusion_matrix(
            test_results['true_labels'],
            test_results['predictions']
        ).tolist()
    }
    
    os.makedirs('results', exist_ok=True)
    with open('results/evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"\nTraining completed! Results saved in 'results' directory")
    print(f"Test Accuracy: {test_results['test_accuracy']:.2f}%")
    print(f"Test Loss: {test_results['test_loss']:.4f}")

if __name__ == "__main__":
    main()
