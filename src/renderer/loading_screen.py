import os
from PIL import Image
from images.image_helper import ImageHelper

PATH = "assets/loading/"

class Loading:
    def __init__(self, matrix):
        self.matrix = matrix

	# Check to see if loading image for screen size exists, if not, fall back to 
        # original 64x32 one
      
        img = f"{PATH}/loading-{self.matrix.width}x{self.matrix.height}.png"
        img_ori = f"{PATH}/loading.png"

        if os.path.exists(img):
           self.image = Image.open(img)
        else:
           self.image = Image.open(img_ori)

    def render(self):

        self.matrix.draw_image(
            (0,0),
            self.image
        )
        self.matrix.render()
