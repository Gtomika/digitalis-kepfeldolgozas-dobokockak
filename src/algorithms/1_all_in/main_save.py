from os import listdir
from os.path import isfile, join
import cv2
import numpy as np
import os

# Nálam nem működött a relatív útvonal, mert a jelenlegi munkakönyvtár nem ez a 
# a mappa volt, hanem az src mappa. Átírtam úgy az útvonalakat, hogy ott keressék a 
# fájlokat és mappákat, ahol EZ a forrásfájl van.
# Továbbá a / jel helyett mindhol a join függvényt írtam - Tamás
fileDir = os.path.dirname(os.path.realpath(__file__))

IMAGES_DIR = os.path.join(fileDir, "input_images")

def get_input_image_paths(dir):
    paths = []
    for file in listdir(dir):
        if isfile(join(dir, file)):
            paths.append(os.path.join(dir, file))
    return paths

def read_images(image_paths):
    images = []
    for path in image_paths:
        image = cv2.imread(path)
        images.append(image)
    return images

def get_avg_image_size(images):
    avg_width, avg_height = 0, 0
    for image in images:
        avg_width += image.shape[1]
        avg_height += image.shape[0]
    return (round(avg_height / len(images)), round(avg_width / len(images)))

def resize_image(image, width = None, height = None, inter = cv2.INTER_AREA):
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

def resize_images(images, width = None, height = None):
    if width is None and height is None:
        return images

    resized = []
    for image in images:
        if width is None:
            result = resize_image(image, height = height)
            resized.append(result)

        if height is None:
            result = resize_image(image, width = width)
            resized.append(result)
        
        else:
            result = resize_image(image, width = width, height = height)
            resized.append(result)
    return resized


def process_image(index, img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    image = hsv
    pixels = np.float32(image.reshape(-1, 3))

    n_colors = 6
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    indices = np.argsort(counts)[::-1]   
    freqs = np.cumsum(np.hstack([[0], counts[indices]/float(counts.sum())]))
    rows = np.int_(image.shape[0]*freqs)

    dom_patch = np.zeros(shape=image.shape, dtype=np.uint8)
    for i in range(len(rows) - 1):
        dom_patch[rows[i]:rows[i + 1], :, :] += np.uint8(palette[indices[i]])

        
    low_threshold = -10
    high_threshold = 10
    for p_idx, p in enumerate(palette):
        low = np.array([ p[0], p[1], max(p[2] + low_threshold, 0) ])
        high = np.array([ p[0], p[1], min(p[2] + high_threshold, 255) ])

        mask = cv2.inRange(image, low, high)
        
        print(p)
        print(low)
        print(high)
        print("-" * 20)

        cv2.imshow(str(index) + "# Image mask palette " + str(p_idx), mask)


    # Display
    cv2.imshow(str(index) + "# Image", image)
    cv2.imshow(str(index) + "# Image dominant colors", dom_patch)


if __name__ == '__main__':
    image_paths = get_input_image_paths(IMAGES_DIR)
    print("Images: " + str(image_paths))
    
    images = read_images(image_paths)

    avg_image_size = get_avg_image_size(images)
    print("Average image size: " + str(avg_image_size))

    images = resize_images(images, width = avg_image_size[1], height = avg_image_size[0])
    
    
    for index, image in enumerate(images):
        if index == 1:
            break
        process_image(index + 1, image)
    
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
