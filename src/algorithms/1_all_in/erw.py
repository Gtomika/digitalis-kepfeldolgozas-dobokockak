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

IMAGES_DIR = os.path.join(fileDir, 'input_images')

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

def get_image_palette(image):
    pixels = np.float32(image.reshape(-1, 3))

    n_colors = 6
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    return palette


"""def process_image(index, img):
    image = img
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

    hsvImg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

    #multiple by a factor to change the saturation
    hsvImg[...,0] = hsvImg[...,0]*1.4

    #multiple by a factor of less than 1 to reduce the brightness 
    #hsvImg[...,2] = hsvImg[...,2]*0.6

    back = cv2.cvtColor(hsvImg,cv2.COLOR_HSV2BGR)

    cv2.imshow(str(index) + "# Image2", back)"""

def process_image(index, image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5),  sigmaX=1.0, sigmaY=1.0)

    """im_thresh = np.ndarray(blurred.shape, blurred.dtype)
    im_thresh[blurred >= 95] = 255
    im_thresh[blurred < 95] = 0"""

    edges = cv2.Canny(blurred, 3, 200, None, 3)
    #edges = cv2.Canny(im_thresh, 3, 200, None, 3)

    #cv2.imshow(str(index) + "# im_thresh", im_thresh)
    #cv2.imshow(str(index) + "# blurred", blurred)
    cv2.imshow(str(index) + "# edges", edges)


    _, thresh = cv2.threshold(edges, 10, 255, cv2.THRESH_BINARY)

    im_floodfill = thresh.copy()

    h, w = thresh.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(im_floodfill, mask, (3, 3), 255)
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
    im_out = thresh | im_floodfill_inv

    


    # Display
    #cv2.imshow(str(index) + "# Image", image)
    #cv2.imshow(str(index) + "# Image2", edges)

def sizing_images(path): # Viki
    for root, dirs, files in os.walk(path):
        for name in files:
            img = cv2.imread(os.path.join(root, name))
            print(img.shape)
            img = cv2.resize(img, (img.shape[1]//4, img.shape[0]//4))
            new_root = root.replace('Tesztkepek', 'Tesztkepek_resized')
            if not os.path.exists(new_root):
                os.makedirs(new_root)
            cv2.imwrite(os.path.join(new_root, name), img)
            print(root, name)


if __name__ == '__main__':
    image_paths = get_input_image_paths(IMAGES_DIR)
    print("Images: " + str(image_paths))
    
    images = read_images(image_paths)

    avg_image_size = get_avg_image_size(images)
    print("Average image size: " + str(avg_image_size))

    images = resize_images(images, width = avg_image_size[1], height = avg_image_size[0])
    
    
    for index, image in enumerate(images):
        """if index == 1:
            break"""
        process_image(index + 1, image)
    
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
