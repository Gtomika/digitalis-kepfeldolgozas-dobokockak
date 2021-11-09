from . import image_utils
import cv2
from os import path
import numpy as np
from . import rectangle
from . import brightness_based

"""
Források:
- Objektum szegmentáló háló GitHub: https://github.com/matterport/Mask_RCNN
- Objektum szegmentáló háló cikk: https://machinelearningknowledge.ai/instance-segmentation-using-mask-rcnn-in-opencv-python/
"""

# Nálam nem működött a relatív útvonal, mert a jelenlegi munkakönyvtár nem ez a 
# a mappa volt, hanem az src mappa. Átírtam úgy az útvonalakat, hogy ott keressék a 
# fájlokat és mappákat, ahol EZ a forrásfájl van.
# Továbbá a / jel helyett mindhol a join függvényt írtam - Tamás
fileDir = path.dirname(path.realpath(__file__))

# Ebben a mappában vannak tesztképek
IMAGES_DIR = path.join(fileDir, 'input_images')

# Ez a fájl tartalmazza az objektum detektáló neurális háló paramétereit
MODEL_PATH = path.join(fileDir, 'neural_network_parameters', 'frozen_inference_graph_coco.pb')
# Ez a fájl tartalmazza az objektum detektáló neurális háló konfigurációját
CONFIG_PATH = path.join(fileDir, 'neural_network_parameters', 'mask_rcnn_inception_v2_coco_2018_01_28.pbtxt')
# Kijelölőszínek, véletlen
HIGHLIGHT_COLORS = np.random.randint(125, 255, (120, 3))
# neurális háló betöltése
model = cv2.dnn.readNetFromTensorflow(MODEL_PATH, CONFIG_PATH)

# Előfeldolgozást végez a képen, majd visszaadja az előfeldolgozott 
# képet, amit utána be lehet adni az algoritmusnak.
def preprocess_image(image, index = 0, display = False):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    #image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    image = cv2.erode(image, kernel)
    image = cv2.blur(image, (5,5))
    if(display):
        cv2.imshow(str(index) + '. image preprocessed', image)
    return image

