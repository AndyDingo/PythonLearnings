import wx
import wx.dataview as dv
import xml.etree.ElementTree as ET
import xml.dom.minidom


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


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(800, 600))

        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.dvlc = dv.DataViewListCtrl(self.panel)
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

        self.vbox.Add(self.button_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.form = None
        self.file_path = None
        self.root = None

        self.Centre()
        self.Show()

    def load_data_to_dvlc(self):
        # Clear existing columns and items
        self.dvlc.ClearColumns()
        self.dvlc.DeleteAllItems()

        # Get the first element and create columns based on its children
        first_element = next(iter(self.root))
        columns = [child.tag for child in first_element]

        for column in columns:
            self.dvlc.AppendTextColumn(column)

        # Add rows to DataViewListCtrl
        for item in self.root:
            values = [child.text if child.text else "" for child in item]
            self.dvlc.AppendItem(values)

        # Create form for adding new items dynamically
        self.create_form(columns)

    def create_form(self, columns):
        if self.form:
            self.vbox.Hide(self.form)
            self.form.Clear(True)

        self.form = wx.BoxSizer(wx.HORIZONTAL)
        self.inputs = {}

        for column in columns:
            self.form.Add(wx.StaticText(self.panel, label=f"{column}:"), 0, wx.ALL, 5)
            input_ctrl = wx.TextCtrl(self.panel)
            self.inputs[column] = input_ctrl
            self.form.Add(input_ctrl, 1, wx.ALL, 5)

        self.add_button = wx.Button(self.panel, label="Add")
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add)
        self.form.Add(self.add_button, 0, wx.ALL, 5)

        self.vbox.Add(self.form, 0, wx.EXPAND | wx.ALL, 5)
        self.panel.Layout()

    def on_add(self, event):
        values = [self.inputs[column].GetValue() for column in self.inputs]
        self.dvlc.AppendItem(values)

        # Add new item to XML tree
        new_item = ET.SubElement(self.root, self.root[0].tag)
        for column, value in zip(self.inputs.keys(), values):
            ET.SubElement(new_item, column).text = value

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
    frame = MyFrame(None, "XML to DataViewListCtrl")
    app.MainLoop()


if __name__ == "__main__":
    main()
