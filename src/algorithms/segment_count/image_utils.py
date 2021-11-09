from os import listdir
from os.path import isfile, join
import cv2

# ----------- Beolvasó, átméretező függvények, nem lényegesek az algoritmusok szempontjából ----------------------

def get_input_image_paths(dir):
    paths = []
    for file in listdir(dir):
        if isfile(join(dir, file)):
            paths.append(join(dir, file))
    return paths

def read_images(image_paths):
    images = []
    for path in image_paths:
        image = cv2.imread(path)
        images.append(image)
    return images

def read_image(image_path: str):
    return cv2.imread(image_path)

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
