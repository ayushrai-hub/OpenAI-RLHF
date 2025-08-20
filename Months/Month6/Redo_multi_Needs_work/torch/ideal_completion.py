# ideal_completion.py

from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image
import requests
import torch

def get_boxes(url):
    # Load an image from a URL
    image = Image.open(requests.get(url, stream=True).raw)

    # Load the feature extractor and model
    image_processor = YolosImageProcessor.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection')
    model = YolosForObjectDetection.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection')

    # Preprocess the image and get model inputs
    inputs = image_processor(images=image, return_tensors="pt")

    # Get model outputs
    outputs = model(**inputs)

    # Set a confidence threshold
    confidence_threshold = 0.8

    target_sizes = torch.tensor([image.size[::-1]])  # Image sizes should be in (height, width) format

    results = image_processor.post_process_object_detection(outputs, threshold=confidence_threshold, target_sizes=target_sizes)[0]

    boxes = []

    for _, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        if label.item() == 1:
            boxes.append(box)

    return boxes