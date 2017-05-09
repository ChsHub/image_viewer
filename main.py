from tkinter import Tk, RIGHT, BOTH, Label, W, TOP, NO, Frame, YES, N, E, S, BOTH
from tkinter.filedialog import askdirectory
from tkinter.font import Font
from tkinter import Button

from PIL import Image, ImageTk
from PIL.Image import BICUBIC
from standard_view.colors import color_button
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
    button_width=90

    def __init__(self):

        self._root = Tk()
        self._root.title("Viewer")
        self._root.attributes("-fullscreen", True)

        # self._root_frame = StandardFrame(self._root, side=RIGHT, fill=BOTH)
        self._root.bind("<Right>", lambda x: self.next_image())
        self._root.bind("<Left>", lambda x: self.prev_image())
        self._root.bind("<Escape>", lambda x: self.quit())

        self.screen_width = self._root.winfo_screenwidth()-self.button_width
        self.screen_height = self._root.winfo_screenheight()

        helv36 = Font(family='Helvetica', size=36)
        col = Frame(self._root, padx=0, pady=0, height=self.screen_height, width= 10, bg="#000000")
        col.pack(side=RIGHT, fill=BOTH)

        Button(text="✕", master=col, command=self.quit, font=helv36, bg=color_button).grid(column=1, sticky=W+E+N+S)
        Button(text="⟲", master=col, command=self.flip, font=helv36, bg=color_button).grid(column=1, sticky=W+E+N+S)
        Button(text="⧐", master=col, command=self.next_image, font=helv36, bg=color_button).grid(column=1, sticky=W+E+N+S)
        Button(text="⧏", master=col, command=self.prev_image, font=helv36, bg=color_button).grid(column=1, sticky=W+E+N+S)
        Button(text="...", master=col, command=self.open, font=helv36, bg=color_button).grid(column=1, sticky=W+E+N+S)


        self.col = col
        # build gui
        self._root.mainloop()

    def init_picture(self, path):

        if not path:
            return

        self.path = path
        self.pictures = get_dir_list(path)
        self.pictures = list(filter(lambda x: x[-3:] in "jpgjpegpnggif", self.pictures))
        self.index = 0
        if self.pictures:
            self.update_image()

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
            img = img.rotate(self._angle, expand=True, resample=Image.LANCZOS)

            x, y = img.size
            size = (int(self.screen_height * x / y), self.screen_height)
            img = img.resize(size, Image.LANCZOS)
            x, y = img.size
            if x > self.screen_width:
                img = img.resize((self.screen_width, int(self.screen_width * y / x)), Image.LANCZOS)

            img = ImageTk.PhotoImage(img)
            label = Label(image=img, master=self.col, padx=0, pady=0, anchor=W, border=0)
            label.image = img  # keep a reference!
            label.grid(column=0, row=0, rowspan=5)
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
        if self.image_label:
            self.image_label.destroy()
        self.image_label = self.display_image()


if __name__ == "__main__":
    Window()
