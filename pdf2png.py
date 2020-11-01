# -*- coding: utf-8 -*-

# standard modules
import argparse
import os
import random
import shutil
import subprocess
import sys
import time

# 3rd party modules
import psutil


"""
PDF2PNG
~~~~~~~~~~~~~~~~~~~~~
Purpose: Mass conversion of all pages of PDF files to PNG to run a ML system against the images to ensure 
    no inappropriate images exists in document/media library. 

Features:    
    - Automatic spawning of multi-processes is built-in (see below)
    - A "stop signal" to end conversions after the current file(s) being processed are completed.
    - File list randomization is ON by default to greatly lower the risk of two processes picking up the same 
    file at the exact same time. There is only a brief window where this can happen and file list randomization
    was added to handle that. 
         
Requirements: GhostScript -- the current path to GhostScript is hardcoded. I plan to add registry determination 
    of the GS path in a future version.

Basic usage:
    pdf2png.py -t
    Toggles the existence of the stop_conv.txt file in the user directory. If the "stop signal" file exists,
    conversions will stop after the current file conversions complete. This allows a simple and orderly way 
    to stop the file conversions without manual intervention and cleanup.  
    
    pdf2png.py -i "M:\PDF Library" -o "F:\WorkDirectoryPNGImages" -c "F:\Completed"
    Parse all PDFs located in M:\PDF Library and its subdirectories to the work directory. 
        Move Page _0001 to F:\Completed so that we can keep track of which files have been converted
        and which have not   
        
    pdf2png.py -i "M:\PDF Library" -o "F:\WorkDirectoryPNGImages" -c "F:\Completed" -sc 80
    [S]pawning up to [C]PU utilization percentage
    Multi-Process Spawning of self until CPU utilization reaches 80%. There is a 15 second delay
    giving the prior process time to ramp up, with the exact same command-line except -sc is dropped.
    
    pdf2png.py -i "M:\PDF Library" -o "F:\WorkDirectoryPNGImages" -c "F:\Completed" -sn 5
    [S]pawning [n]umber of processes
    Multi-Process Spawning of self into a new process to value given. In this example 5 processes are started with the 
    exact same command-line except -sn is dropped.
    
"""


__author__ = "Stephen Genusa"
__license__ = "BSD 2-Clause Simplied"
__status__ = "Production"


def if_stop_before_next_file():
    return os.path.isfile(os.path.join(os.path.expanduser("~"), "stop_conv.txt"))


def toggle_start_stop_signal():
    sig_filename = os.path.join(os.path.expanduser("~"), "stop_conv.txt")
    if os.path.isfile(sig_filename):
        os.remove(sig_filename)
        print("Stop signal file removed. Conversions will continue")
    else:
        with open(sig_filename, "w") as sig_file:
            sig_file.write("stop")
            print("Stop signal file created. Conversions will stop after current conversions complete.")


def test_directory(dir_path, path_name):
    if not os.path.isdir(dir_path):
        print(path_name, ": Path does not exist")
        sys.exit()


def does_png_file_exist(png_file_number, pdf_filename, output_path, archive_path):
    filen, ext = os.path.splitext(pdf_filename)
    filename_to_test_for = \
        os.path.join(output_path, filen + "_000" + str(png_file_number) + ".png")
    archive_file_to_test_for = \
        os.path.join(archive_path, filen + "_000" + str(png_file_number) + ".png")
    return os.path.exists(filename_to_test_for) or os.path.exists(archive_file_to_test_for)


def convert_pdf_to_png(pdf_fullpath_filename, output_path, archive_path):
    pdf_filename = os.path.basename(pdf_fullpath_filename)
    if not does_png_file_exist(1, pdf_filename, output_path, archive_path):
        print("Processing:", pdf_fullpath_filename)
        filen, _ = os.path.splitext(pdf_filename)
        output_filename = os.path.join(output_path, filen) + "_%04d.png"
        args = [r"c:\Program Files\gs\gs9.52\bin\gswin64c.exe", "-dNOPAUSE", "-dBATCH", "-sDEVICE=png16m", "-r300",
                "-sOutputFile=" + output_filename, pdf_fullpath_filename]
        print(args)
        process = subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr)
        process.wait()
    else:
        print("Already processed:", pdf_fullpath_filename)


