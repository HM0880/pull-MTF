import wx
import process_THF_file  # the custom module for this project

mytitle = 'Plot MTF'
version_number = '2.0'
date_updated = 'September 02, 2015'


class MyFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self, None,
            pos=wx.DefaultPosition, size=wx.Size(800, 550),
            style=wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU |
            wx.CAPTION | wx.CLIP_CHILDREN,
            title=mytitle + ' v' + version_number)

        favicon = wx.Icon('./icon_for_plot_MTF.ico', wx.BITMAP_TYPE_ICO)
        wx.Frame.SetIcon(self, favicon)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        box_width = 400

        # Create some sizers
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        grid = wx.GridBagSizer(hgap=10, vgap=10)

        # ~~~~~~~~~~

        # Version number and other info
        row_count = 0
        self.info = wx.StaticText(
            self, label=mytitle + ' v' + version_number + '\n' +
            date_updated + ' by HM')
        self.info.SetFont(wx.Font(14, wx.ROMAN, wx.NORMAL, wx.BOLD))
        grid.Add(self.info, pos=(row_count, 0))

        # Description
        self.description = wx.StaticText(
            self, label='\nPlots all through-focus MTF files (ending in ' +
            '\'.thf\' or \'.THF\') in a directory \nas a function ' +
            'of defocus position.  Can process up to six spatial frequencies.')
        self.description.SetFont(wx.Font(10, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        grid.Add(self.description, pos=(0, 1))

        # ~~~~~~~~~~

        # Mandatory
        row_count += 2
        self.optional_text = wx.StaticText(self, label='Mandatory fields')
        self.optional_text.SetFont(wx.Font(11, wx.ROMAN, wx.NORMAL, wx.BOLD))
        grid.Add(self.optional_text, pos=(row_count, 0))

        # "Select directory" button
        row_count += 1
        self.select_dir_text = wx.StaticText(
            self, label='Select the directory where the data is located')
        grid.Add(self.select_dir_text, pos=(row_count, 0))
        self.select_dir = wx.DirPickerCtrl(self, size=(box_width, -1))
        grid.Add(self.select_dir, pos=(row_count, 1))

        # The frequencies
        row_count += 1
        self.freqs_text = wx.StaticText(
            self, label='Frequencies, separated by commas (i.e. 5, 10, 15)')
        grid.Add(self.freqs_text, pos=(row_count, 0))
        self.freqs = wx.TextCtrl(self, value='', size=(box_width, -1))
        grid.Add(self.freqs, pos=(row_count, 1))

        # ~~~~~~~~~~

        # Optional
        row_count += 2
        self.optional_text = wx.StaticText(
            self, label='Optional fields (all independent of each other)')
        self.optional_text.SetFont(wx.Font(11, wx.ROMAN, wx.NORMAL, wx.BOLD))
        grid.Add(self.optional_text, pos=(row_count, 0))

        # The plot title
        row_count += 1
        self.plot_title_text = wx.StaticText(self, label='Title of the plot')
        grid.Add(self.plot_title_text, pos=(row_count, 0))
        self.plot_title = wx.TextCtrl(self, value='', size=(box_width, -1))
        grid.Add(self.plot_title, pos=(row_count, 1))

        # The horizontal spec lines
        row_count += 1
        self.spec_lines_text = wx.StaticText(
            self, label='Spec lines, separated by commas (i.e. 25, 50, 75)')
        grid.Add(self.spec_lines_text, pos=(row_count, 0))
        self.spec_lines = wx.TextCtrl(self, value='', size=(box_width, -1))
        grid.Add(self.spec_lines, pos=(row_count, 1))

        # Number of plot rows
        row_count += 1
        self.plots_down_text = wx.StaticText(
            self, label='Number of rows on the plot; default is two rows')
        grid.Add(self.plots_down_text, pos=(row_count, 0))
        self.plots_down = wx.TextCtrl(self, value='', size=(box_width, -1))
        grid.Add(self.plots_down, pos=(row_count, 1))

#        # Option for saving the data to an external file
#        row_count += 1
#        self.select_data_save_text = wx.StaticText(
#            self, label='Select the directory to save the data ++update++')
#        grid.Add(self.select_data_save_text, pos=(row_count, 0))
#        self.select_data_save = wx.DirPickerCtrl(self, size=(box_width, -1))
#        grid.Add(self.select_data_save, pos=(row_count, 1))

        # Checkbox option for plotting all the plots on the same figure
        row_count += 1
        self.same_plot_text = wx.StaticText(
            self, label='Plot all data on the same figure; default is ' +
            'separate figures')
        grid.Add(self.same_plot_text, pos=(row_count, 0))
        self.same_plot = wx.CheckBox(self)
        grid.Add(self.same_plot, pos=(row_count, 1))

        # Checkbox to select separate horz and vert plotting
        row_count += 1
        self.plot_avg_text = wx.StaticText(
            self, label='Plot average MTF; default is separate horz and vert')
        grid.Add(self.plot_avg_text, pos=(row_count, 0))
        self.plot_avg = wx.CheckBox(self)
        grid.Add(self.plot_avg, pos=(row_count, 1))

        # ~~~~~~~~~~

        # "Run!" button
        row_count += 2
        self.run_button = wx.Button(self, label='Run!')
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.run_button)
        grid.Add(self.run_button, pos=(row_count, 1))

        # ~~~~~~~~~~

        # Set up the grid
        hSizer.Add(grid, 0, wx.ALL, 5)
        mainSizer.Add(hSizer, 0, wx.ALL, 5)
        self.SetSizerAndFit(mainSizer)

    ''' When "Run!" is clicked, then run the "plot_all" function from the
    "plot_MTF" module. '''
    def OnClick(self, event):
        # Mandatory entries
        if self.select_dir.GetPath() == '':
            wx.MessageBox('Please select a directory.', 'Error')
            return

        if self.freqs.GetValue() == '':
            wx.MessageBox('Please enter at least one frequency.', 'Error')
            return

        if len(self.freqs.GetValue().split(',')) > 6:
            wx.MessageBox('Cannot use more than six spatial frequencies.',
                          'Error')
            return

        colors = ['b', 'r', 'g', 'c', 'y', 'k']
        maximize_plot = True  # always maximize the plot

        # Run the plotting function
        process_THF_file.plot_all(
            self.select_dir.GetPath(),
            self.plots_down.GetValue(),
            self.plot_title.GetValue(),
            self.freqs.GetValue(),
            self.spec_lines.GetValue(),
            self.plot_avg.GetValue(),
            self.same_plot.GetValue(),
            colors,
            maximize_plot)


app = wx.App(False)
frame = MyFrame(None)
panel = MyPanel(frame)
frame.Show()
app.MainLoop()
