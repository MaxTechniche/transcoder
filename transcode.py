import os
import time
import sys
import argparse
import datetime as dt

parser = argparse.ArgumentParser(description="Handbrake Transcoding")
parser.add_argument(
    "-hb-path",
    required=False,
    default=os.path.join(os.getcwd(), "HandBrakeCLI.exe"),
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
    default=os.path.join(os.getcwd(), "exiftool.exe"),
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
    help="The time you want the program to stop. (00:00 - 23:59)",
)
parser.add_argument(
    "--hours",
    required=False,
    default=None,
    type=int,
    nargs="?",
    dest="hours",
    help="The number of hours the program should run. HH:MM",
)

args = parser.parse_args()

if args.stop_time:
    stop_time = list(map(int, args.stop_time.split(":")))
    if stop_time[0] < 0 or stop_time[0] > 23 or stop_time[1] < 0 or stop_time[1] > 59:
        raise argparse.ArgumentTypeError(
            "%s is an invalid time input." % ":".join([str(x) for x in stop_time])
        )

preset_file = os.path.join(os.getcwd(), "handbrake-preset.json")

base_dir = os.getcwd()

video_extentions = "mp4,ts,mov,mkv,avi,vob,flv,mpg,3g2,3gp,wmv,m4v,mpeg,f4v,m2ts".split(
    ","
)

start_time = time.time()

info = []

if not os.path.exists(args.exiftool_path):
    print("ExifTool path required")
    exit()


def remove_file(filepath):
    try:
        os.remove(filepath)
    except PermissionError:
        print("File currently in use by another proccess.")
    except FileNotFoundError:
        pass


def copy_metadata(old_file, new_file):
    exiftool_path = args.exiftool_path
    os.system(f'{exiftool_path} -TagsFromFile "{old_file}" "{new_file}"')
    return


for dirpath, dirs, files in os.walk(args.target):
    if "#recycle" in dirpath:
        continue
    for filename in files:
        if args.stop_time:
            hour = stop_time[0] - int(time.localtime()[3])
            minute = stop_time[1] - int(time.localtime()[4]) + (hour * 60)
            if minute <= 0:
                print(*info, sep="\n")
                exit()
        if args.hours:
            if (time.time() - start_time) / 3600 >= args.hours:
                print(*info, sep="\n")
                exit()
        filepath = dirpath + os.sep + filename
        name, ext = os.path.splitext(filepath)
        new_filepath = name + "-transcoded.mp4"

        if ext[1:].lower() not in video_extentions:
            continue
        if os.path.exists(name + "-transcoded.mp4"):
            remove_file(filepath)
            continue

        if filename.endswith("-transcoded.mp4"):
            if os.path.exists(name[:-2] + ext):
                remove_file(name[:-2] + ext)
            continue

        try:
            os.system(
                f'{args.hb_path} -i "{filepath}" -o "{name}-transcoded.mp4" --preset-import-file {preset_file}'
            )
            copy_metadata(filepath, new_filepath)
            if os.path.exists(new_filepath):
                remove_file(filepath)
                remove_file(new_filepath + "_original")
            info.append(f"{new_filepath} transcoded successfully")
        except FileNotFoundError:
            pass
        except Exception as e:
            info.append(e)
            print(*info, sep="\n")
            raise e

        except KeyboardInterrupt:
            print("KEYBOARD INTERUPT!!")
            print("MAKING SURE FILE IS SAFELY HANDLED")
            if os.path.exists(filepath):
                if os.path.exists(new_filepath):
                    remove_file(new_filepath)
                print("Removed unfinished transcoded file!")
            print("FILE WAS SAFELY HANDLED")
            raise KeyboardInterrupt("FILE WAS SAFELY HANDLED!")

    if not args.recursive:
        break

print(*info, sep="\n")
exit()
