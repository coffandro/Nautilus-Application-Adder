from gi.repository import Nautilus, GObject, Gtk, GdkPixbuf
from typing import List
from pathlib import Path
from builtins import any as b_any
import json
import window
import os


class NautilusAddDesktopFile(GObject.Object, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()

        self.MimeTypes = [
            "application/x-msdownload",
            "application/vnd.microsoft.portable-executable",
            "application/x-sh",
            "application/x-shellscript",
            "application/x-executable",
            "text/x-python",
        ]

        with open(os.path.join(os.path.dirname(__file__), "config.json")) as json_file:
            try:
                self.config = json.load(json_file)
            except:
                self.config = {
                    "items": {
                        "_comment": "Items to include in the context menu",
                        "AddToLocal": True,
                        "RemoveFromLocal": True,
                    }
                }

        print("Initialized Nautilus Applications extension")

    def AddLocalApp(
        self,
        menu: Nautilus.MenuItem,
        file: Nautilus.FileInfo,
    ) -> None:
        home = str(Path.home())
        self.Popup(file, f"{home}/.local/share/applications")

    def RemoveLocalApp(
        self,
        menu: Nautilus.MenuItem,
        file: Nautilus.FileInfo,
    ) -> None:
        home = str(Path.home())
        os.remove(self.ApplicationExists(file))

    def Popup(self, file, ExportDir):
        win = window.NAAWindow(file, ExportDir)

        win.present()

    def ApplicationExists(self, file):
        home = str(Path.home())
        status = False

        for i in os.listdir(f"{home}/.local/share/applications"):
            if not os.isdir(f"{home}/.local/share/applications/{i}"):
                f = open(
                    f"{home}/.local/share/applications/{i}", "r"
                )
                if f"# NAA={file.get_location().get_path()}" in f.readline().strip('\n'):
                    status = f"{home}/.local/share/applications/{i}"
    
                f.close()
        return status

    def get_file_items(
        self,
        files: List[Nautilus.FileInfo],
    ) -> List[Nautilus.MenuItem]:
        config_items = self.config["items"]
        active_items = []

        if len(files) != 1:
            return []

        file = files[0]
        if file.get_mime_type() in self.MimeTypes:

            if config_items["AddToLocal"]:
                item = Nautilus.MenuItem(
                    name="SimpleMenuExtension::AddLocalAppEntry",
                    label="Add to apps",
                    tip="This adds the selected app to your users applications list,\n others cannot see it",
                )
                item.connect("activate", self.AddLocalApp, file)
                active_items.append(item)
            if config_items["RemoveFromLocal"]:
                if self.ApplicationExists(file)!=False:
                    item = Nautilus.MenuItem(
                        name="SimpleMenuExtension::AddLocalAppEntry",
                        label="Remove from apps",
                        tip="This removes the selected app from your users applications list,\n others cannot see it",
                    )
                    item.connect("activate", self.RemoveLocalApp, file)
                    active_items.append(item)

            return active_items
