*******************************************************************************
Readme
*******************************************************************************

Still a work-in-progress.

Motivation
===============================================================================

.. note:: This code works on Windows 7, 32-bit and 64-bit.


Optikos LensCheck benches produce ``.thf`` (through-focus)
`MTF <https://en.m.wikipedia.org/wiki/Modulation_transfer_function>`__ files.
This GUI was designed to be an easy and flexible yet powerful way to plot any
number of these ``.thf`` files in a given folder.

Four sample data files are in this repository's ``data`` folder.

Sphinx auto-generated  documentation of the source code modules is +++here+++.


GUI design evolution from v1.0 to v2.0
===============================================================================

_static\plot_MTF_v1.0_screenshot.PNG
   :align: center

   Version 1.0 GUI.


_static\plot_MTF_v2.0_screenshot.PNG
   :align: center

   Version 2.0 GUI


Sample output
===============================================================================

Below are some examples of the plots that this GUI can produce.

_static\default.PNG
   :align: center

   The default plotting results (with an optional title).


_static\multiple_freq_and_spec.PNG
   :align: center

   Multiple spatial frequencies and a single horizontal specification line.


_static\avg_MTF.PNG
   :align: center

   The average MTF of multiple spatial frequencies with the same horizontal
   spec line as above.  Also demonstrates the result of entering "1" in
   the "Number of rows on the plot" field.


_static\same.PNG
   :align: center

   All data on the same figure.  Useful for visualizing the defocus positions
   (i.e. the horizontal axis) where the MTF values from multiple tests are
   above the specification line.