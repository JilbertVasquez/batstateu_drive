import os
user_directory = r"D:\Thesis\batstateu_drive\uploadedfiles"

print("Root directory:", user_directory)

contents = os.listdir(user_directory)

folders = [item for item in contents if os.path.isdir(os.path.join(user_directory, item))]

print("Folders in the root directory:")
# for folder in folders:
#     print(folder)

print(folders)