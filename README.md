panoptisong
===========

scripts for monitoring songbird song via the jack/jill framework


Usage
--------

Clone this repository: `git clone https://github.com/kylerbrown/panoptisong.git`

Edit the file `birds` to include your birds and their microphone channels.

Edit `panoptisong.sh` to change variables such as the name of the experimenter, the species, etc.

Try running `bash panoptisong.sh` to ensure it's working.

Finally either
+ use `dailyreset.sh`
+ or edit cron to start a recording everday by typing `crontab -e`. To reset at noon every day add the line `0 12 * * * ~/panoptisong/panoptisong.sh`
