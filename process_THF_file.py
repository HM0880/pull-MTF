import numpy as np
import os
import matplotlib
matplotlib.use('wxAgg')
import matplotlib.pyplot as plt
import time
from datetime import datetime

t0 = time.clock()

def pull_horz_MTF(path):
    """
    Returns a Numpy array of the all the horizontal data in the through-focus
    MTF data file at "path".

    From stackoverflow.com/questions/18865058/extract-values-between-two-
         strings-in-a-text-file-using-python

    Parameters
    ==========
    path : string
        through-focus MTF data file ending in ``.thf`` or ``.THF``

    Returns
    =======
    output : array
        numpy.ndarray of all the horizontal MTF data in "path"

    Notes
    =====
    Data will be saved between the strings "Horizontal Freq (lp/mm)  MTF @"
    and "Vertical Freq (lp/mm)  MTF @" (not including those strings).

    There is a corresponding function (``pull_vert_MTF``) that pulls the
    vertical MTF data.

    Code from stackoverflow.com/questions/18865058/extract-values-between-two-
    strings-in-a-text-file-using-python

    See Also
    ========
    pull_vert_MTF
    """
    horz = []

    with open(path) as infile:
        copy = False
        for line in infile:
            if line.strip() == "Horizontal Freq (lp/mm)  MTF @":
                copy = True
            elif line.strip() == "Vertical Freq (lp/mm)  MTF @":
                copy = False
            elif copy:
                horz.append(line.strip().split('\t'))

    # Delete first and last line from "horz", since those are empty lines
    # +++ WORK -- a more robust method is needed +++
    horz = horz[1:len(horz)-1]

    return np.asarray(horz).astype(float)


def pull_vert_MTF(path):
    """
    Returns a Numpy array of all the vertical data in the through-focus MTF
    data file at "path".

    Parameters
    ==========
    path : string
        through-focus MTF data file ending in ``.thf`` or ``.THF``

    Returns
    =======
    output : array
        numpy.ndarray of all the vertical MTF data in "path"

    Notes
    =====
    Data will be saved between the strings "Vertical Freq (lp/mm)  MTF @"
    and "Defocus Intensity Data: Horiz	Vert" (not including those strings).

    There is a corresponding function (``pull_horz_MTF``) that pulls the
    horizontal MTF data.

    See Also
    ========
    pull_horz_MTF
    """
    vert = []

    with open(path) as infile:
        copy = False
        for line in infile:
            if line.strip() == "Vertical Freq (lp/mm)  MTF @":
                copy = True
            elif line.strip() == "Defocus Intensity Data: Horiz	Vert":
                copy = False
            elif copy:
                vert.append(line.strip().split('\t'))

    return np.asarray(vert).astype(float)


def pull_MTF_data(path, desired_freqs):
    """
    Pulls all the horizontal or vertical data stored in "path", averages
    the horizontal + vertical data, then extracts the row vectors corresponding
    to the desired input frequencies.

    Returns three Numpy arrays of the horizontal, vertical, and average MTF
    data corresponding to the desired spatial frequencies.

    Parameters
    ==========
    path : string
        through-focus MTF data file ending in ``.thf`` or ``.THF``

    desired_freqs : 1D list of floats
        :todo: work on (1) type and (2) documentation of "desired_freqs"

        The user will enter the frequencies into the GUI (``plot_MTF_GUI.py``)
        as a comma-separated string, and then the GUI splits the string by the
        commas, converts it to a +++Numpy array+++, sorts from smallest to
        largest, and converts the type to float.

    Returns
    =======
    output : three arrays (horizontal, vertical, and average MTF data)
        :todo: returns as list of arrays???

        #. ``horz[all_idx]`` -- horizontal data at the desired frequencies
        #. ``vert[all_idx]`` -- vertical data at the desired frequencies
        #. ``average_MTF[all_idx]`` -- average data at the desired frequencies

        :todo: Throw an error if the user inputs a freq that isn't in the data.
    """
    # Pull all data
    horz = pull_horz_MTF(path)
    vert = pull_vert_MTF(path)

    # Average horz and vert; this is an array of *all* the freqs in the file
    average_MTF = np.add(horz, vert)/2

    # Make a list of all the frequencies in the average MTF data
    all_freqs = [row[0] for row in average_MTF]

    # Make a list of the row indices of the desired frequencies
    all_idx = [
        idx for idx, current_freq in enumerate(all_freqs)
        for user_freq in desired_freqs if current_freq == user_freq]

    # Slice out the desired data and return the arrays
    return horz[all_idx], vert[all_idx], average_MTF[all_idx]


