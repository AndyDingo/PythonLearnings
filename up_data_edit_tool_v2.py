import wx
import wx.dataview as dv
import xml.etree.ElementTree as ET
import xml.dom.minidom
import uuid


def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root


def prettify_xml(element):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def write_xml(root, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(prettify_xml(root))


class AddEntryDialog(wx.Dialog):
    def __init__(self, parent, columns):
        super(AddEntryDialog, self).__init__(parent, title="Add Entry", size=(300, 400))

        self.columns = columns
        self.values = {}

        self.panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.panel.SetScrollRate(20, 20)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.form = wx.BoxSizer(wx.VERTICAL)

        for column in columns:
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(wx.StaticText(self.panel, label=f"{column}:"), 0, wx.ALL, 5)
            input_ctrl = wx.TextCtrl(self.panel)
            if column == "id":
                input_ctrl.SetValue(str(uuid.uuid4()))
                input_ctrl.Enable(False)  # Make the id field read-only
            self.values[column] = input_ctrl
            hbox.Add(input_ctrl, 1, wx.ALL, 5)
            self.form.Add(hbox, 0, wx.EXPAND | wx.ALL, 5)

        self.vbox.Add(self.form, 1, wx.EXPAND | wx.ALL, 5)

        self.button_panel = wx.BoxSizer(wx.HORIZONTAL)

        self.ok_button = wx.Button(self.panel, label="OK")
        self.ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
        self.button_panel.Add(self.ok_button, 0, wx.ALL, 5)

        self.cancel_button = wx.Button(self.panel, label="Cancel")
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.button_panel.Add(self.cancel_button, 0, wx.ALL, 5)

        self.vbox.Add(self.button_panel, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.panel.SetSizer(self.vbox)

    def on_ok(self, event):
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def get_values(self):
        return {column: ctrl.GetValue() for column, ctrl in self.values.items()}


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(1024, 768))

        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.dvlc = dv.DataViewListCtrl(self.panel, style=dv.DV_ROW_LINES)
        self.vbox.Add(self.dvlc, 1, wx.EXPAND)

        self.panel.SetSizer(self.vbox)

        # Add buttons for opening and saving files
        self.button_panel = wx.BoxSizer(wx.HORIZONTAL)

        self.open_button = wx.Button(self.panel, label="Open")
        self.open_button.Bind(wx.EVT_BUTTON, self.on_open)
        self.button_panel.Add(self.open_button, 0, wx.ALL, 5)

        self.save_button = wx.Button(self.panel, label="Save")
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)
        self.button_panel.Add(self.save_button, 0, wx.ALL, 5)

        self.add_button = wx.Button(self.panel, label="Add Entry")
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add)
        self.button_panel.Add(self.add_button, 0, wx.ALL, 5)

        self.vbox.Add(self.button_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.form = None
        self.file_path = None
        self.root = None
        self.data_container = None

        # Set the frame icon
        self.set_icon()

        self.Centre()
        self.Show()

    def set_icon(self):
        icon = wx.Icon("pokemon_7025.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    def load_data_to_dvlc(self):
        # Clear existing columns and items
        self.dvlc.ClearColumns()
        self.dvlc.DeleteAllItems()

        # Get the data container (second element) and the first data entry (third level element)
        self.data_container = self.root[0]

        if len(self.data_container) == 0:
            wx.MessageBox("No data entries found in the XML file.", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        first_entry = self.data_container[0]
        columns = [child.tag for child in first_entry]

        for column in columns:
            if column == "id":
                self.dvlc.AppendTextColumn(column, mode=dv.DATAVIEW_CELL_INERT)
            else:
                self.dvlc.AppendTextColumn(column, mode=dv.DATAVIEW_CELL_EDITABLE)

        # Add rows to DataViewListCtrl
        for entry in self.data_container:
            values = [child.text if child.text else "" for child in entry]
            # Ensure the values list matches the number of columns
            while len(values) < len(columns):
                values.append("")
            self.dvlc.AppendItem(values)

        # Auto size columns to fit content
        for i in range(self.dvlc.GetColumnCount()):
            self.dvlc.Columns[i].SetSortable(i != 0)
            self.dvlc.Columns[i].Width = wx.LIST_AUTOSIZE_USEHEADER

    def on_add(self, event):
        if self.data_container is None:
            wx.MessageBox("Please open an XML file first.", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        first_entry = self.data_container[0]
        columns = [child.tag for child in first_entry]

        dlg = AddEntryDialog(self, columns)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.get_values()
            row_values = [values[column] for column in columns]
            self.dvlc.AppendItem(row_values)

            # Add new item to XML tree
            new_entry = ET.SubElement(self.data_container, self.data_container[0].tag)
            for column, value in values.items():
                ET.SubElement(new_entry, column).text = value

        dlg.Destroy()

    def on_open(self, event):
        with wx.FileDialog(self, "Open XML file", wildcard="XML files (*.xml)|*.xml",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            self.file_path = fileDialog.GetPath()
            try:
                self.root = parse_xml(self.file_path)
                self.load_data_to_dvlc()
            except IOError:
                wx.LogError("Cannot open file '%s'." % self.file_path)

    def on_save(self, event):
        if not self.file_path or not self.root:
            wx.LogError("No file is currently open.")
            return

        with wx.FileDialog(self, "Save XML file", wildcard="XML files (*.xml)|*.xml",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Save the current contents in the file
            self.file_path = fileDialog.GetPath()
            try:
                write_xml(self.root, self.file_path)
                wx.MessageBox("Data saved to file!", "Info", wx.OK | wx.ICON_INFORMATION)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % self.file_path)


def main():
    app = wx.App(False)
    frame = MyFrame(None, "Ultimate Pokedex Data Editing Tool (Python ver.)")
    app.MainLoop()


if __name__ == "__main__":
    main()
