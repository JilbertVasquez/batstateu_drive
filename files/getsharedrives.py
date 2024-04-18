import os

def get_shared_drives(domain_name):
    # Construct the path to the domain's shared folder
    shared_folder_path = r"\\{}".format(domain_name)

    # Check if the shared folder exists
    if os.path.exists(shared_folder_path):
        # List the contents of the shared folder
        shared_drives = os.listdir(shared_folder_path)

        # Filter out directories (drives)
        shared_drives = [drive for drive in shared_drives if os.path.isdir(os.path.join(shared_folder_path, drive))]

        return shared_drives
    else:
        print(f"Shared folder '{shared_folder_path}' does not exist.")
        return []

# Example usage:
domain_name = "Laptop-jj9q7d10"
shared_drives = get_shared_drives(domain_name)
print("Shared drives on", domain_name)
print(shared_drives)
