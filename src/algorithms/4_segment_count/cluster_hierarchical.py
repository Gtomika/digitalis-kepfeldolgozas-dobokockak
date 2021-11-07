import cv2
import numpy as np
import statistics
import scipy.cluster.hierarchy as hcluster

"""
Itt tallálható az a megvalósítás, ami a dobókocka pontjait 
hierarchikus klaszterező algoritmussal próbálja oldalak szerint szétválasztani.
Nem sikerült túl jó eredményt elérnem vele.
"""

# Megszámolja a dobás értékét
# A csoportosítás hierarchical clustering segítségével történik, nem működik valami jól
def count_value_hierarchical(preprocessed_image, original_image, masks, index = 0, display = False) -> int:
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

        # Speciális esetek
        if(len(filtered_keypoints) == 0): # Nincs egyetlen pont sem
            continue
        if(len(filtered_keypoints) == 1): # csak egy pont van, tegyük fel hogy ez a dobókocka tetején
            total_count += 1
            continue

        # Ezt próbáltam állítani, nem igazán segít
        thresh = 90
        X = np.array([list(i.pt) for i in filtered_keypoints])

        labels = hcluster.fclusterdata(X, thresh, criterion="distance")
        centers = calculate_group_centers(X, labels)

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
        # talált klaszterezés középpontok rajzolása
        for center_point in total_centerpoints:
            px = int(center_point[0])
            py = int(center_point[1])
            image_with_keypoints = cv2.circle(image_with_keypoints, (px, py), radius=5, color=(0,255,0), thickness=-1)
        cv2.imshow(str(index) + '. image keypoints', image_with_keypoints)
    return total_count

def calculate_group_centers(points, labels):
    # points: numpy array, N x 2, ahol N a pontok száma
    # labels: minden ponthoz tartalmazza a csoport címkét
    centers = []
    point_map = {}
    for i, point in enumerate(points):
        label = labels[i]
        if label not in point_map:
            point_map[label] = []
        point_map[label].append((point[0], point[1]))
    # point map-ban minden csoport pontjai egy listában vannak
    for group_label in point_map.keys():
        group_points = point_map[group_label]
        x_coordinates = []
        y_coordinates = []
        for group_point in group_points:
            x_coordinates.append(group_point[0])
            y_coordinates.append(group_point[1])
        group_center = (statistics.mean(x_coordinates), statistics.mean(y_coordinates))
        centers.append(group_center)

    return centers

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