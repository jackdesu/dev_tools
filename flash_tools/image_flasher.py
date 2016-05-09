import subprocess
import os
import time

DEBUG = True

IMAGE_ROOT_PATH = """please specify your image dir path here"""
BOOT_NAME = "boot"
SYSTEM_NAME = "system"
CACHE_NAME = "cache"
USERDATA_NAME = "userdata"
IMAGE_EXTENSION = ".img"
ADB = "adb"
FASTBOOT = "fastboot"
FLASH_COMMAND = "flash"
ARG_REBOOT_TO_BOOTLOADER = "reboot-bootloader"
ARG_REBOOT = "reboot"
ARG_DEVICE_SPECIFY = "-s"

FULL_UPDATE_PARTITION = [BOOT_NAME, SYSTEM_NAME, CACHE_NAME, USERDATA_NAME]


def execute_command(*args):
    if DEBUG:
        print "execute_command: ", args
    device_popen = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return device_popen.communicate()


def get_tool_full_path(tool_name):
    comm = execute_command("which", tool_name)
    return comm[0].strip()


def file_exist(file_name):
    return os.path.isfile(file_name)


ADB_TOOL = get_tool_full_path(ADB)
FASTBOOT_TOOL = get_tool_full_path(FASTBOOT)


def get_device_id_fastboot():
    if not file_exist(FASTBOOT_TOOL):
        print "fastboot does not exits at:", FASTBOOT_TOOL
        return list()

    comm = execute_command(FASTBOOT_TOOL, "devices")
    tmp = comm[0].split()
    ids = list()
    for x in range(0, len(tmp), 2):
        ids.append(tmp[x])
    return ids


def get_device_id_adb():
    if not file_exist(ADB_TOOL):
        print "adb does not exists at:", ADB_TOOL
        return list()

    comm = execute_command(ADB_TOOL, "devices")
    temp = comm[0].split()
    result = list()
    for x in range(len(temp)-2, 3, -2):
        result.append(temp[x])

    return result


def flash_img(device, partition_name):
    if None is device:
        command_result = execute_command(FASTBOOT_TOOL, FLASH_COMMAND, partition_name,
                                         IMAGE_ROOT_PATH + partition_name + IMAGE_EXTENSION)
    else:
        command_result = execute_command(FASTBOOT_TOOL, ARG_DEVICE_SPECIFY, device, FLASH_COMMAND, partition_name,
                                         IMAGE_ROOT_PATH + partition_name + IMAGE_EXTENSION)

    return "finished. total time:" in command_result[1]


def on_devices_flash_complete(results):
    for result in results.items():
        on_flash_complete(result[0], result[1])


def on_flash_complete(device_id, result):
    if len(result) > 0:
        failure_partition_list = list()
        for index in range(0, len(result), 1):
            if result[index] is False:
                failure_partition_list.append(index)
        generate_flash_complete_report(device_id, failure_partition_list)
        print "Update complete"


def generate_flash_complete_report(device_id, failure_partition_list):
    if len(failure_partition_list) > 0:
        print "device:", device_id, "update complete but some partition cannot be updated correctly :"
        for index in range(0, len(failure_partition_list), 1):
            print "[", FULL_UPDATE_PARTITION[failure_partition_list[index]], "]"


def reboot_to_bootloader(tool, ids):
    for idx in range(0, len(ids), 1):
        execute_command(tool, ARG_DEVICE_SPECIFY, ids[idx], ARG_REBOOT_TO_BOOTLOADER)


def reboot_to_bootloader_with_adb():
    device_ids_w_adb = get_device_id_adb()
    if len(device_ids_w_adb) > 0:
        reboot_to_bootloader(ADB, device_ids_w_adb)

    retry_count = 1
    while True:
        device_ids_w_fastboot = get_device_id_fastboot()

        if retry_count > 4:
            print "reboot to bootloader timeout with", retry_count, "tries."
            break

        if not len(device_ids_w_fastboot) != device_ids_w_adb:
            retry_count += 1
            time.sleep(3)
            print retry_count
            continue
        else:
            break
    return device_ids_w_adb


def flash_devices(device_ids):
    total_result = {}
    if len(device_ids) > 0:
        for device_idx in range(0, len(device_ids)):
            device_result = list()
            current_device_id = device_ids[device_idx]
            for partition_idx in range(0, len(FULL_UPDATE_PARTITION)):
                device_result.append(flash_img(current_device_id, FULL_UPDATE_PARTITION[partition_idx]))
            execute_command(FASTBOOT_TOOL, ARG_DEVICE_SPECIFY, current_device_id, ARG_REBOOT)
            total_result[device_idx] = device_result
    else:
        print "no device connected"

    return total_result


boot_loader_device_ids = reboot_to_bootloader_with_adb()
flash_results = flash_devices(boot_loader_device_ids)
on_devices_flash_complete(flash_results)
