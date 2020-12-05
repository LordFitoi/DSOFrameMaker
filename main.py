import os
import json
import PIL
from PIL import Image, ImageOps

imageA = Image.open("template.png")
imageB = Image.open("cape_packed2.png")


def get_frame_coords(frame, columns = 3, rows = 2, frame_size = (64, 64)):
    x_pos = (frame % columns) * frame_size[0]
    y_pos = ((frame // columns) % rows) * frame_size[1]

    return x_pos, y_pos, x_pos + frame_size[0], y_pos + frame_size[1]

def get_frame(frame, image, mirror = False):
    left, top, right, bottom = get_frame_coords(frame)
    new_image = image.crop((left, top, right, bottom))
    if mirror: new_image = ImageOps.mirror(new_image)
    return new_image

main_path = os.path.dirname(__file__)
with open(os.path.join(main_path, "config.json"), "r") as jsonfile:
    config = json.load(jsonfile)


for frame, array in config["cape"].items():
    for metadata in array:
        frame_image = get_frame(int(frame), imageB, metadata[3])
        left, top, right, bottom = get_frame_coords(metadata[0], 21, 4)
        x_offset, y_offset = metadata[1:3]
        imageA.paste(frame_image, (left + x_offset, top + y_offset), frame_image)
        
imageA.show()