# Megkeresi a képen a dobókockákat. Visszaadja azokat a maszkokat, ahol az objektumok
# vannak a képen, minden objektumhoz egy maszkot. Ezek listában jönnek vissza.
# - model: Az objektum szegmentáló neurális háló
# - preprocessed: Az előfeldolgozott kép
# - index: Megmondja, hogy ez hányadik kép. Csak akkor van jelentősége ha display = True
# - display: Ha ez True, akkor mutat egy ablakot a részeredményekről
def segment_dices(model, preprocessed, index = 0, display = False):
    # Másolat készítése, amin lehet bemutatni
    display_image = preprocessed.copy()
    height, width, _ = preprocessed.shape
    # Erre képre lesznek rajzolva az objektumok, amiket a háló talál
    black_image = np.zeros((height, width, 3), np.uint8)
    black_image[:] = (0,0,0)
    # A kép előkészítése olyan formába, amit a háló is be tud fogadni
    blob = cv2.dnn.blobFromImage(preprocessed, swapRB=True)
    model.setInput(blob)
    # Beadás a hálónak
    # boxes: az objektumok befoglaló téglalapja
    # masks: az objektumok maszkja
    boxes, masks = model.forward(["detection_out_final", "detection_masks"])
    # ennyi objektumot talált
    no_of_objects = boxes.shape[2]
    # Ebbe gyűjti az objektum maszkokat
    object_masks = []
    # Végigmegy az összes talált objektumon
    for i in range(no_of_objects):
        box = boxes[0, 0, i]
        # Osztálycímke
        class_id = box[1]
        # Megbízhatósági arány
        score = box[2]
        # Ha nem elég megbízható vagy nem kocka, akkor nem kell
        if score < 0.5:
            continue
        #print('Detected object with high confidence: ' + str(int(class_id)))
        rect = rectangle.Rectangle(int(box[3]*width), int(box[4]*height), int(box[5]*width), int(box[6]*height))
        # befoglaló téglalap rajzolása az eredményképre
        cv2.rectangle(display_image, (rect.x, rect.y), (rect.width, rect.height), (255,0,0), 2)
        # maszk elkészítése visszaadáshoz
        object_mask = np.zeros((height, width), np.uint8)
        object_roi = object_mask[rect.y: rect.height, rect.x: rect.width]
        roi_height, roi_width = object_roi.shape
        mask = masks[i, int(class_id)]
        mask = cv2.resize(mask, (roi_width, roi_height))
        _, mask = cv2.threshold(mask, 0.5, 255, cv2.THRESH_BINARY)
        object_mask[rect.y: rect.height, rect.x: rect.width] = mask
        object_masks.append(object_mask)
        # maszk elkészítése bemutatáshoz
        roi = black_image[rect.y: rect.height, rect.x: rect.width]
        roi_height, roi_width, _ = roi.shape
        mask = masks[i, int(class_id)]
        mask = cv2.resize(mask, (roi_width, roi_height))
        _, mask = cv2.threshold(mask, 0.5, 255, cv2.THRESH_BINARY)
        # maszk színezése bemutatáshoz
        contours, _ = cv2.findContours(np.array(mask, np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        color = HIGHLIGHT_COLORS[int(class_id)]
        for cnt in contours:
            cv2.fillPoly(roi, [cnt], (int(color[0]), int(color[1]), int(color[2])))

    # eredmények mutatása
    if(display):
        cv2.imshow(str(index) + '. image results', np.hstack([black_image, display_image]))    
    return object_masks

# Ezt lehet meghívni a GUI-ból. 
def count_dices(image_path: str, show_subresults: bool) -> int:
    #beolvasás
    image = image_utils.read_image(image_path)
    # Átméretezés
    image = cv2.resize(image, (650, 550))
    # fényesítés
    # alpha érték tologatásával lehet egyes képeken javítani, de nincs olyan ami mindenhol jó lenne
    image = cv2.convertScaleAbs(image, alpha=1.2, beta=0)
    # szegmentálás
    object_masks = segment_dices(model, image, index=1, display=show_subresults)
    # feldolgozás a számoláshoz, itt nem túl érdekes a kép ezért sosem mutatja
    preprocessed = preprocess_image(image, index=1, display=False)
    # Ez csinálja fényesség alapján a számolást
    count = brightness_based.count_value_brightness_based(preprocessed, image, object_masks, index=1, display=show_subresults)
    if(show_subresults):
        cv2.waitKey()
        cv2.destroyAllWindows()
    return count


# Main függvény, itt lehet hívni az algoritmusokat
if __name__ == '__main__':
    # Képek beolvasása és átméretezése
    image_paths = image_utils.get_input_image_paths(IMAGES_DIR)
    #print("Images: " + str(image_paths))
    
    images = image_utils.read_images(image_paths)

    # A képek feldolgozása
    for index, image in enumerate(images):
       # Átméretezés
       image = cv2.resize(image, (650, 550))
       # fényesítés
       # alpha érték tologatásával lehet egyes képeken javítani, de nincs olyan ami mindenhol jó lenne
       image = cv2.convertScaleAbs(image, alpha=1.2, beta=0)
       # szegmentálás, ha display-t True-ra állítjátok akkor mutat szép részeredmény képet
       object_masks = segment_dices(model, image, index, display=False)
       # Ezt ha futtatjátok, akkor mutatja az összes egyéni maszkolt objektumot.
       # Figyelem, ez elég sok ablakot hozhat fel.
       """
       for mask_index, object_mask in enumerate(object_masks):
           masked_object = cv2.bitwise_and(image, image, mask = object_mask)
           cv2.imshow(str(index) + '. image object ' + str(mask_index), masked_object)
        """
       # feldolgozás a számoláshoz
       preprocessed = preprocess_image(image, index, display=False)
       # Ez csinálja a K-means módszerrel, nem túl jól
       #count = count_value_k_means(preprocessed, image, object_masks, index, display=True)
       # Ez csinálja a hierarchikus klaasterezés módszerrel, nem túl jól
       #count = count_value_hierarchical(preprocessed, image, object_masks, index, display=True)
       # Ez csinálja fényesség alapján
       count = brightness_based.count_value_brightness_based(preprocessed, image, object_masks, index, display=True)
       # Eredmény
       print(str(index) + '. kép értéke: ' + str(count))

    # Ha vannak ablakok, azok bezárása
    cv2.waitKey(0)
    cv2.destroyAllWindows()

