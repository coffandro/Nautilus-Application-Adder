from gi.repository import Nautilus, GObject, Gtk, GdkPixbuf
from pathlib import Path
from builtins import any as b_any
import os

class NAAWindow(Gtk.Window):
    def __init__(self, File=None, path="/usr/share/application", **kargs):
        super().__init__(**kargs, title="App list adder")

        hb = Gtk.HeaderBar()
        self.set_titlebar(hb)

        hb.set_show_title_buttons(False)

        CancelButton = Gtk.Button.new_with_label("Cancel")
        CancelButton.connect("clicked", self.Close)
        SubmitButton = Gtk.Button.new_with_label("Submit")
        SubmitButton.connect("clicked", self.Submit)

        hb.pack_start(CancelButton)
        hb.pack_end(SubmitButton)

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

        Path = str(File.get_uri())
        Path = Path.split("file://")[1]
        word = os.path.basename(Path)
        Path = os.path.dirname(Path)

        images = []
        for image in os.listdir(Path):
            # check if the image ends with png or jpg or jpeg
            if (
                image.endswith(".png")
                or image.endswith(".jpg")
                or image.endswith(".jpeg")
            ):
                images.append(image)

        if b_any(word in x for x in images):
            Icon = self.CreateIcon(Path + "/" + images[0])
        elif File.get_mime_type() == None:
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

        self.TerminalCheckbox = Gtk.CheckButton.new_with_label("Run with terminal?")

        grid = Gtk.Grid()
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)

        grid.attach(self.IconButton, 0, 0, 1, 4)

        grid.attach(NameLabel, 1, 0, 1, 1)
        grid.attach(self.NameTextbox, 2, 0, 2, 1)

        grid.attach(CmntLabel, 1, 2, 1, 1)
        grid.attach(self.CmntTextbox, 2, 2, 2, 1)

        grid.attach(CMDLabel, 1, 3, 1, 1)
        grid.attach(self.CMDTextbox, 2, 3, 1, 1)
        grid.attach(CMDPicker, 3, 3, 1, 1)

        grid.attach(self.TerminalCheckbox, 2, 4, 2, 1)

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
        f.write(f"Terminal={self.TerminalCheckbox.get_active()}\n")
        f.write(f"Comment={self.CmntTextbox.get_text()}\n")
        f.write(f"Exec={self.CMDTextbox.get_text()}\n")
        f.close()

        self.close()

    def Close(self, _widget):
        self.destroy()
