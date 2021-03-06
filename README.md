# splitSURVEY

splitSURVEY is an interactive tool that lets you split subbottom profiler data (or any other SEG-Y files) according to locations picked from the navigation. The tool reads an entire folder of SEG-Y data and plots the navigation from all the headers. From here the user can select points along the navigation to break the data into line files. For subbottom profiler data, this makes it easier to create lines that correspond with the navigation of the survey, and can also be used to trim unwanted data from the dataset or create composite lines with data from multiple surveys.

The code is functional but there are likely a number of things that could be improved or tidied up - so feedback is welcomed! There are a few features that I would like to add in the future, but have not implemented yet:

- Editable preferences window for changing projection, sample rate settings, export settings, etc.
- Different picking modes

## Using the tool

To run the tool, navigate to the directory with the command prompt and run splitSURVEY.py. This will launch the main window.

How to import SEGY's and split them into lines:

1. Click 'Import' and navigate to the folder containing the SEG-Y files you want to import (can do an entire survey if you want)
2. Click 'Output Folder' to choose the destination to output your SEG-Y files
3. Give the survey a Cruise ID
4. Click 'Plot' to plot the navigation from all the input SEG-Y files (this might take a while if doing a large volume of files)
5. You can now start picking the 'split' locations by selecting points along the navigation and pressing the 'Z' key (or clicking 'Split'). The zoom and pan tools in the toolbar can be used to move around.
6. 'N' and 'M' keys can be used to move the current selection forward and backward in the navigation.
7. If you need to undo a split location you can click the 'Undo split' button, or press 'X'. If you want to clear all of your splits you can click 'Clear splits', or press 'C'.
8. When you are happy with the split locations you can click 'Split Survey' which will export your split SEG-Y files to the folder you specified.
9. 'Splits' and 'Surveys' can be saved using the export buttons. These can then be imported later to save you from having to reload all the SEG-Y files if you get interrupted. Splits are saved automatically upon export.

### Libraries

The tool is built using the following libraries, so you will need to have these installed if you do not already:
* [Obspy](http://www.obspy.org) - for SEG-Y I/O
* [Matplotlib](https://matplotlib.org/) - for plotting/certain UI elements
* [PyQt5](https://pypi.org/project/PyQt5/) - for the UI
* [PyProj](https://pypi.org/project/pyproj/) - for projection of navigation

These are also listed in the requirements.txt file.

## License

GNU-GPL - see the [LICENSE.md](LICENSE.md) file for details