def pull_defocus(path):
    """
    Pulls the defocus data at the end of the file and returns it.

    Parameters
    ==========
    path : string
        through-focus MTF data file ending in ``.thf`` or ``.THF``

    Returns
    =======
    defocus : array of floats
        The defocus positions in microns along the :math:`z` axis as a
        numpy.ndarray of floats
    """
    defocus = []

    with open(path) as infile:
        copy = False

        for line in infile:
            if line.strip() == "Defocus Position":
                copy = True
            elif line.strip() == "":
                copy = False
            elif copy:
                defocus.append(line.strip().split('\t'))

    return np.asarray(defocus).astype(float)


def flatten_and_name_array(path, slicename, input_array):
    """
    Flattens and names input arrays so that they can be easily saved to a
    external file.  Used in ``plot_one_THF_file``.

    Parameters
    ==========
    path : string
        Complete path name.  This function will split the path and extract
        only the filename, which will be used for the final output.

    slicename : string
        Can be any name, but must *not* have the "sep" value used to join the
        names in "filename" below.

    input_array : numpy.ndarray
        The MTF data to be flattened.  The input freq is the first entry of
        this array.

    Returns
    =======
    name : string
        The slicename and the spatial frequency.  Obtained from the first
        entry in ``named_array``.

    named_output :  list
        Returns the MTF data in a flattened list format with the first entry
        in the format ``filename slicename at freq``.

    See Also
    ========
    plot_one_THF_file
    """
    # Split "input_array" and keep the frequency and data +++ WORK +++
    freq, data = np.split(np.transpose(input_array), [1])

    # Create the output name
    filename = os.path.basename(path)[:-4]  # the "-4" removes ".thf" extension
    sep = ' '
    named_output = [
        filename + sep + '% MTF' + sep + slicename + sep + 'at' + sep +
        str(freq[0]) + sep + 'lp/mm']

    # Now go through the data and convert each entry to a string, and
    # then append it to "named_output"
    for number in data.tolist():  # omit the first entry (the freq)
        named_output.append(str(number))

    # "filename", "at", "freq", and "lp/mm" will show up as
    # separate entities when "split" is used below
    name_length = 4
    name = (' ').join(named_output[0].split(sep)[-name_length:])

    return name, named_output


def plot_one_THF_file(path, title, freqs, spec_lines, plot_avg, input_colors):
    """
    For one given path and desired input frequencies, extract and plot at
    least one through-focus MTF curve as a function of defocus position.

    Parameters
    ==========
    path : string
        through-focus MTF data file ending in ``.thf`` or ``.THF``

    title : string
        title for the plot

    freqs : 1D list of floats
        :todo: work on (1) the type and (2) the documentation

    spec_lines : 1D list of floats
        horizontal lines for MTF specs

    plot_avg : boolean
        If true, then plot the average of the MTF.  Otherwise, plot horizontal
        and vertical MTF separately.

    Returns
    =======
    output_data : list
        Returns a list of the MTF(s) at the desired spatial frequencies with
        the first entry in the format ``filename SLICENAME at freq``, where
        ``SLICENAME`` is either "horz", "vert", or "avg".

    Displays a plot
        Plot of the MTF for the user-selected frequencies.  Uses
        solid lines with points for the horizontal data and dashed lines with
        points for the vertical data.
    """
    defocus = pull_defocus(path)  # defocus positions along the z-axis
    horz, vert, avg = pull_MTF_data(path, freqs)  # MTF at desired freqs

    # Put the defocus data into "output_data"; it's a little hokey, but it
    # creates a list of the defocus values, so that we will end up with a
    # lists of lists at the end
    output_data = []
    filename = os.path.basename(path)[:-4]  # the "-4" removes ".thf" extension
    defocus_vec = [filename + ' defocus (um)']
    for sublist in defocus.tolist():
        for number in sublist:
            defocus_vec.append(str(number))
    output_data.append(defocus_vec)

    # Plot the data
    for n in range(len(avg)):
        color = input_colors[n]

        # Plot MTF as a function of defocus position
        if plot_avg:
            # Use the *entire* vector (i.e. "avg" and *not* "avg_plot_vec"),
            # since "flatten_and_name_array" uses the first entry for the
            # spatial freq
            slicename_avg = 'avg'
            input_array = avg[n]
            name_avg, current_avg = flatten_and_name_array(
                path, slicename_avg, input_array)
            output_data.append(current_avg)

            # Omit the first value from "avg", which is the spatial frequency
            plt.plot(
                defocus, avg[n][1:], '.-', linewidth=1, c=color,
                label=name_avg)

        else:
            # Process the data for output
            slicename = 'horz'
            input_array = horz[n]  # use the entire vector (i.e. horz)
            name_horz, current_horz = flatten_and_name_array(
                path, slicename, input_array)
            output_data.append(current_horz)

            slicename = 'vert'
            input_array = vert[n]  # use the entire vector (i.e. vert)
            name_vert, current_vert = flatten_and_name_array(
                path, slicename, input_array)
            output_data.append(current_vert)

            # Plot the results
            plt.plot(
                defocus, horz[n][1:], '.-', linewidth=1, c=color,
                label=name_horz)
            plt.plot(
                defocus, vert[n][1:], '.:', linewidth=1, c=color,
                label=name_vert)

        # Title, legend, y-axis limits, axis labels
        plt.title(title, fontsize=12, fontweight='bold')
        plt.ylim((0, 100))
        plt.xlabel('defocus position (um)')
        plt.ylabel('% MTF')
        ax = plt.gca()  # get current axes
        plt.setp(ax.get_xticklabels(), fontsize=10, rotation='vertical')
        plt.setp(ax.get_yticklabels(), fontsize=10)

        # Plot spec lines as horizontal, black, dotted lines
        for m in range(len(spec_lines)):
            min_x = ax.get_xlim()[0]  # Use this so the spec lines are always
            max_x = ax.get_xlim()[1]  # the exact width of the plot

            plt.plot((min_x, max_x), (spec_lines[m], spec_lines[m]), 'k:')

    # For debugging...
