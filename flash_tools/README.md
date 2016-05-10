To batch (in parallel) flash device with adb and fastboot tool
Simply run python image_flasher.py and it will automatically update decives.

This tool will update following partitions:
boot
system
cache
userdata

Initial condition:

1 Please ensure your devices are adb attachable, because script need adb reboot-bootlaoder to reset to boot loader

2 Please ensure your adb, fastboot tool are available in search path.
(Script uses 'which adb' to get full adb path)

3 Please specify your image folder in variable IMAGE_ROOT_PATH

4 If output log is annoying, just set DEBUG to False
