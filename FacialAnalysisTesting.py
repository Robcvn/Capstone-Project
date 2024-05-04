from deepface import DeepFace
import cv2
import matplotlib.pyplot as plt
import json

img_path = "CS-4700/deepface/Sample Face Images/Guy smiling.jpg"

frame = cv2.imread(img_path)

plt.imshow(frame)

demography = DeepFace.analyze(img_path, actions = ['emotion'])

demography_json = json.dumps(demography, indent = 4, separators = (". ", " = "))

print(demography_json) 