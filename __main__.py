__version__ = '1.0.0'
from logger_default import Logger

log = Logger(debug=True)
try:
    from logging import info, exception, error
    from sys import argv, executable
    from concurrent.futures import ThreadPoolExecutor
    from multiprocessing import BoundedSemaphore
    from os import listdir
    from os.path import join, exists, isdir, split
    from tkinter import Button, Tk, RIGHT, Label, W, Frame, N, E, S
    from tkinter.filedialog import askdirectory
    from tkinter.font import Font

    from PIL import Image, ImageTk
    from PIL.Image import BILINEAR, HAMMING, BICUBIC, LANCZOS
    from send2trash import send2trash
    from standard_view.colors import color_button
    from timerpy import Timer
    from utility.os_interface import natural_sorted
    from utility.utilities import is_file_type
except Exception as e:
    exception(e)


class Window:
    def __init__(self, input_path=""):
        self.image_label = None
        self._root = None
        self._angle = 0
        self.path = None
        self.pictures = None
        self._index = 0
        self._zoom = 100
        button_width = 90

        self._root = Tk()
        self._root.title("Viewer")
        self._root.attributes("-fullscreen", True)

        self._root.bind("<Right>", lambda x: self.update_image(1))
        self._root.bind("<Left>", lambda x: self.update_image(-1))
        self._root.bind("<Escape>", lambda x: self._root.quit())
        self._root.bind_all("<MouseWheel>", lambda x: self._on_mousewheel(x))

        self.screen_width = self._root.winfo_screenwidth() - button_width
        self.screen_height = self._root.winfo_screenheight()

        helv36 = Font(family='Helvetica', size=36)
        col = Frame(self._root, padx=0, pady=0, height=self.screen_height, width=self._root.winfo_screenwidth(),
                    bg="#000000")
        col.pack(side=RIGHT)

        Button(text="✕", master=col, command=self._root.quit,
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)
        Button(text="⟲", master=col, command=self.flip,
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)
        Button(text="⧐", master=col, command=lambda: self.update_image(1),
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)
        Button(text="⧏", master=col, command=lambda: self.update_image(-1),
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)
        Button(text="...", master=col, command=self.open,
               font=helv36, bg=color_button).grid(column=1, sticky=W + E + N + S)

        self.col = col
        # Multithreading
        self._executor = ThreadPoolExecutor()
        self._update_sem = BoundedSemaphore(value=1)

        # build gui
        self.init_path(input_path)
        self._root.mainloop()

    def _get_pictures(self, dir_path):
        return list(filter(lambda x: is_file_type(x, ["jpg", "jpeg", "png", "gif", 'webp', 'tiff', 'bmp']),
                           natural_sorted(listdir(dir_path))))

    def init_path(self, path: str):
        if not exists(path):
            error('Invalid input')
            return

        if isdir(path):
            self.path = path
            self.pictures = self._get_pictures(self.path)
        else:
            self.path, file = split(path)
            self.pictures = self._get_pictures(self.path)
            if file in self.pictures:
                self._index = self.pictures.index(file)

        self.update_image()

    def flip(self):
        self._angle += 1
        self._angle %= 4
        self.update_image()

    def open(self):
        self.init_path(path=askdirectory())

    def _fit_screen(self, img, angle):

        img = img.rotate(angle, expand=True)
        # Resize
        x, y = img.size
        pixels = x * y
        info('IMG SIZE: ' + str(pixels))
        sample = [LANCZOS, BICUBIC, HAMMING, BILINEAR][pixels // 1000000 % 4]
        info('SAMPLE: ' + str(sample))

        if y * self.screen_width <= self.screen_height * x:
            img = img.resize((int(self.screen_width), int(y * self.screen_width / x)), resample=sample)
        else:  # if int(x * self.screen_height / y) <= self.screen_width:
            img = img.resize((int(x * self.screen_height / y), int(self.screen_height)), resample=sample)

        img.non = True

        return img

    def _process_image(self, index):
        info('PROCESS ' + str(index))

        if type(self.pictures[index]) == str:
            path_file = join(self.path, self.pictures[index])
            if not exists(path_file):
                return None

            img = Image.open(path_file)
            with Timer('CONVERT'):
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img = img.convert('RGBA')  # keeping PNG palette will introduce aliasing
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

            img.non = False
            self.pictures[index] = [img, img]
        # no else

        with Timer('FIT SCREEN'):
            angle = self._angle % 2
            if not self.pictures[index][angle].non:
                self.pictures[index][angle] = self._fit_screen(self.pictures[index][angle], 90 * angle)
            # no else

        if self._angle < 2:
            return self.pictures[index][angle]
        else:
            return self.pictures[index][angle].rotate(180, expand=True)

    def _display_image(self):

        try:
            img = self._process_image(self._index)
            img = ImageTk.PhotoImage(img)
            label = Label(image=img, master=self.col, padx=0, pady=0, anchor=W, border=0)
            label.image = img  # keep a reference!
            label.grid(column=0, row=0, rowspan=5)
            label.index = self._index  # save image index for threading
            label.angle = self._angle  # save image index for threading
        except OSError as e:
            info('Delete invalid file')
            send2trash(join(self.path, self.pictures[self._index]))
            label = self.image_label
        return label

    def update_image(self, offset=0):
        self._index += offset
        if self.pictures:
            with self._update_sem:
                self._index %= len(self.pictures)
                if self.image_label:
                    if self._index == self.image_label.index and self._angle == self.image_label.angle:
                        return

                if self.image_label:
                    self.image_label.destroy()
                self.image_label = self._display_image()

                # self._executor.submit(self._process_image, (self._index + 1) % len(self.pictures))
                # self._executor.submit(self._process_image, (self._index - 1) % len(self.pictures))

    def _on_mousewheel(self, wheel_event):
        self._zoom += int(wheel_event.delta / 12)
        print(self._zoom)
    # TODO zoom
    #   size = (int(size[0] * self._zoom / 100), int(size[1] * self._zoom / 100))  # apply zoom
    #  img = self.image_label.img.resize(size, self.sample)


if __name__ == "__main__":

    path = argv[-1]
    info(path)
    info(executable)

    try:
        Window(path)
    except Exception as e:
        exception(e)
