from turtle import width
import PIL
from PIL import Image


def compress_image(image):

    with Image.open(image) as my_image:
        image_height = my_image.height
        image_width = my_image.width
        compressed_image = my_image.resize(
            (image_width, image_height), PIL.Image.NEAREST)

        return compressed_image
