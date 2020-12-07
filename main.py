import os
import json
import PIL
from PIL import Image, ImageTk, ImageOps
from tkinter import filedialog, messagebox
from tkinter import *
from tkinter.ttk import *

CURRENT_VERSION = "0.2"

class SpriteManager:
    # Program Properties:
    main_path = os.path.dirname(__file__)
    canvasTitle = f"PaperdollMaker v{CURRENT_VERSION}"
    searchLoad_title = "Select Paperdoll to use"
    searchSave_title = "Select Name and Path to save it"
    
    loadButton_title = "Load File"
    createButton_title = "Create It"
    
    rootsize = "425x420"

    canvasWidth = 400
    canvasHeight = 300

    toolbar_offset = (11, 10)
    preview_offset = (11, 45)
    createbutton_offset = (340, 390)

    filetypes = (('png files', '*.png'),)

    def __init__(self):
        with open(os.path.join(self.main_path, "config.json"), "r") as jsonfile:
            self.config = json.load(jsonfile)
        self.templates = {
            "cape" : {
                "top" : os.path.join(self.main_path, "sources/topcape.png"),
                "bottom" : os.path.join(self.main_path, "sources/bottomcape.png"),
                "mask" : "",
                "offset" : (200, 150),
                "maskframes" : []
            },
            "hat/mask (symmetric)" : {
                "top" : os.path.join(self.main_path, "sources/tophat.png"),
                "bottom" : "",
                "mask" : os.path.join(self.main_path, "sources/handmask.png"),
                "offset" : (200, 150),
                "maskframes" : [25, 35, 46, 56]
            }
            
        }
        self.loadFilePath = None
        self.root = Tk()
        self.root.title(self.canvasTitle)
        self.root.resizable(0,0)
        self.root.geometry(self.rootsize)

        # # ToolBar Label:
        # self.ToolbarLabel = Label()

        # LoadButton:
        self.loadButton = Button(
            self.root,
            text = self.loadButton_title,
            command = self.LoadFile
        )
        self.loadButton.place(
            x = self.toolbar_offset[0],
            y = self.toolbar_offset[1]
        )

        # Option Menu:
        choices = list(self.templates.keys())
        self.type_sprite = StringVar(self.root)
        self.type_sprite.set(choices[0])

        self.optionMenu = Combobox(
            self.root,
            textvariable = self.type_sprite,
            state="readonly",
            width = 20,
            values = choices,
            xscrollcommand = self.drawPreview
        )
        self.optionMenu.place(
            x = self.toolbar_offset[0] + 190,
            y = self.toolbar_offset[1] + 2
        )

        Text = "Paperdoll Type:"
        self.MenuText = Label(
            self.root,
            text = Text,
            justify = LEFT,
            font = ("Arial", 10)
        )
        self.MenuText.place(
            x = self.toolbar_offset[0] + 90,
            y = self.toolbar_offset[1] + 2
        )

        # Preview Label:
        Text = "Preview:"
        self.PreviewText = Label(self.root, text=Text, justify=LEFT, font=("Arial", 10))
        self.PreviewText.place(
            x = self.preview_offset[0],
            y = self.preview_offset[1]
        )

        self.PreviewLabel= Label(
            self.root,
            relief = "sunken",
            padding=(self.canvasWidth/2, self.canvasHeight/2)
        )
        self.PreviewLabel.place(
            x = self.preview_offset[0],
            y = self.preview_offset[1] + 20
        )

        # Canvas:
        self.Canvas = Canvas(
            self.PreviewLabel,
            width = self.canvasWidth - 20, 
            height = self.canvasHeight - 20
        )
        self.Canvas.place(x=10, y=10)

        # Create Button:
        self.createButton = Button(
            self.root,
            text = self.createButton_title,
            command = self.SaveFile
        )
        self.createButton.place(
            x = self.createbutton_offset[0],
            y = self.createbutton_offset[1]
        )
        
        self.root.mainloop()
        self.drawPreview()

    def searchPathFile(self, savemode = False):
        if savemode:
            filePath = filedialog.asksaveasfilename(
                initialdir = self.main_path, 
                title = self.searchSave_title,
                filetypes = self.filetypes
            )
            
        else:
            filePath = filedialog.askopenfilename(
                initialdir = self.main_path, 
                title = self.searchLoad_title,
                filetypes = self.filetypes
            )
        return filePath

    def LoadFile(self):
        filePath = self.searchPathFile()
        self.loadFilePath = filePath
        self.drawPreview()


    def SaveFile(self):
        filePath = self.searchPathFile(True)
        if self.loadFilePath:
            new_sprite = self.createSprite(self.loadFilePath)
            new_sprite.save(f"{filePath}.png")

    def createSprite(self, path):
        new_sprite = PIL.Image.open(os.path.join(self.main_path, "sources/template.png"))
        # new_sprite = PIL.Image.new("RGBA", (64*21, 64*4), (0,0,0,0))
        old_sprite = PIL.Image.open(os.path.join(self.main_path, path))
        mask_path = self.templates[self.optionMenu.get()]["mask"]
        if mask_path: mask_sprite = PIL.Image.open(mask_path)

        for frame, array in self.config[self.optionMenu.get()].items():
            for metadata in array:

                if metadata[0] in self.templates[self.optionMenu.get()]["maskframes"]:
                    mask = mask_sprite
                else: mask = None

                frame_image = self.get_frame(int(frame), old_sprite, metadata[3], mask)
                left, top, right, bottom = self.get_frame_coords(metadata[0], 21, 4)
                x_offset, y_offset = metadata[1:3]

                new_sprite.paste(frame_image, (left + x_offset, top + y_offset), frame_image)
        
        return new_sprite


    def drawPreview(self, *args):
        self.Canvas.delete("all")
        key = self.optionMenu.get()
        if self.loadFilePath:
            path = self.loadFilePath
        else: path = ""

        image_offset = self.templates[key]["offset"]
        image_list = self.createPreview(key, path)
        for image in image_list:
            self.Canvas.create_image(image_offset, image=image)
        self.root.mainloop()
 
    def createPreview(self, key, path):
        path_list = [
            self.templates[key]["top"], path,
            self.templates[key]["bottom"]
        ]
        return [PhotoImage(file = path) for path in path_list]

    @staticmethod
    def saveImage(image, path):
        image.save(path)

    def get_frame_coords(self, frame, columns = 3, rows = 2, frame_size = (64, 64)):
        x_pos = (frame % columns) * frame_size[0]
        y_pos = ((frame // columns) % rows) * frame_size[1]

        return x_pos, y_pos, x_pos + frame_size[0], y_pos + frame_size[1]

    def get_frame(self, frame, image, mirror = False, mask = None):
        left, top, right, bottom = self.get_frame_coords(frame)
        new_image = image.crop((left, top, right, bottom))

        if mask: new_image = PIL.Image.composite(new_image, mask, mask)
        if mirror: new_image = ImageOps.mirror(new_image)
        return new_image


# imageA = Image.open(os.path.join(main_path, "template.png"))
# imageB = Image.open(os.path.join(main_path, "cape_packed2.png"))


# with open(os.path.join(main_path, "config.json"), "r") as jsonfile:
#     config = json.load(jsonfile)


# for frame, array in config["cape"].items():
#     for metadata in array:
#         frame_image = get_frame(int(frame), imageB, metadata[3])
#         left, top, right, bottom = get_frame_coords(metadata[0], 21, 4)
#         x_offset, y_offset = metadata[1:3]
#         imageA.paste(frame_image, (left + x_offset, top + y_offset), frame_image)
        
if __name__ == "__main__": SpriteManager()

