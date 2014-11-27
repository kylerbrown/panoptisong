panoptisong
===========

scripts for monitoring songbird song via the jack/jill framework


Installation
--------

Clone this repository: `git clone https://github.com/kylerbrown/panoptisong.git`

Ensure you have a working copy of JACK and [Jill](https://github.com/melizalab/jill).

birds
------
Edit the file `birds` to include your birds and their microphone channels. Rows starting with # are ignored. The three positional variables are BIRD BOX CHANNEL. For example, the line 

    bk196 1 system:capture_3

means a bird name bk196 in box 1 has a microphone channel system:capture_3. You may specify additional channels after the first channel, which will also be recorded at the same time. The first channel is the triggered channel. For exammple, the line:

    o43 4 system:capture_5 system:capture_6

will record both `system:capture_5` and  `system:capture_6` when a signal from `system:capture_5` passes the jdetect threshold.


Other Parameters
----------------
Edit `panoptisong.sh` to change variables such as the name of the experimenter, the species, etc.


Running
----------
Try running `bash panoptisong.sh` to ensure it's working.

Finally either
+ use `dailyreset.sh`, you can open the file and edit the time of day to reset.
+ or edit cron to start a recording everday by typing `crontab -e`. To reset at noon every day add the line `0 12 * * * ~/panoptisong/panoptisong.sh`
