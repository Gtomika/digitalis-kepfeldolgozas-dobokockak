import cv2
import math
from shape import Shape
from point import Point
import numpy as np
from os import listdir
from os.path import isfile, join    

class Dices:

    def __init__(self, loader):
        self._loader = loader
        self._CIRCULARITY = 0.06
        self._CONTOUR_MIN_LEN = 30
        self._CONTOUR_MAX_LEN = 100
        self._LINE_COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 0), (255, 255, 255)]

    def match_template(self, template_path, image, threshold):
        template = cv2.imread(template_path, 0)
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        return (zip(*loc[::-1]), template)


    def match_templates(self, templates_dir, image, threshold = 0.4):
        items = []
        for file in listdir(templates_dir):
            if isfile(join(templates_dir, file)):
                path = templates_dir + "/" + file
                matches, template = self.match_template(path, image, threshold)
                items.append((matches, template))

        

        print(len(items))

        self._loader.load_image("preprocessed/Image_1_prepocessed.jpg")
        self._loader.to_grayscale()
        self._loader.to_rgb()
        
        for item in items:
            self.show_matches(item[0], item[1], self._loader.images[0])

        self._loader.show_image(124, self._loader.images[0], "rqetwets", False)


    def show_matches(self, matches, template, image):
        w, h = template.shape[::-1]
        
        for pt in matches:
            print("here")
            cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 1)


    def get_contours(self, image):
        contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
        return contours


    def get_contour_shapes(self, contours, image):
        shapes = []
        for i, contour in enumerate(contours):
            contour_area = cv2.contourArea(contour, False)
            contour_length = cv2.arcLength(contour, False)

            if contour_area != 0.0:
                compactness = math.pow(contour_length, 2) / contour_area
                circularity = 1 / compactness

                #if circularity > self._CIRCULARITY and contour_length > self._CONTOUR_MIN_LEN and contour_length < self._CONTOUR_MAX_LEN:
                if contour_length > self._CONTOUR_MIN_LEN and contour_length < self._CONTOUR_MAX_LEN:
                    # Shape center
                    M = cv2.moments(contour)
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])

                    cv2.fillPoly(image, [contour], color = (255, 0, 0))
                    cv2.circle(image, (cX, cY), 2, (0, 0, 255), 3)

                    shape = Shape(i, contour_area, contour_length, compactness, circularity, contour, Point(cX, cY))
                    shapes.append(shape)

            cv2.drawContours(image, [contour], 0, self._LINE_COLORS[3], 1, cv2.LINE_4)

        print(len(shapes))
        # Remove doubles
        # TODO

        return shapes


    def process(self):
        """self._loader.to_grayscale()
        self._loader.adaptive_threshold()

        contours = self.get_contours(self._loader.images[0])

        self._loader.to_rgb()

        shapes = self.get_contour_shapes(contours, self._loader.images[0])

        self._loader.show_image(124, self._loader.images[0], "rqetwets", False)"""

        self._loader.to_grayscale()
        self.match_templates("templates", self._loader.images[0])

    def find_K_nearest(self):
        pass