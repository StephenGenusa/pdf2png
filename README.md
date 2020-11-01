# PDF2PNG

**Author**: Stephen Genusa

**Date**: October 2020

**Purpose**: Mass conversion of all pages of PDF files to PNG to run an ML system against the images to ensure no inappropriate images exists in document/media library.

**License**: BSD 2-Clause Simplified

###Features:###

- Automatic spawning of multi-processes is built-in (see below)
- A "stop signal" to end conversions after the current file(s) being processed are completed.
- File list randomization is ON by default to greatly lower the risk of two processes picking up the same file at the exact same time. There is only a brief window where this can happen and file list randomization was added to handle that. 
         
###Requirements:###
GhostScript -- the current path to GhostScript is hardcoded. I plan to add registry determination of the GS path in a future version.

###Basic usage:###

####Toggle Stop Signal [-t]####

    pdf2png.py -t
    
Toggles the existence of the stop_conv.txt file in the user directory. If the "stop signal" file exists, conversions will stop after the current file conversions complete. This allows a simple and orderly way to stop the file conversions without manual intervention and cleanup.  

####Basic Single Process File Conversion####
    
    pdf2png.py -i "M:\PDF Library" -o "F:\WorkDirectoryPNGImages" -c "F:\Completed"

Parse all PDFs located in M:\PDF Library and its subdirectories to the work directory. Moves Page _0001 to F:\Completed so that we can keep track of which files have been converted and which have not   
        
####[S]pawning up to [C]PU utilization percentage####

    pdf2png.py -i "M:\PDF Library" -o "F:\WorkDirectoryPNGImages" -c "F:\Completed" -sc 80

Multi-Process Spawning of self until CPU utilization reaches 80%. There is a 15 second delay giving the prior process time to ramp up, with the exact same command-line except -sc is dropped.

####[S]pawning [n]umber of processes####
    
    pdf2png.py -i "M:\PDF Library" -o "F:\WorkDirectoryPNGImages" -c "F:\Completed" -sn 5

Multi-Process Spawning of self into a new process to value given. In this example 5 processes are started with the exact same command-line except -sn is dropped.
    
