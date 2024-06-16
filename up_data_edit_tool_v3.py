import wx
import wx.dataview as dv
import xml.etree.ElementTree as ET
import xml.dom.minidom
import uuid
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure


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
        super(AddEntryDialog, self).__init__(parent, title="Add Entry", size=(400, 300))

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


class GraphDialog(wx.Dialog):
    def __init__(self, parent, data):
        super(GraphDialog, self).__init__(parent, title="Graph Display", size=(600, 400))

        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # Extract data for graph
        origins = [item['origin'] for item in data]
        unique_origins = list(set(origins))
        origin_counts = [origins.count(origin) for origin in unique_origins]

        # Create a figure and a canvas
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.bar(unique_origins, origin_counts)

        self.canvas = FigureCanvas(self.panel, -1, self.figure)
        self.vbox.Add(self.canvas, 1, wx.EXPAND)

        self.panel.SetSizer(self.vbox)
        self.Layout()


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(800, 600))

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

        self.graph_button = wx.Button(self.panel, label="Show Graph")
        self.graph_button.Bind(wx.EVT_BUTTON, self.on_show_graph)
        self.button_panel.Add(self.graph_button, 0, wx.ALL, 5)

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
        icon = wx.Icon("icon.ico", wx.BITMAP_TYPE_ICO)
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
            values = {child.tag: child.text if child.text else "" for child in entry}
            # Ensure the values list matches
