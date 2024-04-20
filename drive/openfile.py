import os

MEDIA_ROOT = r'\\DESKTOP-UUTKA7R\uploadedfiles\folder1\ggg'




file_path = os.path.join(MEDIA_ROOT, 'portrait.jpg')
with open(file_path, 'r') as file:
    content = file.read()
    print(content)
