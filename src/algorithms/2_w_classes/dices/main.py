from loader import Loader
from dices import Dices
from template_generator import TemplateGenerator
import cv2

loader = None
dices = None

if __name__ == '__main__':
    TemplateGenerator.generate_templates('templates')
    loader = Loader(show_all_steps = False)
    dices = Dices(loader)
    loader.load_image("images/test_image.jpg")

    loader.add_processor(loader.to_grayscale)
    #loader.add_processor(loader.adaptive_threshold)
    loader.add_processor(loader.blur_images)
    loader.add_processor(loader.canny_edges)
    loader.preprocess_images()
    loader.save_images("preprocessed")

    loader.load_image("preprocessed/Image_1_prepocessed.jpg")
    
    dices.process()

    cv2.waitKey(0)
    cv2.destroyAllWindows()