#    plt.show()
#    plt.close()

    return output_data


def get_all_file_paths(selected_dir):
    """
    Walks through the selected directory, and if the file path ends in ``.thf``
    or ``.THF``, then that path is appended to a list.

    This is used to plot multiple ``.thf`` files by generating the list of
    ``.thf`` paths and then feeding that list to the :func:`.plot_single_THF`
    function, which will then step through the list and plot each file.

    Parameters
    ==========
    selected_dir : string
        path to a folder (i.e. directory) containing at least one ``.thf`` file

        .. todo:: throw error if no .thf file in directory

    Returns
    =======
    all_paths : list of strings
        Returns a list of all the paths ending in ``.thf`` or ``.THF`` in the
        selected directory.

    See Also
    ========
    plot_single_THF
    """
    all_paths = [
        os.path.join(dir_name, file_name)
        for dir_name, sub_dir_list, file_list in os.walk(selected_dir)
        for file_name in file_list
        if file_name.lower().endswith('.thf')]

    return all_paths


def plot_all(
    selected_dir, plots_down, main_title, freqs, spec_lines, plot_avg,
        same_plot, colors, maximize_plot):
    """
    For a given directory with ``.thf`` files and at least one spatial
    frequency, plot all the data from the ``.thf`` files at the given
    frequency(s).

    Parameters
    ==========
    selected_dir : string
        path to the folder containing the ``.thf`` files to plot

    plots_down : integer (optional parameter in the GUI)
        Number of rows of subplots.

        If only there is one file in the directory, then ``plots_down`` is set
        to 1.

        If the user specifies more rows than there are plots to be made, then
        ``plots_down`` is set to the number of ``.thf`` paths in the directory.
        This will produce a plot with that has 1 column and N rows, where N is
        the number of ``.thf`` paths in the directory.

        If no value is entered into the GUI, then the GUI code sets "2" as the
        default ``plots_down`` value.

    main_title : string (optional parameter in the GUI)
        Super-title above all the subplots

    freqs : comma-separated string of desired spatial frequencies
        :todo: work on (1) the type and (2) the documentation of desired_freqs

        This function sorts "freqs" from lowest to highest.

        :warning: None of the other functions sort the frequencies.  Only this
            top-level function does.

    spec_lines : comma-separated string of desired spec lines
        (Optional parameter in the GUI)
        Horizontal lines for MTF specs.  If no value is entered, then
        "spec_lines" is set to [0].  This function sorts "spec_lines" from
        lowest to highest.

    plot_avg : boolean
        If true, then plot the average of the MTF.  Otherwise, plot horizontal
        and vertical MTF separately.

    same_plot : boolean
        If true, then plot all the MTF curves on the same plot.  Otherwise,
        plot each file's MTF curves on a separate subplot.

    maximize_plot : boolean
        If true, then maximize the plot window.  This is used in the wxPython
        GUI only.

    Returns
    =======
    output : Displays a plot
        A plot is produced with each ``.thf`` path as its own subplot.  There
        can be multiple spatial frequencies on each subplot.
    """
    all_paths = get_all_file_paths(selected_dir)  # get all paths

    # Establish the value of "plots_down".
    if plots_down == '':       # if nothing is entered,
        plots_down = 2  # then set to 2
    # If needed, override the user-entered value of "plots_down"
    elif len(all_paths) == 1:  # only one file in the directory
        plots_down = 1
    elif len(all_paths) < int(plots_down):  # more rows than there are plots
        plots_down = len(all_paths)
    else:
        plots_down = int(plots_down)

    # Calculate the "plots_across" value
    plots_across = np.ceil(len(all_paths)/float(plots_down)).astype(int)

    # Sort the frequencies +++ WORK +++
    freqs_sorted = np.sort(np.asarray(freqs.split(',')).astype(float))

    # Sort the spec lines
    if spec_lines == '':                # if nothing is entered,
        specs_sorted = np.ndarray([0])  # then set to 0
    else:
        specs_sorted = np.sort(
            np.asarray(spec_lines.split(',')).astype(float))

    # Set the figure size before plotting
    plt.figure(figsize=(16, 12))

    # If in GUI mode, maximize the plot window
    if maximize_plot:
        # plt.switch_backend('wxAgg')
        mng = plt.get_current_fig_manager()
        mng.frame.Maximize(True)

    # Plot the requested data
    if same_plot:  # plot all curves on the same plot
        for current_path in all_paths:
            if plot_avg:
                title = 'Average % MTF of overlapping corridors'
            else:
                title = 'Horz and vert % MTF of overlapping corridors'
            plot_one_THF_file(
                current_path, title, freqs_sorted, specs_sorted,
                plot_avg, colors)

    else:  # loop through the files and plot separately
        subplot_idx = 1
        for current_path in all_paths:
            title = os.path.basename(current_path)  # get the file name
            plt.subplot(plots_down, plots_across, subplot_idx)  # set supblot
            plot_one_THF_file(
                current_path, title, freqs_sorted, specs_sorted, plot_avg,
                colors)
            subplot_idx += 1

        # Add one master legend
        # http://matplotlib.org/1.3.1/users/legend_guide.html#legend-location
        plt.legend(
            bbox_to_anchor=(1.02, 1.0), loc='upper left',
            borderaxespad=0, fontsize=10)

        # Tweak subplot spacing
        plt.subplots_adjust(hspace=0.7, wspace=0.3)

    # Concatenate the plot supertitle
    plt.suptitle(
        main_title + '\n' + selected_dir + '\n' +
        str(datetime.now().strftime('%B %d, %Y')),
        fontsize=14, fontweight='bold')

    # Adjust the spacing so suptitle won't overlap the plots
    plt.subplots_adjust(top=0.85)

    plt.show()
