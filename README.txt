# Video Game Console Analytics Tool

The purpose of this tool is to analyze a footage taken from a video game console and then deduce the actual FPS based on the difference between each frame. 

## Features

Currently the results are saved within a CSV file and an .mp4 file which has an FPS counter at the top left corner.

## Downloads

Binaries for Windows are available in the [Releases](https://github.com/Kenshin9977/VGCAT/releases) section.

## Usage

Open a console and put the path to the video file as an argument.
```
VGCAT.exe --input C:/file_to_analyze.avi
```

You can also use the argument '--debug' which will output every binary image to the folder Debug at the same location than VGCAT.exe.
```
VGCAT.exe C:/file_to_analyze.avi --debug
```

And '--help' for a detailed help
```
VGCAT.exe --help
```

## Acknowledgments

* OpenCV Library
* DigitalFoundry and GamerNexus for explaining the concept
