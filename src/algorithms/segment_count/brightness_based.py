import cv2
import statistics
import numpy as np
import math

"""
Ezek a függvények az alapján próbálják a legfelső oldalt megtalálni, hogy hol a 
legfényesebb a felület a dobókockán.
"""

def create_blob_detector():
    min_threshold = 50                     
    max_threshold = 200                     
    min_area = 10                          
    max_area = 30
    min_circularity = .2
    max_circularity = .4
    min_inertia_ratio = .1

    params = cv2.SimpleBlobDetector_Params()  
    params.filterByArea = False
    params.filterByCircularity = True
    params.filterByInertia = False
    params.minThreshold = min_threshold
    params.maxThreshold = max_threshold
    params.minArea = min_area
    params.maxArea = max_area
    params.minCircularity = min_circularity
    #params.maxCircularity = max_circularity
    params.minInertiaRatio = min_inertia_ratio

    return cv2.SimpleBlobDetector_create(params)

def is_close_to(keypoint, other_keypoints) -> bool:
    min_distance = 10
    for other_keypoint in other_keypoints:
        distance = math.sqrt(math.pow(keypoint.pt[0]-other_keypoint.pt[0],2) + math.pow(keypoint.pt[1]-other_keypoint.pt[1],2))
        if distance <= min_distance:
            return True
    return False

# Kiválogatja az értékesnek ítélt pontokat
def filter_keypoints(keypoints, total_keypoints):
    sizes = []
    for keypoint in keypoints:
        if(keypoint.size >= 10):   
            sizes.append(keypoint.size)
    if(len(sizes) == 0):
        return keypoints
    median = statistics.median(sizes)

    filtered_keypoints = []
    for keypoint in keypoints:
        if(abs(keypoint.size - median) < 10): # legyen normális méretű
            if(not is_close_to(keypoint, total_keypoints+filtered_keypoints)): # legyen valamennyire távol a többitől
                filtered_keypoints.append(keypoint)
    return filtered_keypoints

"""
Feltételezi, hogy a dobókockák felülete világos, a rajtuk lévő pontok pedig sötétek. Feltételezi 
továbbá, hogy a megvilágítás felülről történik.
"""
def count_value_brightness_based(preprocessed_image, original_image, object_masks, index = 0, display = False) -> int:
    display_image = original_image.copy()
    total_keypoints = []
    width, height = preprocessed_image.shape
    black_image = np.zeros((width, height), np.uint8)
    total_count = 0
    # Minden objektumra (maszkra) külön elvégezzük.
    for mask_index, object_mask in enumerate(object_masks):
        # Maszkolt kép, ahol csak ez az egy objektum van
        masked_image = cv2.bitwise_and(preprocessed_image, preprocessed_image, mask=object_mask)
        #cv2.imshow('Image #' + str(index) + ' mask #' + str(mask_index), masked_image)
        # Pontok keresése a maszkolt képen

        # úgy vesszük, hogy ennél sötétebb pixelek ponthoz vagy maszkon kívüli részhez tartoznak, a 
        # világosabbak pedig dobókocka laphoz
        point_color_threshold = 100

        min_side_color = 256
        max_side_color = 0
        for i in range(width):
            for j in range(height):
                pixel = masked_image[i, j]
                if(pixel > point_color_threshold):
                    # ez a pixel a dobókocka felülete
                    #szélsőérték-e?
                    if(pixel > max_side_color):
                        max_side_color = pixel
                        max_side_location = (i, j)
                    if(pixel < min_side_color):
                        min_side_color = pixel

        brightest_side_range = 50
        _, brightest_side_image = cv2.threshold(masked_image, max_side_color-brightest_side_range, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4,4))
        brightest_side_image = cv2.morphologyEx(brightest_side_image, cv2.MORPH_CLOSE, kernel, iterations=3)
        black_image = cv2.bitwise_or(black_image, brightest_side_image)
    
        # kontúr: nem jó
        # hough kördetektálás: nem jó
        #blobok
        #detector = create_blob_detector()
        detector = cv2.SimpleBlobDetector_create()
        keypoints = detector.detect(brightest_side_image)
        inverse_image = cv2.bitwise_not(brightest_side_image)
        keypoints_inverse = detector.detect(inverse_image)
        filtered_keypoints = filter_keypoints(keypoints + keypoints_inverse, total_keypoints)
        total_keypoints.extend(filtered_keypoints)

        total_count += len(filtered_keypoints)
        display_image = cv2.drawKeypoints(display_image, filtered_keypoints, np.array([]), (255,0,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    #cv2.imshow('Image #' + str(index) + ' brightest side of object #' + str(mask_index), brightest_side_image)
    if(display):
        black_image = cv2.cvtColor(black_image, cv2.COLOR_GRAY2BGR)
        cv2.imshow('Image #' + str(index) + ' top points', np.hstack([black_image, display_image]))

    return total_count