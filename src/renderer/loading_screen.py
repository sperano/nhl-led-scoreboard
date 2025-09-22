import os
from PIL import Image, ImageFont, ImageDraw


PATH = "assets/loading/"
VERSION_FONT = ImageFont.truetype("assets/fonts/VGA.ttf", 12)
VERSION_FONT_64 = ImageFont.truetype("assets/fonts/04B_24__.TTF", 8)

class Loading:
    def __init__(self, matrix,__version__):
        self.matrix = matrix
        self.version = __version__

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
        
        if self.matrix.width > 64:
            self.matrix.draw_text(["2%","3%"],f"V{self.version}",VERSION_FONT)
        else:
            self.matrix.draw_text(["0%","1%"],f"V{self.version}",VERSION_FONT_64)
        
        self.matrix.render()
