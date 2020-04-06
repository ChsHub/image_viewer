from os.path import split

from utility.setup_lib import setup_exe

app_title, _ = split(__file__)
_, app_title = split(app_title)
pyinstaller = 'C:\Python\Python38-32\Scripts\pyinstaller.exe'

setup_exe(main_path="__main__.py", app_name=app_title, pyinstaller_path=pyinstaller)
