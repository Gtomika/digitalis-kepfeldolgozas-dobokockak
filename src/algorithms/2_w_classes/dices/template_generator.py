import numpy as np
import cv2
import os

class TemplateGenerator:

    @staticmethod
    def generate_templates(path):
        # Nekem enélkül nem működik, így viszont létrehozza a mappát előtte - Tamás
        if(not os.path.exists(path)):
            os.makedirs(path)

        # ha már megvannak, akkor nem kell újra generálni - Tamás
        if(len(os.listdir(path)) > 0):
            return

        sizes = [s for s in range(32, 256, 16)]
        angles = [a for a in range(0, 180, 15)]

        index = 0
        for size in sizes:
            for angle in angles:
                axes_lengths = [ax for ax in range(10, round(size / 2), 4)]
                for ax in axes_lengths:
                    center = (round(size / 2), round(size / 2))
                    axesLength = (10, ax)

                    image = np.zeros((size, size, 3), dtype = "uint8")
                    image = cv2.ellipse(image, center, axesLength, angle, 0.0, 360.0, (255, 255, 255), 1)

                    imgPath = os.path.join(path, "template_S{}_A{}_AX{}.jpg".format(size, angle, ax))
                    cv2.imwrite(imgPath, image)
                    index += 1
        