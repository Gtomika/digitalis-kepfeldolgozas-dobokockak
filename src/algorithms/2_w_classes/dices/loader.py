import cv2
from os import listdir
from os.path import isfile, join
from os import path
import os

class Loader:

    def __init__(self, show_all_steps = False):
        self._images = []
        self._show_all_steps = show_all_steps
        self._processors = []


    def load_images(self, dir):
        self._images = []

        paths = []
        for file in listdir(dir):
            if isfile(join(dir, file)):
                paths.append(dir + "/" + file)

        for p in paths:
            image = cv2.imread(p)
            self._images.append(image)


    def load_image(self, path):
        self._images = []
        image = cv2.imread(path)
        self._images.append(image)


    def show_images(self):
        for i, img in enumerate(self._images):
            cv2.imshow(str(i + 1) + "# Image", img)
    

    def show_image(self, i, img, name, resize = True):
        image = img
        if resize:
            image = self.resize_image(img, height = 300)
        cv2.imshow(str(i + 1) + "# Image " + name, image)


    def to_grayscale(self):
        for i, img in enumerate(self._images):
            self._images[i] = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if self._show_all_steps:
                self.show_image(i, self._images[i], "GRAYSCALE")


    def to_rgb(self):
        for i, img in enumerate(self._images):
            self._images[i] = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            if self._show_all_steps:
                self.show_image(i, self._images[i], "GRAYSCALE")


    def blur_images(self, kernel_size = 9):
        for i, img in enumerate(self._images):
            self._images[i] = cv2.GaussianBlur(img, (kernel_size, kernel_size), 2.0)
            if self._show_all_steps:
                self.show_image(i, self._images[i], "BLURED")


    def canny_edges(self, th1 = 200, th2 = 255):
        for i, img in enumerate(self._images):
            self._images[i] = cv2.Canny(img, th1, th2, None, 5, True)
            if self._show_all_steps:
                self.show_image(i, self._images[i], "EDGES")


    def adaptive_threshold(self, max = 255, block_size = 21, c = -5):
        for i, img in enumerate(self._images):
            self._images[i] = cv2.adaptiveThreshold(img, max, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, c)
            if self._show_all_steps:
                self.show_image(i, self._images[i], "THRESH")


    def save_images(self, path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        new_dir = os.path.join(current_dir, path)
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

        for i, img in enumerate(self._images):
            cv2.imwrite(new_dir + "/Image_" + str(i + 1) + "_prepocessed.jpg", img)


    def preprocess_images(self):
        print("Processing images...")
        for processor in self._processors:
            processor()
        print("Processing done!")


    def add_processor(self, processor):
        self._processors.append(processor)


    def clear_all_processor(self):
        self._processors = []
        
        
    def resize_image(self, image, width = None, height = None, inter = cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image

        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)

        else:
            r = width / float(w)
            dim = (width, int(h * r))

        resized = cv2.resize(image, dim, interpolation = inter)
        return resized


    @property
    def images(self):
        return self._images

