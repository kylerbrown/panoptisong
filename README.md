panoptisong
===========

scripts for monitoring birdsong via the jack/jill framework


Installation
--------

Clone this repository: `git clone https://github.com/kylerbrown/panoptisong.git`

Ensure you have a working copy of JACK and [Jill](https://github.com/melizalab/jill).

If you want to use the GUI, also make sure you have [urwid](http://urwid.org/) installed.
You can either do `pip install urwid`, or download urwid from the site and unpack the urwid folder
into the panoptisong folder.


Using the GUI
----------
You can run `python gui.py` to edit the parameters and birds settings. The GUI contains hints
explaining some of the parameters. You can creating profiles, which follow the convention `myconfig_parameters` and `myconfig_birds`. When you start recording from the GUI (ctrl + p),
the current settings as saved as profile `_tmp`, which is then used as setting to panoptisong.
You can make use of the profiles even when running panoptisong from the command line, by typing
`./panoptisong my_config` (but you can use the default files with just `./panoptisong`)

birds
------
Edit the file `birds` to include your birds and their microphone channels. Rows starting with # are ignored. The four positional variables are BIRD BOX EXPERIMENTER CHANNEL. The values are separated with tabs. For example, the line 

    bk196 1 bob system:capture_3

means a bird name bk196 in box 1 has a microphone channel system:capture_3, and belongs to the person bob. You may specify additional channels after the first channel, which will also be recorded at the same time. The first channel is the triggered channel. For exammple, the line:

    o43 4 jack system:capture_5 system:capture_6

will record both `system:capture_5` and  `system:capture_6` when a signal from `system:capture_5` passes the jdetect threshold.


Other Parameters
----------------
Edit the `parameters` file to change variables such as the name of the experimenter, the species, etc.
Make sure the jackd parameters are correctly set, and the right sound card is loaded. The command `jackd_lsp` can help to ensure the chosen sound card has the expected number of channels.


Running
----------
Try running `bash panoptisong` to ensure it's working.

Panoptisong will create a new file for each bird every day. This keeps file sizes managable and provides an easy way to summarize the quantity of song by looking at the size of the files. To change the time at which new files are made, modify the `reset_time` variable in `parameters`. For normal light cycle use "00:00", for reversed use the middle of the subjective night.


Checking Free Space
-------------------
The script 'bird_space' will give a disk usage summary. To use, type `bash bird_space`.


Automatic Backup
----------------
Set the variable `backup_location` in the parameters file to have panoptisong automatically backup all the recordings to a (optionally) remote location automatically. You must have valid ssh public key authentication if the backup location is on a remote computer.