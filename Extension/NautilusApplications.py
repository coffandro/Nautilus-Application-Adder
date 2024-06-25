from gi.repository import Nautilus, GObject, Gtk, GdkPixbuf
from typing import List
from pathlib import Path
import os


class NautilusAddDesktopFile(GObject.Object, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()

        self.MimeTypes = [
            "application/x-ms-dos-executable",
            "application/x-ms-installer",
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

    def Popup(self, file, ExportDir):
        win = MyWindow(file, ExportDir)

        win.present()

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

            return active_items


class MyWindow(Gtk.Window):
    def __init__(self, File=None, path="/usr/share/application", **kargs):
        super().__init__(**kargs, title="App list adder")

        self.path = path
        self.file = File
        self.IconPath = ""

        NameLabel = Gtk.Label.new("Name: ")
        self.NameTextbox = Gtk.Entry.new()
        if File != None:
            self.NameTextbox.set_text(File.get_name())

        CmntLabel = Gtk.Label.new("Comment: ")
        self.CmntTextbox = Gtk.Entry.new()
        if File.get_mime_type() == "application/x-executable":
            self.CmntTextbox.set_text(f"{File.get_name()} Executable")
        elif File.get_mime_type() == "application/x-sh":
            self.CmntTextbox.set_text(f"{File.get_name()} Script")
        elif File.get_mime_type() == "application/x-shellscript":
            self.CmntTextbox.set_text(f"{File.get_name()} Script")

        CMDLabel = Gtk.Label.new("Command: ")
        self.CMDTextbox = Gtk.Entry.new()
        self.CMDTextbox.set_text(File.get_location().get_path())

        CMDPicker = Gtk.Button(label="🖿")
        CMDPicker.connect("clicked", self.SelectCMD)

        self.IconButton = Gtk.Button()
        if File.get_mime_type() == None:
            Icon = self.CreateIcon(
                "/usr/share/icons/Adwaita/symbolic/actions/action-unavailable-symbolic.svg"
            )
        elif File.get_mime_type() == "application/x-executable":
            Icon = self.CreateIcon(
                "/usr/share/icons/Adwaita/symbolic/mimetypes/application-x-executable-symbolic.svg"
            )
        elif File.get_mime_type() == "application/x-sh":
            Icon = self.CreateIcon(
                "/usr/share/icons/Adwaita/symbolic/mimetypes/text-x-generic-symbolic.svg"
            )
        elif File.get_mime_type() == "application/x-shellscript":
            Icon = self.CreateIcon(
                "/usr/share/icons/Adwaita/symbolic/mimetypes/text-x-generic-symbolic.svg"
            )
        else:
            Icon = self.CreateIcon(
                "/usr/share/icons/Adwaita/symbolic/mimetypes/application-x-executable-symbolic.svg"
            )

        self.IconButton.set_child(Icon)
        self.IconButton.connect("clicked", self.SelectImage)

        CancelButton = Gtk.Button.new_with_label("Cancel")
        CancelButton.connect("clicked", self.Close)
        SubmitButton = Gtk.Button.new_with_label("Submit")
        SubmitButton.connect("clicked", self.Submit)

        self.TerminalCheckbox = Gtk.CheckButton.new_with_label("Run with terminal?")

        grid = Gtk.Grid()
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)

        grid.attach(self.IconButton, 0, 0, 1, 4)

        grid.attach(NameLabel, 1, 0, 1, 1)
        grid.attach(self.NameTextbox, 2, 0, 2, 1)

        grid.attach(CmntLabel, 1, 2, 1, 1)
        grid.attach(self.CmntTextbox, 2, 2, 2, 1)

        grid.attach(CMDLabel, 1, 3, 1, 1)
        grid.attach(self.CMDTextbox, 2, 3, 1, 1)
        grid.attach(CMDPicker, 3, 3, 1, 1)

        grid.attach(self.TerminalCheckbox, 2, 4, 2, 1)

        grid.attach(CancelButton, 0, 5, 2, 1)
        grid.attach(SubmitButton, 2, 5, 2, 1)

        self.set_child(grid)

    def CreateIcon(self, path):
        Icon = Gtk.Image()

        width = -1
        height = 128
        preserve_aspect_ratio = True

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            path, width, height, preserve_aspect_ratio
        )

        Icon.set_from_pixbuf(pixbuf)
        Icon.set_pixel_size(96)

        self.IconPath = path
        return Icon

    def SelectImage(self, _widget):
        dialog = Gtk.FileDialog()

        dialog.open(self, None, self.on_Icon_select)

    def SelectCMD(self, _widget):
        dialog = Gtk.FileDialog()

        dialog.open(self, None, self.on_CMD_select)

    def on_Icon_select(self, dialog, result):
        try:
            File = dialog.open_finish(result)
            self.IconButton.set_child(self.CreateIcon(File.get_path()))
        except Gtk.DialogError:
            # user cancelled or backend error
            pass

    def on_CMD_select(self, dialog, result):
        try:
            File = dialog.open_finish(result)
            self.CMDTextbox.set_text(File.get_path())
        except Gtk.DialogError:
            # user cancelled or backend error
            pass

    def Submit(self, _widget):
        if not os.path.isdir(self.path):
            os.mkdir(self.path)

        f = open(
            f"{self.path}/{self.NameTextbox.get_text().split('.')[0]}.desktop", "w"
        )
        f.write("[Desktop Entry]\n")
        f.write(f"Name={self.NameTextbox.get_text()}\n")
        f.write(f"Icon={self.IconPath}\n")
        f.write("Type=Application\n")
        f.write("Version=1.0\n")
        f.write(f"Terminal={self.TerminalCheckbox.get_active()}\n")
        f.write(f"Comment={self.CmntTextbox.get_text()}\n")
        f.write(f"Exec={self.CMDTextbox.get_text()}\n")
        f.close()

    def Close(self, _widget):
        self.destroy()