#    plt.close(fig)

    print 'done!'

# -----------------------------------------------------------------------------

# Testing

'''
selected_dir = 'C:\ds\+++update plot_MTF -- s1c corridor'
path = "C:\ds\+++update plot_MTF -- s1c corridor\set1a+17-0.thf"
plots_down = 2
main_title = 'test'
freqs = [52, 104]  # +++ WORK on format (**string** or list of floats???) +++
spec_lines = '40'
plot_avg = False
data_output_path = 'c:/ds/woo.xlsx'
same_plot = True
maximize_plot = False

colors = ['b', 'r', 'g']
# aa = plot_one_THF_file(path, 'title', freqs, spec_lines, plot_avg, colors)

all_paths = [
    "C:/ds/+++update plot_MTF -- s1c corridor/set1a+17-0.thf",
    "C:/ds/+++update plot_MTF -- s1c corridor/set1a-33-90.thf"]
for path in all_paths:
    plot_one_THF_file(
        path, os.path.basename(path), freqs, spec_lines, plot_avg, colors)

#freqs2 = '52, 104'
#plot_all(
#    selected_dir, plots_down, main_title, freqs2, spec_lines, plot_avg,
#    same_plot, colors, maximize_plot)

t1 = time.clock()

print ' '
print "total time was " + str('{:.2f}'.format(t1-t0)) + ' seconds'
'''
