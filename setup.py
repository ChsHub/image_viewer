from subprocess import Popen

from utility.os_interface import read_file_data, write_file_data, delete_file

app_title = __file__.split("/")[-2]
icon_path = 'icon.ico'

delete_file(app_title+".spec")
# datas=[('artist_path.cfg', '.'),('src/icons/icon.ico', 'src/icons/')]
# "+app_title+".spec
# __main__.py
Popen('pyinstaller "main.py"  --noconfirm --onedir --noconsole --name "' + app_title +
      '" --icon "' + icon_path + '"').communicate()

spec_data = read_file_data(app_title+".spec")
spec_data = spec_data.replace('datas=[',
                              "datas=[('icon.ico', '.')")
write_file_data(".", app_title+".spec", spec_data)

Popen('pyinstaller "'+app_title+'.spec"  --noconfirm').communicate()
delete_file(app_title+".spec")
