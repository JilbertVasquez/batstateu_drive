from django.shortcuts import render, HttpResponse
# from django.contrib.auth.models import User
from .models import Users, FileDetails
from .models import SharingFiles
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
import os
import shutil
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
import time

from cryptography.fernet import Fernet

def encrypt_file(input_file_path, output_file_path, key):
    print("fileeeee dataaaaaaa", input_file_path)
    """
    Encrypts a file using Fernet encryption.
    
    Args:
    - input_file_path: Path to the input file to be encrypted.
    - output_file_path: Path to save the encrypted output file.
    - key: Fernet encryption key.
    """
    
    batstateu = b'batstateukey'
    combined = key + batstateu
    # print(']]]]]]]]]]]]]]]]]]]]]]]')
    # print(type(key))
    cipher_suite = Fernet(key)
    # print(cipher_suite)
    with open(input_file_path, 'rb') as file:
        file_data = file.read()
        
    encrypted_data = cipher_suite.encrypt(file_data)

    with open(output_file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)
        

def decrypt_file(input_file_path, output_file_path, key):
    
    """
    Decrypts a file using Fernet encryption.
    
    Args:
    - input_file_path: Path to the input file to be decrypted.
    - output_file_path: Path to save the decrypted output file.
    - key: Fernet encryption key.
    """
    
    batstateu = b'batstateukey'
    # concat = key[2:-1]
    
    # key_bytes = base64.urlsafe_b64decode(concat.encode())
    
    # combined = key + batstateu
    # print(']]]]]]]]]]]]]]]]]]]]]]]')
    # print(type(key))
    # print(combined, 'COOOOOOOOOOOOOOOOOOOOOO')
    
    cipher_suite = Fernet(key)
    
    with open(input_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    print("dataaaaaaafileeeee", input_file_path)
    with open(output_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

# Create your views here.

def dashboard(request):
    username = request.session.get('username', None)
    userid = request.session.get('userid', None)
    user_upload_dir = os.path.join(settings.MEDIA_ROOT, username)
    
    contents = os.listdir(settings.MEDIA_ROOT)

    folders = [item for item in contents if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
    
    folder1 = [item for item in os.listdir(os.path.join(settings.MEDIA_ROOT, folders[0], username)) if os.path.isdir(os.path.join(settings.MEDIA_ROOT, folders[0], username, item))]
    # print(folder1)
    uploaded_files = []

    if username:
        try:
            user = Users.objects.get(username=username)
            userfiles = FileDetails.objects.filter(user_id = user.userid)
            
            for files in userfiles:
                uploaded_files.append({
                    'fileid': files.file_id,
                    'filename': files.filename,
                    'extension': files.extension,
                    'size': files.size,
                    'upload_date': files.upload_date,
                    'key': files.key,
                    'path': files.path 
                })
        
        except Exception as e:
            print(e)
            # uploaded_files.append({'name': file_name, 'size': file_size, 'last_modified': last_modified_date, 'is_dir': is_dir, 'full_path': file_path})  # Add full_path
        return render(request, 'dashboardextend.html', {'username': username, 'uploaded_files': uploaded_files, 'folders': folder1})
    else:
        return redirect('login')
    
def convert_size(size_bytes):
    # Define suffixes and corresponding divisor
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    divisor = 1024

    # Determine appropriate suffix and value
    for suffix in suffixes:
        if size_bytes < divisor:
            return f"{size_bytes:.2f} {suffix}"
        size_bytes /= divisor

    return f"{size_bytes:.2f} {suffixes[-1]}"  # Fallback to largest suffix

import json
from django.http import FileResponse
import shutil

def download_file(request):
    if request.method == 'POST':
        userid = request.session.get('userid', None)
        
        
        file_id = request.POST.get('itemid')
        
        file_details = FileDetails.objects.get(file_id=file_id)
        retrieved_paths_list = file_details.get_paths()
        # print(file_details.key, 'keyyyyyyyyyyyyyy')
        # for paths in retrieved_paths_list:
        #     print(paths)
        file_path = file_details.get_paths()[0]
        
        if os.path.exists(file_path):
            
            temp_path = os.path.join(settings.MEDIA_TEMP, file_details.filename + file_details.extension)
            
            encrypted_filepath = os.path.join(file_path, file_details.filename + file_details.extension)
            # print("----------------", temp_path)
            with open('key.txt', 'rb') as key_file:
                key = key_file.read()
            decrypt_file(encrypted_filepath, temp_path, key)
            
        # Construct the response with X-Sendfile header
            response = HttpResponse(content_type='application/force-download')
            response['Content-Disposition'] = f'attachment; filename="{file_details.filename}{file_details.extension}"'
            response['X-Sendfile'] = settings.MEDIA_TEMP

            # Optionally, set additional headers
            
            # response['Content-Length'] = os.path.getsize(file_path)
            
            # delete_temp = os.path.join(file_path, str(file_details.filename + file_details.extension))
            # os.remove(delete_temp)

            return response
        else:
            return HttpResponse("File not found", status=404)
    else:
        return HttpResponse("Method not allowed", status=405)
    
def download_share_file (request):
    pass


def delete_share_files(request):
    pass

def delete_item(request):
    if request.method == 'POST':
        username = request.session.get('username', None)
        userid = request.session.get('userid', None)
        itemid = request.POST.get('itemid')
        
        try:
            file_details = FileDetails.objects.get(file_id=itemid)
            share_details = SharingFiles.objects.filter(file=file_details).first()

            item_path = file_details.path
            
            if item_path:
                paths = file_details.get_paths()
                for path in paths:
                    
                    if os.path.exists(path):
                        file_path = os.path.join(path, str(file_details.filename + file_details.extension))
                        # print(path)
                        # print(file_path)
                        os.remove(file_path)
            
            file_details.delete()
            if share_details:
                share_details.delete()
            
            return redirect('dashboard')
            
        except FileDetails.DoesNotExist:
            return HttpResponse("File not found", status=404)
        except SharingFiles.DoesNotExist:
            return HttpResponse("Sharing information not found", status=404)
        
    else:
        return HttpResponse("Method not allowed", status=405)

def delete_item_search(request):
    if request.method == 'POST':
        username = request.session.get('username', None)
        userid = request.session.get('userid', None)
        item_path = request.POST.get('item_path')  # Get the full item path
        item_name = request.POST.get('item_name')
        if username and item_path:
            if os.path.exists(item_path):
                try:
                    # os.remove(item_path + "\\" + item_name)  # Delete file
                    os.remove(os.path.join(item_path))
                    # return JsonResponse({'success': True, 'message': 'Item deleted successfully'})
                    # deleted_item_directory = os.path.dirname(item_path)
                    return redirect('view_folder', folder_path=os.path.dirname(item_path))
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error deleting item: {str(e)}'})
            else:
                return HttpResponse("Item not found", status=404)
        else:
            return HttpResponse("Invalid request", status=400)
    else:
        return HttpResponse("Method not allowed", status=405)

def get_folder_contents(folder_path):
    """
    Recursive function to get the contents of a folder and its subfolders.
    Returns a list of dictionaries containing information about files and folders.
    """
    contents = []
    for item_name in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item_name)
        is_dir = os.path.isdir(item_path)
        item_info = {'name': item_name, 'is_dir': is_dir}
        if is_dir:
            # Recursively get contents of subfolders
            item_info['contents'] = get_folder_contents(item_path)
        item_info['full_path'] = item_path  # Set the full path
        contents.append(item_info)
    return contents


def view_folder(request, folder_path):
    username = request.session.get('username', None)
    userid = request.session.get('userid', None)
    folder_path = os.path.join(settings.MEDIA_ROOT, username, folder_path)
    uploaded_items = []

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # Retrieve contents of the folder and its subfolders
        uploaded_items = get_folder_contents(folder_path)
    else:
        return HttpResponse("Folder not found", status=404)

    # Update full_path attribute for each item
    for item in uploaded_items:
        item['full_path'] = os.path.join(folder_path, item['name'])
        
    parent_directory = os.path.dirname(folder_path)
    if parent_directory == settings.MEDIA_ROOT:
        return redirect('dashboard')
    else:
        return render(request, 'dashboardextend.html', {'uploaded_files': uploaded_items, 'current_directory': folder_path, 'parent_directory': parent_directory, 'username': username})

'''
def search(request):
    query = request.GET.get('query')
    username = request.session.get('username')
    current_directory = request.GET.get('current_directory')
    
    if current_directory == "":
        current_directory = os.path.join(settings.MEDIA_ROOT, username)
    
    retrieved_files = {}    

    if query == "":
        return render(request, 'dashboardextend.html')
    # user_filenames = FileDetails.objects.filter(filename__icontains=query)
    search_results = FileDetails.objects.filter(filename__icontains=query)
    

    
    return render(request, 'search_form.html', {
        'search_results': search_results,
        'current_directory': current_directory,
        'query': query,  # Pass the query back to the template for displaying in the search input field
        'username': username
    })
    
'''


# views.py

# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from .models import SharingFiles, FileDetails
# from django.contrib import messages

# def share_file(request):
#     if request.method == 'POST':
#         username = request.session.get('username', None)
#         current_directory = request.POST.get('current_directory', '')
#         # if current_directory == "":
#         #     current_directory = os.path.join(settings.MEDIA_ROOT, username)
#         curr_dir = os.path.join(settings.MEDIA_ROOT, username, current_directory)
#         item_name = request.POST.get('itemname', '')
#         item_name2 = item_name.split(".")[0]
#         print(item_name2)
#         print(curr_dir)
#         item_path = request.POST.get('item_path', None)
#         email = request.POST.get('email', None)

#         try:
#             recipient = Users.objects.get(email=email)
#             print(recipient.email, recipient.userid, curr_dir, item_name2)
#             # Check if the file exists in the file_details table
#             file_entry = FileDetails.objects.get(filename=item_name2, path=curr_dir)
#             print(file_entry.id)
#             print(recipient.email, recipient.userid, curr_dir, item_name2)
#             SharingFiles.objects.create(filename=item_name, file_id=file_entry, user_id=recipient, path=curr_dir, share_by=username, share_to=email)
#             print("SUCCESS")
#             messages.success(request, f'File shared with {email} successfully!')
#         except FileDetails.DoesNotExist:
#             messages.error(request, f'File with name {item_name2} does not exist in the specified path!')
#         except Users.DoesNotExist:
#             messages.error(request, f'User with email {email} does not exist!')

#         return redirect('dashboard')  # Redirect to the dashboard or appropriate URL after sharing
#     else:
#         # Handle GET request if needed
#         pass


def share_file(request):
    if request.method == 'POST':
        username = request.session.get('username', None)
        userid = request.session.get('userid', None)
        
        itemid = request.POST.get('itemid')
        email = request.POST.get('email', None)
        
        
        
        try:
            sharetouser = Users.objects.get(email=email)
            
            if sharetouser:
                fileuser = Users.objects.get(userid=userid)
                filedetails = FileDetails.objects.get(file_id=itemid)
                
                SharingFiles.objects.create(
                    filename = filedetails.filename,
                    extension = filedetails.extension,
                    share_by = fileuser.email,
                    share_to = sharetouser.email,
                    path = filedetails.path,
                    file=filedetails
                )
            
            else:
                return redirect('dashboard')
            
            messages.success(request, f'File shared with {email} successfully!')
            # print("SSUSSSSS")
        except FileDetails.DoesNotExist:
            messages.error(request, f'File with id {itemid} does not exist in the specified path!')
            # ("ASDADQWEQ")
        except Users.DoesNotExist:
            messages.error(request, f'User with email {email} does not exist!')
            # print("!@#!#")
            

        return redirect('dashboard')
    else:
        # Handle GET request if needed
        pass

from django.db.models import Q
def share_files_section(request):
    # Retrieve the username from the session
    username = request.session.get('username', None)
    
    if username:
        fileuser = Users.objects.get(username=username)
        
        share_file_details = []

        shared_files = SharingFiles.objects.filter(share_to=fileuser.email)
        file_ids = [shared_file.file_id for shared_file in shared_files]
        file_details = FileDetails.objects.filter(file_id__in=file_ids)

        # print(file_ids)
        # print(file_details)

        for share in shared_files:
            for details in file_details:
                if details.file_id == share.file_id:
                    share_file_details.append({
                        'fileid': details.file_id,
                        'filename': share.filename,
                        'extension': share.extension,
                        'share_by': share.share_by,
                        'share_to': share.share_to,
                        'path': share.path,
                        'size': details.size,
                        'upload_date': details.upload_date
                    })

        # Now share_file_details contains combined details from both SharingFiles and FileDetails
        # for detail in share_file_details:
        #     print(detail)
            

        
        #     print(i.path)
        # if current_directory == "":
        #     current_directory = os.path.join(settings.MEDIA_ROOT, 'username')
        return render(request, 'sharedfiles.html', {'shared_files': share_file_details})
    else:
        # Handle case where username is not found in the session
        # Redirect or render an error message as needed
        return render(request, 'error.html', {'message': 'Username not found in session'})




def search(request):
    query = request.GET.get('query')
    username = request.session.get('username')
    userid = request.session.get('userid', None)
    
    retrieved_files = []

    if query == "":
        return render(request, 'dashboardextend.html')
    
    files = FileDetails.objects.filter(Q(filename__icontains=query), user_id=userid).values('file_id', 'filename', 'size', 'extension', 'upload_date', 'path')
    
    
    search_results = []

    
    
    return render(request, 'search_form.html', {
        'search_results': files,
        'query': query,  # Pass the query back to the template for displaying in the search input field
        'username': username
    })

def get_formatted_file_size(file_size):
    # Convert bytes to appropriate unit (KB, MB, GB)
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if file_size < 1024.0:
            return f"{file_size:.2f} {unit}"
        file_size /= 1024.0


def rename_file(request):
    if request.method == 'POST':
        username = request.session.get('username')  
        item_path = request.POST.get('item_path')
        # if item_path == "":
        #     item_path = os.path.join(settings.MEDIA_ROOT)
        last_name = request.POST.get('lastname') # Retrieve the last filename from the hidden input
        last_name1 = last_name.split(".")
        last_name2 = last_name1[0]
        last_name3 = "." + last_name1[-1]
        new_name = request.POST.get('new_name')
        new_name1 = new_name.split(".")
        new_name2 = new_name1[0]
        new_name3 = "." + new_name1[-1]
        current_dir = request.POST.get("current_directory")
        if current_dir == "":
            current_dir = os.path.join(settings.MEDIA_ROOT, username) + "\\"
        # print(new_name)
        # print(last_name2)
        # print(current_dir)
        try:
            # Rename the file
            os.rename(item_path, os.path.join(os.path.dirname(item_path), new_name))
            
            user = Users.objects.get(username=username)
            userid = user.userid
            useremail = user.email
            
            # Update database record with new name
            file_detail = FileDetails.objects.get(filename=last_name2, extension=last_name3 ,path=current_dir, user_id=userid)
            file_detail.filename = new_name2
            file_detail.extension = new_name3
            file_detail.save()
            
            # Check if the file is shared by the user and update the filename in share_files table
            shared_files = SharingFiles.objects.filter(share_by=useremail, filename=last_name2, extension=last_name3, path=current_dir)
            for shared_file in shared_files:
                print(share_file)
                shared_file.filename = new_name2
                shared_file.extension = new_name3
                shared_file.save()
            
            # Return success response
            # return JsonResponse({'success': True})
            if current_dir == "":
                return redirect("dashboard")
            else:
                return redirect('view_folder', folder_path=current_dir)
        except Exception as e:
            # Handle renaming errors
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # Handle GET request or invalid method
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

def rename_folder(request):
    if request.method == 'POST':
        username = request.session.get('username')
        item_path = request.POST.get('item_path')
        last_name = request.POST.get('itemname')
        new_name = request.POST.get('new_name')
        current_dir = request.POST.get("current_directory")
        current_dir2 = ""
        
        newpath = ""
        if current_dir == "":
            current_dir2 = os.path.join(settings.MEDIA_ROOT, username, last_name)
            newpath = os.path.join(settings.MEDIA_ROOT, username, new_name)
        else:
            current_dir2 = current_dir

        # print(current_dir2)
        
        try:
            user = Users.objects.get(username=username)
            userid = user.userid
            
            file_details = FileDetails.objects.filter(path__contains=current_dir2, user_id=userid)
            shared_files = SharingFiles.objects.filter(path__contains=current_dir2)
            
            for file_detail in file_details:
                new_db_path = file_detail.path.replace(current_dir2, newpath)
                file_detail.path = new_db_path
                file_detail.save()
                
            for shared_file in shared_files:
                new_db_path = shared_file.path.replace(current_dir2, newpath)
                shared_file.path = new_db_path
                shared_file.save()
            
            
            # Rename the folder
            os.rename(item_path, os.path.join(os.path.dirname(item_path), new_name))
            # Return success response
            # return JsonResponse({'success': True})
            if current_dir == "":
                return redirect("dashboard")
            else:
                return redirect('view_folder', folder_path=current_dir)
        except Exception as e:
            # Handle renaming errors
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # Handle GET request or invalid method
        return JsonResponse({'success': False, 'error': 'Method not allowed'})




def handle_file_upload(request):
    if request.method == 'POST':
        # Check if files were uploaded
        if 'file' in request.FILES:
            uploaded_files = request.FILES.getlist('file')  # Get list of uploaded files
            
            username = request.session.get('username')
            userid = request.session.get('userid', None)
            current_directory = request.POST.get('current_directory', '')
            
            if username:
                # Get the User object for the logged-in user
                user = Users.objects.get(userid=userid)
                # user_upload_dir = os.path.join(settings.MEDIA_ROOT, username, current_directory)
                # print("_____________________" + user_upload_dir)
                # if not os.path.exists(user_upload_dir):
                #     os.makedirs(user_upload_dir)
                # fs = FileSystemStorage(location=user_upload_dir)
                
                
                
                for uploaded_file in uploaded_files:
                    try:
                        # file_details = get_file_details(uploaded_file, user_upload_dir)
                        # fs.save(uploaded_file.name, uploaded_file)  # Save each uploaded file
                        
                        
                        
                        contents = os.listdir(settings.MEDIA_ROOT)

                        folders = [item for item in contents if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
                        
                        # user_directory = os.path.join(settings.MEDIA_ROOT, uname)
                        
                        list_of_dir_copy = []
                        
                        for folder in folders:
                            key = Fernet.generate_key()
                            
                            print(key)
                            
                            user_directory = os.path.join(settings.MEDIA_ROOT, folder, username)
                            list_of_dir_copy.append(user_directory)
                            # print(list_of_dir_copy)
                            fs = FileSystemStorage(location=user_directory)
                            fs.save(uploaded_file.name, uploaded_file)
                            
                            input_file_path = os.path.join(user_directory, uploaded_file.name)
                            output_file_path = os.path.join(user_directory, uploaded_file.name)
                            # print(input_file_path)
                            # print(output_file_path)
                            encrypt_file(input_file_path, output_file_path, key)
                            # print("SS________________")
                        
                        
                        with open('key.txt', 'rb') as key_file:
                            key2 = key_file.read()
                        
                        file_details = get_file_details(uploaded_file, list_of_dir_copy)
                        save_file_details(user, file_details, key2)
                            
                        # input_file_path = os.path.join(user_upload_dir, uploaded_file.name)
                        # output_file_path = os.path.join(user_upload_dir, uploaded_file.name)
                        # encrypt_file(input_file_path, output_file_path, key)
                        
                        # file_details = get_file_details(uploaded_file, user_upload_dir)
                        # save_file_details(user, file_details)
                        
                        
                    
                        # if current_directory:
                            # Redirect back to the view_folder with the current directory path included
                        # return redirect(reverse('view_folder', kwargs={'folder_path': user_directory}))
                        return redirect('dashboard')
                        # else:
                            # Redirect to dashboard if current_directory is empty
                            # return redirect('dashboard')
                    
                    except Exception as e:
                        # Handle file upload error
                        return render(request, 'dashboard.html', {'error': str(e)})
                    
                # Redirect to the current page to update file list
                return redirect('dashboard')
            else:
                return redirect('dashboard')   # Redirect to login if user is not authenticated
    return redirect('dashboard')


def get_file_details(uploaded_file, file_path):
    """
    Function to extract details of an uploaded file.
    Returns a dictionary containing the file's name, size, extension, and upload date.
    """
    file_name = uploaded_file.name
    file_name_without_extension = os.path.splitext(file_name)[0]
    file_size = uploaded_file.size
    file_extension = os.path.splitext(file_name)[-1]
    
    # Convert file size to KB, MB, or GB based on magnitude
    if file_size < 1024:
        size_unit = 'B'
        size_value = file_size
    elif file_size < 1024 ** 2:
        size_unit = 'KB'
        size_value = file_size / 1024
    elif file_size < 1024 ** 3:
        size_unit = 'MB'
        size_value = file_size / (1024 ** 2)
    else:
        size_unit = 'GB'
        size_value = file_size / (1024 ** 3)
        
    size_value = str(round(size_value, 2)) + size_unit
    upload_date = timezone.now().strftime('%Y-%m-%d')
    
    file_details = {
        'filename': file_name_without_extension,
        'extension': file_extension,
        'size': size_value,
        'upload_date': upload_date,
        'path': file_path,
    }
    
    return file_details



def save_file_details(user, file_details, key):
    """
    Function to save file details into the database.
    """
    file_details_object = FileDetails.objects.create(
        user=user,
        filename=file_details['filename'],  # Use 'filename' instead of 'name'
        extension=file_details['extension'],
        size=file_details['size'],
        upload_date=file_details['upload_date'],
        key=key
    )
    file_details_object.set_paths(file_details['path'])
    file_details_object.save()
    
    print(key)
    
    file_details_objectss = FileDetails.objects.get(filename=file_details['filename'])
    
    if key == file_details_objectss.key:
        print("TUERRRRRRRRRRRRR")
    
    return file_details_object


def handle_folder_upload(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_folder = request.FILES['file']
            username = request.session.get('username', None)
            userid = request.session.get('userid', None)
            if username:
                user_upload_dir = os.path.join(settings.MEDIA_ROOT, username)
                if not os.path.exists(user_upload_dir):
                    os.makedirs(user_upload_dir)
                
                # Obtain the folder name
                folder_name = uploaded_folder.name
                
                # Create a folder for the uploaded directory
                directory_path = os.path.join(user_upload_dir, folder_name)
                os.makedirs(directory_path, exist_ok=True)
                
                # Iterate over the uploaded files and save each one
                for uploaded_file in uploaded_folder:
                    # Save the file with its original name inside the directory
                    fs = FileSystemStorage(location=directory_path)
                    fs.save(uploaded_file.name, uploaded_file)
                
                return redirect('dashboard')  # Redirect after successful upload
            else:
                return redirect('login')  # Redirect to login if user is not authenticated
    return render(request, 'dashboard.html')  # Render the same page if no file is uploaded or request method is not POST


def handle_create_folder(request):
    if request.method == 'POST':
        # Get the current username from session
        username = request.session.get('username', None)
        userid = request.session.get('userid', None)
        
        # Get the folder name and current directory from the POST request
        folder_name = request.POST.get('folder_name')
        current_directory = request.POST.get('current_directory')
        
        # Check if the current username and folder name are valid
        if username and folder_name:
            # Construct the full path to the new folder
            # new_folder_path = os.path.join(settings.MEDIA_ROOT, username, current_directory, folder_name)
            
            try:
                # Create the new folder
                # os.makedirs(new_folder_path, exist_ok=True)
                
                contents = os.listdir(settings.MEDIA_ROOT)

                folders = [item for item in contents if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
                
                # user_directory = os.path.join(settings.MEDIA_ROOT, uname)
                for folder in folders:
                    user_directory = os.path.join(settings.MEDIA_ROOT, folder, username, folder_name )
                    os.makedirs(user_directory, exist_ok=True)
                
                # Check if current_directory is not empty
                if current_directory:
                    # Redirect back to the view_folder with the current directory path included
                    return redirect(reverse('view_folder', kwargs={'folder_path': current_directory}))
                else:
                    # Redirect to dashboard if current_directory is empty
                    return redirect('dashboard')
            except Exception as e:
                # Handle any errors during folder creation
                return JsonResponse({'success': False, 'message': f'Error creating folder: {str(e)}'})
        else:
            # Return a response indicating missing data
            return JsonResponse({'success': False, 'message': 'Invalid request or missing data'})
    else:
        # Return a response indicating invalid request method
        return HttpResponse('Method not allowed', status=405)


def signupPage(request):
    if request.method == 'POST':
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password2')
        
        
        # Check if username already exists
        if Users.objects.filter(username=uname).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup.html', {'messages': messages})
        
        # Check if email already exists
        if Users.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'signup.html', {'messages': messages})
        
        if pass1 != pass2:
            messages.error(request, "Your password is not the same !!")
            return render(request, 'signup.html', {'messages': messages})
        else:
            hashed_password = make_password(pass1)
            my_user = Users(firstname=fname, lastname=lname, username=uname, email=email, password=hashed_password)
            my_user.save()
            
            contents = os.listdir(settings.MEDIA_ROOT)

            folders = [item for item in contents if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
            
            # user_directory = os.path.join(settings.MEDIA_ROOT, uname)
            for folder in folders:
                user_directory = os.path.join(settings.MEDIA_ROOT, folder, uname)
                os.makedirs(user_directory, exist_ok=True)
            
            return redirect('login')
        
    else:
        return render(request, 'signup.html')

def loginPage(request):
    if request.method == 'POST':

        email = request.POST.get("email")
        pass1 = request.POST.get("password")
        
        try:
            user = Users.objects.get(email=email)
            
            if check_password(pass1, user.password):
                # Passwords match, user authenticated
                request.session['username'] = user.username  # Storing username in session
                request.session['userid'] = user.userid
                return redirect('dashboard')
            else:
                return HttpResponse("Username or Password is incorrect")
            
        except Users.DoesNotExist:
            return HttpResponse("User does not exist!!")
        
    else:
        return render(request, 'login.html')

def logout(request):
    # Clear session data
    request.session.flush()
    # Redirect to the login page
    return redirect('login')