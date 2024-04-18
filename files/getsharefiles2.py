import os

def get_shared_drives(share_path):
    # Check if the shared folder exists
    if os.path.exists(share_path):
        # List the contents of the shared folder
        shared_drives = os.listdir(share_path)

        # Filter out directories (drives)
        shared_drives = [drive for drive in shared_drives if os.path.isdir(os.path.join(share_path, drive))]

        return shared_drives
    else:
        print(f"Shared folder '{share_path}' does not exist.")
        return []

# Example usage:
share_path = r"\\Laptop-jj9q7d10\K"
shared_drives = get_shared_drives(share_path)
print("Shared drives on", share_path)
print(shared_drives[-1])
