import cv2
import numpy as np
import statistics

"""
Itt tallálható az a megvalósítás, ami a dobókocka pontjait 
K-means algoritmussal próbálja oldalak szerint szétválasztani.
Nem sikerült túl jó eredményt elérnem vele.
"""

def create_blob_detector():
    min_threshold = 50                     
    max_threshold = 200                     
    min_area = 50                          
    max_area = 100
    min_circularity = .3
    min_inertia_ratio = .4

    params = cv2.SimpleBlobDetector_Params()  
    params.filterByArea = False
    params.filterByCircularity = True
    params.filterByInertia = False
    params.minThreshold = min_threshold
    params.maxThreshold = max_threshold
    params.minArea = min_area
    params.maxArea = max_area
    params.minCircularity = min_circularity
    params.minInertiaRatio = min_inertia_ratio

    return cv2.SimpleBlobDetector_create(params)

# Kiválogatja az értékesnek ítélt pontokat
def filter_keypoints(keypoints):
    sizes = []
    for keypoint in keypoints:
        if(keypoint.size >= 10):   
            sizes.append(keypoint.size)
    median = statistics.median(sizes)
    
    filtered_keypoints = []
    for keypoint in keypoints:
        if(abs(keypoint.size - median) < 10):
            filtered_keypoints.append(keypoint)
    return filtered_keypoints

# Megszámolja a dobás értékét
# A csoportosítás k means algoritmussal történik és nem túl jó
def count_value_k_means(preprocessed_image, original_image, masks, index = 0, display = False) -> int:
    detector = create_blob_detector()
    total_keypoints = []
    total_centerpoints = []
    total_count = 0
    # Minden objektumra (maszkra) külön elvégezzük.
    for object_mask in masks:
        # Maszkolt kép, ahol csak ez az egy objektum van
        masked_image = cv2.bitwise_and(preprocessed_image, preprocessed_image, mask=object_mask)
        # Pontok keresése a maszkolt képen
        keypoints = detector.detect(masked_image)
        inverse_image = cv2.bitwise_not(masked_image)
        keypoints_inverse = detector.detect(inverse_image)
        filtered_keypoints = filter_keypoints(keypoints + keypoints_inverse)
        total_keypoints.extend(filtered_keypoints)

        # Ennyi csoportot keres a K-means
        k = 3
        # Speciális esetek
        if(len(filtered_keypoints) == 0): # Nincs egyetlen pont sem
            continue
        if(len(filtered_keypoints) == 1): # csak egy pont van
            total_count += 1
            continue
        if(len(filtered_keypoints) <= 3): # kevés pont van, elég 2 oldalt keresni
            k = 2
        # A pontok csoportosítása, a két jellemző a pontok X és Y koordinátái
        features = np.empty((0,2), float)
        for keypoint in filtered_keypoints:
            features = np.append(features, np.array([[keypoint.pt[0], keypoint.pt[1]]]), axis=0)
        features = np.float32(features)

        # K-means futtatása
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        compactness, labels, centers = cv2.kmeans(features, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Megvan a csoportosítás, most meg kell nézni, hogy melyik csoport közepe van a legmagasabban
        group_with_highest_center = 0
        highest_center = 1000
        for i, group_center in enumerate(centers):
           total_centerpoints.append((group_center[0], group_center[1]))
           if(group_center[1] < highest_center):
               highest_center = group_center[1]
               group_with_highest_center = i

        # Meg kell számolni, hogy ebbe a csoportba mennyi pont tartozik
        count = 0
        for label in labels:
            if label == group_with_highest_center:
                count += 1
        # hozzáadás a teljes értékhez
        total_count += count
    
    if(display):
        # talált pontok rajzolása
        image_with_keypoints = cv2.drawKeypoints(original_image, total_keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        # talált K-means középpontok rajzolása
        for center_point in total_centerpoints:
            px = int(center_point[0])
            py = int(center_point[1])
            image_with_keypoints = cv2.circle(image_with_keypoints, (px, py), radius=5, color=(0,255,0), thickness=-1)
        cv2.imshow(str(index) + '. image keypoints', image_with_keypoints)
    return total_count