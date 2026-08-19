from PIL import Image, ImageDraw
import random

def create_random_image(filename):
    img = Image.new('RGB', (224, 224), color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    d = ImageDraw.Draw(img)
    d.text((10,10), filename, fill=(255,255,0))
    img.save(filename)

create_random_image("image1.jpg")
create_random_image("image2.jpg")
print("Created image1.jpg and image2.jpg")
