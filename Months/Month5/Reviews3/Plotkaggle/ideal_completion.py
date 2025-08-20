# ideal_completion.py

import matplotlib.pyplot as plt
import os

def generate_plots(epochs, data, title, ylabel, output_filename):
    plt.figure(figsize=(14, 7))
    for model_name, model_data in data.items():
        plt.plot(epochs[model_name], model_data, label=f'Improved {model_name}', marker='o')
    plt.title(f'{title} Comparison')
    plt.xlabel('Epochs')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, f'{output_filename}_comparison.jpeg'), dpi=300)
 

# Create directory if it doesn't exist
output_dir = 'kaggle/working/compare'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Data for models
epochs = {
    'AlexNet': list(range(1, 20)),
    'Inception': list(range(1, 24)),
    'DenseNet': list(range(1, 19)),
    'YOLO': list(range(1, 17))
}

# Populate the data for training and validation loss/accuracy
training_loss = {
    'AlexNet': [0.8725, 0.2801, 0.2033, 0.1614, 0.1422, 0.1210, 0.1037, 0.0917, 0.0851, 0.0768,
                0.0703, 0.0632, 0.0600, 0.0541, 0.0523, 0.0486, 0.0480, 0.0435, 0.0410],
    'Inception': [0.6001, 0.2801, 0.2309, 0.2109, 0.1805, 0.1718, 0.1638, 0.0863, 0.0671, 0.0651,
                  0.0578, 0.0590, 0.0510, 0.0481, 0.0438, 0.0440, 0.0424, 0.0421, 0.0435, 0.0420,
                  0.0420, 0.0429, 0.0418],
    'DenseNet': [1.7195, 0.2675, 0.1485, 0.1060, 0.0820, 0.0672, 0.0580, 0.0486, 0.0420, 0.0378,
                 0.0338, 0.0301, 0.0250, 0.0240, 0.0223, 0.0205, 0.0193, 0.0176],
    'YOLO': [1.2989, 0.1921, 0.1209, 0.0961, 0.0805, 0.0700, 0.0615, 0.0480, 0.0431, 0.0402,
             0.0382, 0.0380, 0.0365, 0.0380, 0.0356, 0.0343]
}
validation_loss = {
    'AlexNet': [0.3588, 0.2205, 0.2068, 0.1375, 0.2050, 0.1579, 0.1275, 0.1340, 0.0930, 0.0845,
                0.0725, 0.0892, 0.0830, 0.0815, 0.0515, 0.0868, 0.0585, 0.0890, 0.0535],
    'Inception': [0.2756, 0.2201, 0.1390, 0.1425, 0.2723, 0.1000, 0.0684, 0.0340, 0.0341, 0.0281,
                  0.0295, 0.0265, 0.0281, 0.0245, 0.0230, 0.0251, 0.0241, 0.0220, 0.0243, 0.0222,
                  0.0241, 0.0220, 0.0235],
    'DenseNet': [0.3829, 0.1405, 0.0810, 0.0685, 0.0489, 0.0414, 0.0325, 0.0349, 0.0265, 0.0223,
                 0.0253, 0.0223, 0.0168, 0.0211, 0.0153, 0.0148, 0.0143, 0.0133],
    'YOLO': [0.1490, 0.0573, 0.0398, 0.0260, 0.0232, 0.0205, 0.0168, 0.0130, 0.0138, 0.0131,
             0.0123, 0.0135, 0.0129, 0.0132, 0.0118, 0.0124]
}
training_accuracy = {
    'AlexNet': [0.7420, 0.9060, 0.9325, 0.9456, 0.9530, 0.9577, 0.9639, 0.9679, 0.9710, 0.9740,
                0.9755, 0.9780, 0.9795, 0.9801, 0.9820, 0.9839, 0.9825, 0.9845, 0.9859],
    'Inception': [0.8210, 0.9090, 0.9260, 0.9305, 0.9440, 0.9440, 0.9470, 0.9715, 0.9790, 0.9785,
                  0.9810, 0.9800, 0.9838, 0.9837, 0.9855, 0.9854, 0.9858, 0.9859, 0.9853, 0.9857,
                  0.9863, 0.9860, 0.9856],
    'DenseNet': [0.6209, 0.9210, 0.9535, 0.9670, 0.9735, 0.9792, 0.9819, 0.9840, 0.9865, 0.9875,
                 0.9895, 0.9904, 0.9921, 0.9921, 0.9930, 0.9933, 0.9940, 0.9943],
    'YOLO': [0.7570, 0.9570, 0.9705, 0.9760, 0.9785, 0.9820, 0.9835, 0.9860, 0.9881, 0.9891,
             0.9900, 0.9905, 0.9907, 0.9898, 0.9903, 0.9910]
}
validation_accuracy = {
    'AlexNet': [0.8775, 0.9253, 0.9299, 0.9544, 0.9319, 0.9475, 0.9555, 0.9552, 0.9684, 0.9717,
                0.9754, 0.9695, 0.9725, 0.9721, 0.9814, 0.9725, 0.9801, 0.9722, 0.9812],
    'Inception': [0.9236, 0.9339, 0.9564, 0.9559, 0.9349, 0.9701, 0.9785, 0.9900, 0.9901, 0.9919,
                  0.9921, 0.9941, 0.9925, 0.9940, 0.9949, 0.9945, 0.9951, 0.9952, 0.9947, 0.9956,
                  0.9946, 0.9954, 0.9948],
    'DenseNet': [0.8962, 0.9583, 0.9755, 0.9781, 0.9830, 0.9859, 0.9902, 0.9889, 0.9910, 0.9923,
                 0.9923, 0.9931, 0.9945, 0.9925, 0.9947, 0.9965, 0.9948, 0.9956],
    'YOLO': [0.9793, 0.9901, 0.9922, 0.9950, 0.9948, 0.9957, 0.9963, 0.9971, 0.9970, 0.9973,
             0.9972, 0.9974, 0.9975, 0.9973, 0.9977, 0.9976]
}

# Generate plots for each metric
generate_plots(epochs, training_loss, 'Training Loss', 'Loss', 'training_loss')
generate_plots(epochs, validation_loss, 'Validation Loss', 'Loss', 'validation_loss')
generate_plots(epochs, training_accuracy, 'Training Accuracy', 'Accuracy', 'training_accuracy')
generate_plots(epochs, validation_accuracy, 'Validation Accuracy', 'Accuracy', 'validation_accuracy')