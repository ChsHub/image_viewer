from tkinter import Tk, RIGHT, BOTH, Label, W, TOP, NO
from tkinter.filedialog import askdirectory
from tkinter.font import Font

from PIL import Image, ImageTk
from PIL.Image import BICUBIC
from standard_view.standard_button import StandardButton
from standard_view.standard_frame import StandardFrame
from utility.os_interface import get_dir_list, exists
from utility.path_str import get_full_path


class Window:
    image_label = None
    _root = None
    _root_frame = None
    _angle = 90
    path = None
    pictures = None
    index = None

    def __init__(self):

        self._root = Tk()
        self._root.title("Viewer")
        self._root.attributes("-fullscreen", True)

        # self._root_frame = StandardFrame(self._root, side=RIGHT, fill=BOTH)
        self._root.bind("<Right>", lambda x: self.next_image())
        self._root.bind("<Left>", lambda x: self.prev_image())
        self._root.bind("<Escape>", lambda x: self.quit())

        screen_width = self._root.winfo_screenwidth()
        self.screen_height = self._root.winfo_screenheight()

        helv36 = Font(family='Helvetica', size=36)
        button_height = int(self.screen_height / 5 / 72)
        button_width = int(screen_width / 10 / 36)
        col = StandardFrame(self._root, RIGHT, expand=NO, padx=0, pady=0)
        StandardButton("✕", col, self.quit, side=TOP, height=button_height, font=helv36, width=button_width)
        StandardButton("⟲", col, self.flip, side=TOP, height=button_height, font=helv36, width=button_width)
        StandardButton("⧐", col, self.next_image, side=TOP, height=button_height, font=helv36, width=button_width)
        StandardButton("⧏", col, self.prev_image, side=TOP, height=button_height, font=helv36, width=button_width)
        StandardButton("Open", col, self.open, side=TOP, height=button_height, font=helv36, width=button_width)

        # build gui
        self._root.mainloop()

    def init_picture(self, path):

        if not path:
            return

        self.path = path
        self.pictures = get_dir_list(path)
        self.pictures = list(filter(lambda x: x[-3:] in "jpgjpegpnggif", self.pictures))
        self.index = 0
        if len(self.pictures) > 0:
            self.image_label = self.display_image()

    def quit(self):
        self._root.quit()

    def flip(self):
        self._angle += 90
        self._angle %= 360
        self.update_image()

    def open(self):
        self.init_picture(path=askdirectory())

    def display_image(self):
        path_file = get_full_path(self.path, self.pictures[self.index])

        if exists(path_file):

            img = Image.open(path_file)
            x, y = img.size
            if x < y:
                size = (self.screen_height, int(self.screen_height / x * y))
                img = img.resize(size, BICUBIC)
                img = img.rotate(self._angle, expand=True, resample=Image.LANCZOS)
            else:
                size = (int(self.screen_height / y * x), self.screen_height)
                img = img.resize(size, Image.LANCZOS)


            img = ImageTk.PhotoImage(img)
            label = Label(image=img, master=self._root_frame, padx=10, pady=10, anchor=W)
            label.image = img  # keep a reference!
            label.pack(side=RIGHT)
            return label

        return None

    def next_image(self):
        self.index += 1
        self.index %= len(self.pictures)
        self.update_image()

    def prev_image(self):
        self.index -= 1
        self.index %= len(self.pictures)
        self.update_image()

    def update_image(self):
        self.image_label.destroy()
        self.image_label = self.display_image()


if __name__ == "__main__":
    Window()
