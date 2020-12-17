import os
import json
import PIL
from PIL import Image, ImageTk, ImageOps
from tkinter import filedialog, messagebox
from tkinter import *
from tkinter.ttk import *

CURRENT_VERSION = "16.12.2020"
class SpriteManager:
    # Program Properties:
    main_path = os.path.dirname(__file__)
    canvasTitle = f"DSO PaperMaker v{CURRENT_VERSION}, By: WaffleFitoi"
    searchLoad_title = "Select Paperdoll to use"
    searchSave_title = "Select Name and Path to save it"
    
    loadButton_title = "Load File"
    createButton_title = "Create It"
    
    rootsize = "425x420"

    canvasWidth = 400
    canvasHeight = 300

    toolbar_offset = (11, 10)
    preview_offset = (11, 45)
    image_preview_offset = (200, 150)
    createbutton_offset = (340, 390)

    filetypes = (('png files', '*.png'),)

    def __init__(self):
        with open(os.path.join(self.main_path, "config.json"), "r") as jsonfile:
            offset_dict, metadata = json.load(jsonfile).values()
        
        self.config = offset_dict
        self.templates = metadata

        self.loadFilePath = None
        self.root = Tk()
        self.root.title(self.canvasTitle)
        self.root.resizable(0,0)
        self.root.geometry(self.rootsize)
        try:
            # ToolBar Label:
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

        except TclError: pass

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
            if ".png" in filePath: filePath = filePath[:-4]
            new_sprite = self.createSprite(self.loadFilePath)
            new_sprite.save(f"{filePath}.png")

    def createSprite(self, path):

        key = self.optionMenu.get()

        sprite_type = self.templates[key]
        sprite_size = sprite_type["output_size"]
        new_sprite = PIL.Image.new("RGBA", sprite_size[0], (0,0,0,0))
        old_sprite = PIL.Image.open(os.path.join(self.main_path, path))

        columns, rows = sprite_type["matrix"]

        for frame, array in self.config[key].items():
            for metadata in array:
                if len(metadata) == 5: angle = metadata[4]
                else: angle = 0

                frame_image = self.get_frame(
                    int(frame),
                    old_sprite,
                    columns = columns,
                    rows = rows,
                    mirror = metadata[3],
                    angle90 = float(angle)
                )
                left, top, right, bottom = self.get_frame_coords(
                    metadata[0],
                    sprite_size[1][0],
                    sprite_size[1][1]
                )
                x_offset, y_offset = metadata[1:3]

                new_sprite.paste(frame_image, (left + x_offset, top + y_offset), frame_image)
        
        mask_path = sprite_type["mask"]
        if mask_path:
            mask_sprite = PIL.Image.open(os.path.join(self.main_path, mask_path))
            new_sprite = PIL.Image.composite(new_sprite, mask_sprite, mask_sprite)

        if key == "bow":
            offset, sprite_path = sprite_type["extra"]
            string_sprite = PIL.Image.open(os.path.join(self.main_path, sprite_path))
            new_sprite.paste(string_sprite, offset, string_sprite)
            
        # template = PIL.Image.open(os.path.join(self.main_path, "sources/template.png"))
        # template.paste(new_sprite, (0, 0), new_sprite)
        # new_sprite = template

        return new_sprite

    def drawPreview(self, *args):
        self.Canvas.delete("all")
        key = self.optionMenu.get()
        if self.loadFilePath:
            path = self.loadFilePath
        else: path = ""

        image_list = self.createPreview(key, path)
        for image in image_list:
            self.Canvas.create_image(self.image_preview_offset, image=image)
        self.root.mainloop()
 
    def createPreview(self, key, path):
        path_list = [
            self.templates[key]["top"], path,
            self.templates[key]["bottom"]
        ]

        preview = [
            PhotoImage(file = os.path.join(self.main_path, path))
            for path in path_list if path
        ]

        return preview
        
    @staticmethod
    def saveImage(image, path):
        image.save(path)

    def get_frame_coords(self, frame, columns = 3, rows = 2, frame_size = (64, 64)):
        x_pos = (frame % columns) * frame_size[0]
        y_pos = ((frame // columns) % rows) * frame_size[1]

        return x_pos, y_pos, x_pos + frame_size[0], y_pos + frame_size[1]

    def get_frame(self, frame, image, columns = 3, rows = 2, mirror = False, angle90 = 0):
        left, top, right, bottom = self.get_frame_coords(frame, columns, rows)
        new_image = image.crop((left, top, right, bottom))
        
        # Flip the image
        if mirror: new_image = ImageOps.mirror(new_image)
        
        # Rotate the image
        if angle90: new_image = new_image.rotate(round(90*angle90))

        return new_image
        
if __name__ == "__main__": SpriteManager()


