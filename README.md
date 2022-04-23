# Auto-HandBrake-Transcoder

## Info and Background

My dad records a LOT of videos, so a few years ago I got him a NAS.

I needed a way to reduce the size of videos on the NAS to be able to store more of them.
Going through with HandBrake and manually selecting files or folders would take FOREVER, so I wrote this script to run through the desired folder and automatically transcode video files.

## Requirements

- HandBrakeCLI - The main part of this program. This does the actual transcoding.
- ExifTool - Attempts to copy video tags and details to the newly transcoded video file.

Both are included within this repo.

## Usage

Currently, only the windows amd version is in the repo. If you need something other than that, download from the official [Handbrake website](https://handbrake.fr/downloads2.php)

```bash
python transcode.py <target-folder> [-r] [-hb-path] [-e] [-s] [--hours]
```

`<target-folder> REQUIRED:` path to target folder.

`[-r --recursive] OPTIONAL:` Adding this will transcode all video files within the target folder and its subfolders.

`[--hb-path <handbrakecli-path>] OPTIONAL:` Defaults to 'HandBrakeCLI.exe' within the called folder.

`[-e --exiftool-path <exiftool-path>] OPTIONAL:` Defaults to 'exiftool.exe' within the called folder.

`[-s --stop-time <HH:MM>] OPTIONAL:` (Not reliable) Add if you want the program to stop after a specific time (24h time 00:00 ==> 23:59). (I believe it only works if the time input is a larger overall minute than the current time.)

`[--hours <hour(s)> OPTIONAL:` Add this if you want the program to run for a specific amount of hours

**_`If neither --hours or --stop-time are given, the program will run until it finishes or encounters an error.`_**

I've included a HandBrake preset file within this repo, if you would like to make your own preset, download the regular non CLI HandBrake and change settings within it. Then, export the preset and name it `handbrake-preset.json` and put it in the main folder that the `transcode.py` file is stored.

The preset file is 720p 128bit audio. You can open the file to look at more of it's details.

## Thanks

Let me know if I should add/change something.
Good luck!

## TODO

- Add platform check and ask user to install required programs
- Change to system installs of programs. If it's unable to find them, check the folder, else return exception.
