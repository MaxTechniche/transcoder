#!/usr/bin/env python3
import os
import time
import sys
from shutil import which
import subprocess
import platform
import argparse
import datetime as dt

SECONDS_IN_DAY = 60 * 60 * 24

def get_handbrake_path():
    if platform.system() == "Darwin":
        return os.path.join(os.getcwd(), "HandBrakeCLI")
    else:
        return os.path.join(os.getcwd(), "HandBrakeCLI.exe")
    
def get_exiftool_path():
    if platform.system() == "Darwin":
        if which("exiftool"):
            return "exiftool"
    else:
        return os.path.join(os.getcwd(), "exiftool.exe")

parser = argparse.ArgumentParser(description="Handbrake Transcoding")
parser.add_argument(
    "--hb-path",
    required=False,
    default=get_handbrake_path(),
    nargs=1,
    dest="hb_path",
    help="Path to CLI HandBrake file",
)
parser.add_argument(
    "target",
    help="File or top level directory to start transcoding.",
)
parser.add_argument(
    "-r",
    "--recursive",
    required=False,
    default=False,
    action="store_true",
    dest="recursive",
    help="Transcode the target directory recursively",
)
parser.add_argument(
    "-e",
    "--exiftool-path",
    required=False,
    default=get_exiftool_path(),
    nargs=1,
    dest="exiftool_path",
    help="Path to exiftool for metadata copying.",
)
parser.add_argument(
    "-s",
    "--stop-time",
    required=False,
    default=None,
    nargs="?",
    dest="stop_time",
    help="The time you want the program to stop 24hr time. (00:00 - 23:59)",
)
parser.add_argument(
    "--run-time",
    required=False,
    default=None,
    nargs="?",
    dest="run_time",
    help="The number of hours and/or minutes the program should run. (0+:0-59) OR (0-) for only minutes if you wish to not calculate.",
)
parser.add_argument(
    "--no-exif",
    required=False,
    default=False,
    action="store_true",
    dest="no_exif",
    help="Add this argument if you wish to not use exif",
)
parser.add_argument(
    "-j",
    "--json",
    required=False,
    default=os.path.join(os.getcwd(), "handbrake-preset.json"),
    dest="preset_file",
    help="Path to the preset file",
)
parser.add_argument(
    "--prefix",
    required=False,
    default="",
    dest="prefix",
    help="String that you wish to use for the prefix.",
)
parser.add_argument(
    "--postfix",
    required=False,
    default="-transcoded",
    dest="postfix",
    help="String that you wish to use for the postfix.",
)

args = parser.parse_args()
print(args.exiftool_path)
preset_file = args.preset_file
postfix = args.postfix + ".mp4"

base_dir = os.getcwd()

video_extentions = "mp4,ts,mov,mkv,avi,vob,flv,mpg,3g2,wmv,m4v,mpeg,f4v,m2ts".split(",")

start_time = dt.datetime.today()


def calculate_stop_time(args):
    if not args.stop_time and not args.run_time:
        return
    if args.stop_time:
        stop_time = list(map(int, args.stop_time.split(":")))
        if not (0 <= stop_time[0] < 24) or not (0 <= stop_time[1] < 60):
            raise argparse.ArgumentTypeError(
                "%s is an invalid time input." % ":".join([str(x) for x in stop_time])
            )
        stop_time = start_time.replace(hour=stop_time[0], minute=stop_time[1])
        if (stop_time - start_time).total_seconds() < 0:
            stop_time = stop_time + dt.timedelta(days=1)
    if args.run_time:
        a = list(map(int, args.run_time.split(":")))
        if len(a) == 1:
            run_time = start_time + dt.timedelta(minutes=a)
        elif len(a) == 2:
            if a[1] > 59:
                raise argparse.ArgumentTypeError(
                    f"{a[0]}:{a[1]} is an invalid time input."
                )
            run_time = start_time + dt.timedelta(hours=a[0], minutes=a[1])
        else:
            raise argparse.ArgumentTypeError(f"{a[0]}:{a[1]} is an invalid time input.")
    if args.stop_time and args.run_time:
        stop_time = min(stop_time, run_time)

    return stop_time


stop_time = calculate_stop_time(args)

info = []

if not os.path.exists(args.exiftool_path):
    if args.no_exif:
        print("ExifTool file path required")
        exit()


def check_stop(start_time, stop_time):
    if stop_time < dt.datetime.today():
        print("Stoping due to stop time")
        exit()


def remove_file(filepath):
    try:
        os.remove(filepath)
    except PermissionError:
        print("File currently in use by another proccess.")
    except FileNotFoundError:
        pass


def copy_metadata(old_file, new_file):
    subprocess.call([args.exiftool_path, '-TagsFromFile', old_file, new_file])
    # os.system(f'{exiftool_path} -TagsFromFile "{old_file}" "{new_file}"')
    return


for dirpath, dirs, files in os.walk(args.target):
    if "#recycle" in dirpath:
        continue

    for filename in files:

        if stop_time:
            check_stop(start_time, stop_time)

        filepath = dirpath + os.sep + filename
        name, ext = os.path.splitext(filepath)
        new_filepath = args.prefix + name + postfix

        if ext[1:].lower() not in video_extentions:
            print(f"Skipping '{name + ext}' due to unknown extention.")
            continue

        if os.path.exists(name + postfix):
            remove_file(filepath)
            continue

        if filename.endswith(postfix):
            if os.path.exists(name[:-2] + ext):
                remove_file(name[:-2] + ext)
            continue

        try:

            subprocess.call([args.hb_path, '-i', filepath, '-o', args.prefix + name + postfix, '--preset-import-file', preset_file])
            # os.system(
            #     f'{args.hb_path} -i "{filepath}" -o "{args.prefix + name + postfix}" --preset-import-file {preset_file}'
            # )
            if not args.no_exif:
                copy_metadata(filepath, new_filepath)

            if os.path.exists(new_filepath):
                remove_file(filepath)
                remove_file(new_filepath + "_original")

            info.append(f"{new_filepath} transcoded successfully")

        except FileNotFoundError:
            pass

        except KeyboardInterrupt:
            print("KEYBOARD INTERUPT!!")
            print("MAKING SURE FILE IS SAFELY HANDLED")
            if os.path.exists(filepath):
                if os.path.exists(new_filepath):
                    remove_file(new_filepath)
                print("Removed unfinished transcoded file!")
            print("FILE WAS SAFELY HANDLED")
            raise KeyboardInterrupt("FILE WAS SAFELY HANDLED!")

        except Exception as e:
            info.append(e)
            print(*info, sep="\n")
            raise e

    if not args.recursive:
        break

print(*info, sep="\n")
exit()
