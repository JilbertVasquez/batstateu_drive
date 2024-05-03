import os
import shutil

def bytes_to_gb(bytes_value):
    gb_value = bytes_value / (1024 * 1024 * 1024)
    return gb_value

def get_disk_usage(folder_path):
    # Get the drive letter from the folder path
    drive_letter = os.path.splitdrive(folder_path)[0]

    # Get disk usage information for the drive
    disk_usage = shutil.disk_usage(drive_letter)
    
    # Convert bytes to GB
    total_gb = bytes_to_gb(disk_usage.total)
    used_gb = bytes_to_gb(disk_usage.used)
    free_gb = bytes_to_gb(disk_usage.free)
    
    # Return disk usage information in GB
    return {
        'total': total_gb,
        'used': used_gb,
        'free': free_gb
    }

# Example usage:
shared_folder = r'\\Ict-pc1\pc1'
shared_folder = r'\\DESKTOP-5S162M5\doc'
disk_usage_info = get_disk_usage(shared_folder)
print(f"Total Space: {disk_usage_info['total']:.2f} GB")
print(f"Used Space: {disk_usage_info['used']:.2f} GB")
print(f"Free Space: {disk_usage_info['free']:.2f} GB")
