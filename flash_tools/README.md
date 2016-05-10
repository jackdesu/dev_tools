To batch (in parallel) flash device with adb and fastboot tool
Simply run python image_flasher.py and it will automatically update decives.

Initial condition:
1 Please ensure your adb, fastboot tool are available in search path.
(Script uses 'which adb' to get full adb path)

2 Please specify your image folder in variable IMAGE_ROOT_PATH

3 If output log is annoying, just set DEBUG to False

I plan to read variable from a configuration file, ex XXX.config.
Just a TBD.