def cleanup_checked_images(output_path, archive_path):
    try:
        file_list = os.listdir(output_path)
        for png_filename in file_list:
            if "_0001" in png_filename:
                pdf_filename_to_test_for = os.path.join(output_path, png_filename).lower().replace("_0001.png", ".pdf")
                if not does_png_file_exist(2, pdf_filename_to_test_for, output_path, archive_path):
                    archive_filename = os.path.join(archive_path, os.path.basename(png_filename))
                    shutil.move(os.path.join(output_path, png_filename), archive_filename)
    except Exception:
        pass


def convert_files_in_path(args):
    file_list = []
    for root, dirs, files in os.walk(args.input_path):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                file_list.append(os.path.join(root, filename))
    if args.reverse:
        file_list.reverse()
    if args.random:
        random.seed(int(str(time.time()).replace(".", "")[::-1][:8]))
        random.shuffle(file_list)
    total_files = len(file_list)
    for idx, filename in enumerate(file_list):
        if if_stop_before_next_file():
            print("Stop signal detected. Conversions halted.")
            sys.exit()
        print("*" * 40)
        print("*", idx, "of", total_files)
        print("*" * 40)
        convert_pdf_to_png(filename, args.output_work_path, args.completed_path)
        cleanup_checked_images(args.output_work_path, args.completed_path)
    print("All conversions complete")


def get_cpu_utilization():
    print("Getting average CPU utilization. Please wait...")
    cpu_use = psutil.cpu_times_percent(15)
    print("\t", cpu_use)
    return 100 - cpu_use.idle


def start_new_process(options):
    os.system("start cmd /k python " + __file__ + " " + options)


def start_processes(args):
    processes_to_create = args.spawn
    spawn_to_cpu_utilization = args.spawn_to_cpu_utilization
    args.spawn = None
    options = ""
    # ["--" + key.replace("_", "-") + '="' + str(args.__dict__[key]) + '"' for key in args.__dict__.keys()]
    for key in args.__dict__.keys():
        if key in ["input_path", "output_work_path", "completed_path"]:
            options += " --" + key.replace("_", "-") + '="' + str(args.__dict__[key]) + '"'
    print(options)
    # spawn until CPU utilization is at desired max user setting
    if spawn_to_cpu_utilization:
        while get_cpu_utilization() < spawn_to_cpu_utilization:
            start_new_process(options)
    # spawn fixed # of processes
    else:
        for _ in range(0, processes_to_create):
            time.sleep(0.3)
            start_new_process(options)


def main():
    parser = argparse.ArgumentParser(prog="PDF2PNG by Stephen Genusa October 2020")
    parser.add_argument('-r', '--reverse', required=False, action='store_true', default=False,
                        help='process files in reverse')
    parser.add_argument('-g', '--random', required=False, action='store_true', default=True,
                        help='process files in random order')
    parser.add_argument('-i', '--input-path', required=False, action='store', type=str,
                        help='input path of PDF files')
    parser.add_argument('-o', '--output-work-path', required=False, action='store', type=str,
                        help='work path to send PNG files to')
    parser.add_argument('-c', '--completed-path', required=False, action='store', type=str,
                        help='completed conversion path - saves _0001 image files to determine if file tested or not')
    parser.add_argument('-sn', '--spawn', required=False, action='store', type=int,
                        help='number of processes to spawn')
    parser.add_argument('-sc', '--spawn-to-cpu-utilization', required=False, action='store', type=int,
                        help='spawn until CPU utilization %% reached')
    parser.add_argument('-t', '--toggle-signal', required=False, action='store_true',
                        help='toggle the start/stop signal')
    args = parser.parse_args()

    if args.toggle_signal:
        toggle_start_stop_signal()
    else:
        if args.spawn or args.spawn_to_cpu_utilization:
            start_processes(args)
        else:
            test_directory(args.input_path, "-i Input path")
            test_directory(args.input_path, "-o Output path")
            test_directory(args.input_path, "-c Completed path")
            convert_files_in_path(args)


if __name__ == '__main__':
    main()
