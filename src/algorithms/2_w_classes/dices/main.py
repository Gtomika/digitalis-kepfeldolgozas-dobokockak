from loader import Loader
from dices import Dices
from template_generator import TemplateGenerator
import cv2
import os

loader = None
dices = None

if __name__ == '__main__':
    # Nálam nem működött a relatív útvonal, mert a jelenlegi munkakönyvtár nem ez a 
    # a mappa volt, hanem az src mappa. Átírtam úgy az útvonalakat, hogy ott keressék a 
    # fájlokat és mappákat, ahol EZ a forrásfájl van.
    # Továbbá a / jel helyett mindhol a join függvényt írtam - Tamás
    fileDir = os.path.dirname(os.path.realpath(__file__))
    templatesPath = os.path.join(fileDir, 'templates')
    TemplateGenerator.generate_templates(templatesPath)
    loader = Loader(show_all_steps = False)
    dices = Dices(loader)
    loader.load_image(os.path.join(fileDir, 'images', 'test_image.jpg'))

    loader.add_processor(loader.to_grayscale)
    #loader.add_processor(loader.adaptive_threshold)
    loader.add_processor(loader.blur_images)
    loader.add_processor(loader.canny_edges)
    loader.preprocess_images()
    loader.save_images(os.path.join(fileDir, 'preprocessed'))

    loader.load_image(os.path.join(fileDir, 'preprocessed', 'Image_1_prepocessed.jpg'))
    
    dices.process(templatesPath)

    cv2.waitKey(0)
    cv2.destroyAllWindows()