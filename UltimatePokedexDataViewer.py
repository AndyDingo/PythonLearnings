import wx
import wx.grid
import xml.etree.ElementTree as ET
import wx.dataview as dv
import uuid
import xml.dom.minidom
import os


def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root


# Try to pretty up the XML file, also set the right text encoding
def prettify_xml(element):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)

    prettyxml = reparsed.toprettyxml()

    prettyxml = os.linesep.join([s for s in prettyxml.splitlines()
                                 if s.strip()])
    return prettyxml


# Write XML to a file
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

        # Add columns to DataViewListCtrl
        # self.dvlc.AppendTextColumn("ID")
        # self.dvlc.AppendTextColumn("Num")
        # self.dvlc.AppendTextColumn("Name")
        # self.dvlc.AppendTextColumn("Effect")
        # self.dvlc.AppendTextColumn("Game Text")
        # self.dvlc.AppendTextColumn("Pkmn (Can Have)")
        # self.dvlc.AppendTextColumn("Pkmn (Hidden)")
        # self.dvlc.AppendTextColumn("Field Effect")
        # self.dvlc.AppendTextColumn("Notes")
        # self.dvlc.AppendTextColumn("Origin")

        self.panel.SetSizer(self.vbox)

        # first_column = self.dvlc.Columns[1]  # get the second column
        # first_column.SetSortable(sortable=True)  # make second column sortable

        # Load XML data
        # self.file_path = "data.xml"
        # self.root = parse_xml(self.file_path)
        self.load_data_to_dvlc()

        # Add form for new entry
        # self.create_form()

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

        # self.form = wx.BoxSizer(wx.HORIZONTAL)

        # self.num_input = wx.TextCtrl(self.panel)
        # self.name_input = wx.TextCtrl(self.panel)
        # self.effect_input = wx.TextCtrl(self.panel)
        # self.gametext_input = wx.TextCtrl(self.panel)
        # self.pkmn_canhave_input = wx.TextCtrl(self.panel)

        # self.form.Add(wx.StaticText(self.panel, label="Num:"), 0, wx.ALL, 5)
        # self.form.Add(self.num_input, 1, wx.ALL, 5)
        # self.form.Add(wx.StaticText(self.panel, label="Name:"), 0, wx.ALL, 5)
        # self.form.Add(self.name_input, 1, wx.ALL, 5)
        # self.form.Add(wx.StaticText(self.panel, label="Effect:"), 0, wx.ALL, 5)
        # self.form.Add(self.effect_input, 1, wx.ALL, 5)
        # self.form.Add(wx.StaticText(self.panel, label="Game Text:"), 0, wx.ALL, 5)
        # self.form.Add(self.gametext_input, 1, wx.ALL, 5)
        # self.form.Add(wx.StaticText(self.panel, label="Pokemon Can Have:"), 0, wx.ALL, 5)
        # self.form.Add(self.pkmn_canhave_input, 1, wx.ALL, 5)

        # self.add_button = wx.Button(self.panel, label="Add")
        # self.add_button.Bind(wx.EVT_BUTTON, self.on_add)
        # self.form.Add(self.add_button, 0, wx.ALL, 5)

        # self.vbox.Add(self.form, 0, wx.EXPAND | wx.ALL, 5)

    def on_add(self, event):
        values = [self.inputs[column].GetValue() for column in self.inputs]
        self.dvlc.AppendItem(values)

        # Add new item to XML tree
        new_item = ET.SubElement(self.root, self.root[0].tag)
        for column, value in zip(self.inputs.keys(), values):
            ET.SubElement(new_item, column).text = value

        # id_ = str(uuid.uuid4())  # Generate our GUID
        # num = self.num_input.GetValue()
        # name = self.name_input.GetValue()
        # effect = self.effect_input.GetValue()
        # gametext = self.gametext_input.GetValue()
        # pkmn_canhave = self.pkmn_canhave_input.GetValue()
        # pkmn_hidden = ""
        # fieldeffect = ""
        # notes = "-"
        # origin = ""

        # self.dvlc.AppendItem([id_, num, name, effect, gametext, pkmn_canhave, pkmn_hidden, fieldeffect, notes, origin])

        # Add new ability to XML tree
        # abilities = self.root.find('abilities')
        # new_ability = ET.SubElement(abilities, 'ability')
        # ET.SubElement(new_ability, 'id').text = id_
        # ET.SubElement(new_ability, 'num').text = num
        # ET.SubElement(new_ability, 'name').text = name
        # ET.SubElement(new_ability, 'effect').text = effect
        # ET.SubElement(new_ability, 'gametext').text = gametext
        # ET.SubElement(new_ability, 'pkmn_canhave').text = pkmn_canhave
        # ET.SubElement(new_ability, 'pkmn_hidden').text = "False"
        # ET.SubElement(new_ability, 'fieldeffect').text = "N/A"
        # ET.SubElement(new_ability, 'notes').text = "-"
        # ET.SubElement(new_ability, 'origin').text = ""

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
    frame = MyFrame(None, "Ultimate Pokedex Data Editing Tool")
    app.MainLoop()


if __name__ == "__main__":
    main()
