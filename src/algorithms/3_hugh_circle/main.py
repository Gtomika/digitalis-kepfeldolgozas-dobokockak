from os import listdir
from os.path import isfile, join
import cv2
import numpy as np
import math
import os

# Nálam nem működött a relatív útvonal, mert a jelenlegi munkakönyvtár nem ez a 
# a mappa volt, hanem az src mappa. Átírtam úgy az útvonalakat, hogy ott keressék a 
# fájlokat és mappákat, ahol EZ a forrásfájl van.
# Továbbá a / jel helyett mindhol a join függvényt írtam - Tamás
fileDir = os.path.dirname(os.path.realpath(__file__))

IMAGES_DIR = os.path.join(fileDir, "input_images")
MIN_LENGTH = 30
MAX_LENGTH = 100
CIRCULA = 0.06

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

def get_image_palette(image, colors = 6):
    pixels = np.float32(image.reshape(-1, 3))

    n_colors = colors
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    return palette

def distance(p1, p2):
    return math.sqrt(((p2[0] - p1[0])**2) + ((p2[1] - p1[1])**2))

def find_K_nearest(id, point, circles, K = 3):
    nearests = []
    for i in range(0, len(circles)):
        dis = distance(point, circles[i][4])

        if id == circles[i][5] or dis <= 1:
            continue

        if len(nearests) < 3:
            nearests.append((dis, circles[i]))
        else:
            for j in range(0, len(nearests)):
                if dis < nearests[j][0]:
                    nearests[j] = (dis, circles[i])

    return nearests

        

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)

def process_image(index, img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2.0)
    #edges = cv2.Canny(blurred, 200, 255, None, 5, True)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, -5)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)

    #gray = np.zeros([gray.shape[0], gray.shape[1], 3])
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    circles = []
    points = []
    for idx, cnt in enumerate(contours):
        area = cv2.contourArea(cnt, False)
        leng = cv2.arcLength(cnt, False)
        if area != 0.0:
            komp = math.pow(leng, 2) / area
            cirku = 1 / komp

            if cirku > CIRCULA and leng > MIN_LENGTH and leng < MAX_LENGTH:
                cv2.fillPoly(gray, [cnt], color=(255, 0, 0))
                
                M = cv2.moments(cnt)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                cv2.circle(gray, (cX, cY), 2, (0, 0, 255), 3)
                
                circles.append((area, leng, komp, cirku, (cX, cY), idx))

                #cv2.drawContours(gray, [cnt], 0, (0, 0, 0), 2, cv2.LINE_4)

    
    for c in circles:
        nearests = find_K_nearest(c[5], c[4], circles, 3)
        for n in nearests:
            if n[1][3] <= c[3] + 50 and n[1][3] >= c[3] - 50 and     n[1][0] <= c[0] + 100 and n[1][0] >= c[0] - 100:
                cv2.line(gray, c[4], n[1][4], (0, 255, 0), 1)

                    


    # Display
    #cv2.imshow(str(index) + "# Image", img)
    #gray = resize_image(gray, width = 200)
    #edges = resize_image(edges, width = 200)
    cv2.imshow(str(index) + "# BW", gray)
    cv2.imshow(str(index) + "# Adj", thresh)


if __name__ == '__main__':
    image_paths = get_input_image_paths(IMAGES_DIR)
    print("Images: " + str(image_paths))
    
    images = read_images(image_paths)

    avg_image_size = get_avg_image_size(images)
    print("Average image size: " + str(avg_image_size))

    #images = resize_images(images, width = avg_image_size[1], height = avg_image_size[0])
    
    
    for index, image in enumerate(images):

        if index == 7:
            process_image(index + 1, image)
    
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
