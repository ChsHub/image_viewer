from concurrent.futures import ThreadPoolExecutor
from tkinter import Button
from tkinter import Tk, RIGHT, Label, W, Frame, N, E, S
from tkinter.filedialog import askdirectory
from tkinter.font import Font

from PIL import Image, ImageTk
from standard_view.colors import color_button
from utility.os_interface import get_dir_list, exists, is_dir, natural_sorted
from utility.path_str import get_full_path, get_clean_path, get_file_name
from utility.utilities import is_file_type


class Window:
    image_label = None
    _root = None
    _root_frame = None
    _angle = 0
    path = None
    pictures = None
    index = None
    button_width = 90
    sample = Image.BICUBIC
    _zoom = 100

    def __init__(self, input_path=""):

        self._root = Tk()
        self._root.title("Viewer")
        self._root.attributes("-fullscreen", True)

        # self._root_frame = StandardFrame(self._root, side=RIGHT, fill=BOTH)
        self._root.bind("<Right>", lambda x: self.next_image())
        self._root.bind("<Left>", lambda x: self.prev_image())
        self._root.bind("<Escape>", lambda x: self.quit())
        self._root.bind_all("<MouseWheel>", lambda x: self._on_mousewheel(x))

        self.screen_width = self._root.winfo_screenwidth() - self.button_width
        self.screen_height = self._root.winfo_screenheight()

        helv36 = Font(family='Helvetica', size=36)
        col = Frame(self._root, padx=0, pady=0, height=self.screen_height, width=self._root.winfo_screenwidth(),
                    bg="#000000")
        col.pack(side=RIGHT)

        Button(text="✕", master=col, command=self.quit,
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)
        Button(text="⟲", master=col, command=self.flip,
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)
        Button(text="⧐", master=col, command=self.next_image,
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)
        Button(text="⧏", master=col, command=self.prev_image,
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)
        Button(text="...", master=col, command=self.open,
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)

        self.col = col
        self.executor = ThreadPoolExecutor()
        self.init_path(input_path)

        # build gui
        self._root.mainloop()

    def _get_pictures(self, dir_path):

        return list(filter(lambda x: is_file_type(x, ["jpg", "jpeg", "png", "gif"]),
                           natural_sorted(get_dir_list(dir_path))))

    def init_path(self, path):

        if not path:
            return

        path = get_clean_path(path)

        if is_dir(path):
            self.path = path
            self.pictures = self._get_pictures(self.path)
            self.index = 0
        elif exists(path):
            image = get_file_name(path)
            self.path = '/'.join(path.split('/')[:-1])

            self.pictures = self._get_pictures(self.path)
            if image in self.pictures:
                self.index = self.pictures.index(image)
            else:
                self.index = 0
        else:
            return

        if self.pictures:
            self.update_image()
            self.executor.submit(self._process_image, (self.index + 1) % len(self.pictures))
            self.executor.submit(self._process_image, (self.index - 1) % len(self.pictures))

    def quit(self):
        self._root.quit()

    def flip(self):
        self._angle += 1
        self._angle %= 4
        self.update_image()

    def open(self):
        self.init_path(path=askdirectory())

    def _fit_screen(self, img, angle):
        img = img.rotate(angle, expand=True)  # , resample=self.sample)
        # Resize
        x, y = img.size
        if y * self.screen_width <= self.screen_height * x:
            img = img.resize((int(self.screen_width), int(y * self.screen_width / x)), resample=self.sample)
        else:  # if int(x * self.screen_height / y) <= self.screen_width:
            img = img.resize((int(x * self.screen_height / y), int(self.screen_height)), resample=self.sample)

        img.non = True

        return img

    def _process_image(self, index):
        info('PROCESS ' + str(index))
        if type(self.pictures[index]) == str:
            path_file = get_full_path(self.path, self.pictures[index])
            if not exists(path_file):
                return None

            img = Image.open(path_file)
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGBA')  # keeping PNG palette will introduce aliasing
            else:
                img = img.convert('RGB')

            img.non = False
            self.pictures[index] = [img, img]
        # no else

        angle = self._angle % 2
        if not self.pictures[index][angle].non:
            self.pictures[index][angle] = self._fit_screen(self.pictures[index][angle], 90 * angle)
        # no else

        if self._angle < 2:
            return self.pictures[index][angle]
        else:
            return self.pictures[index][angle].rotate(180, expand=True)

    def display_image(self):

        img = self._process_image(self.index)
        img = ImageTk.PhotoImage(img)
        label = Label(image=img, master=self.col, padx=0, pady=0, anchor=W, border=0)
        label.image = img  # keep a reference!
        label.grid(column=0, row=0, rowspan=5)
        return label

    def next_image(self):
        self.index += 1
        self.update_image()
        self.executor.submit(self._process_image, (self.index + 1) % len(self.pictures))
        self.executor.submit(self._process_image, (self.index + 2) % len(self.pictures))

    def prev_image(self):
        self.index -= 1
        self.update_image()

        self.executor.submit(self._process_image, (self.index - 1) % len(self.pictures))
        self.executor.submit(self._process_image, (self.index - 2) % len(self.pictures))

    def update_image(self):
        self.index %= len(self.pictures)

        if self.image_label:
            self.image_label.destroy()
        self.image_label = self.display_image()

    def _on_mousewheel(self, wheel_event):
        self._zoom += int(wheel_event.delta / 12)
        print(self._zoom)
    # TODO zoom
    #   size = (int(size[0] * self._zoom / 100), int(size[1] * self._zoom / 100))  # apply zoom
    #  img = self.image_label.img.resize(size, self.sample)


if __name__ == "__main__":
    from utility.logger import Logger

    # with Logger(2) as log:
    from sys import argv
    from logging import info

    path = argv
    with Logger():
        Window(path[-1])
