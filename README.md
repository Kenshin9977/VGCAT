# Video Game Console Analytics Tool

The purpose of this tool is to analyze a footage taken from a video game console and then deduce the actual FPS based on the difference between each frame. 

## Features

Currently the results are saved within a CSV file and an .mp4 file which has an FPS counter at the top left corner.

## Limits

If the video is too static (menus of a game for instance) the difference between each frame isn't great enough to be detected. In this case a wrong number might be detected for frame per second and frame time. This issue can not be bypassed so please take it into account if you use this software.

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

## How to read the results

The results given with the CSV can be opened with any spreadsheet software.
Each row corresponds to a frame. The FPS column gives the average frametime of every frame within one second then converted to FPS.
The frametime column gives the time it took to render a frame.
The frametime FPS columns gives the frametime converted to FPS if every frame within one second took the same time to render. 

## Acknowledgments

* OpenCV Library
* DigitalFoundry and GamerNexus for explaining the concept
