from django.shortcuts import render, HttpResponse
from .models import Users, FileDetails
from .models import SharingFiles
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from cryptography.fernet import Fernet
from django.http import FileResponse
from django.db.models import Q
import random
import time
import shutil
import re
from django.contrib.auth import authenticate, login
from concurrent.futures import ThreadPoolExecutor

# Create your views here.

def encrypt_file(input_file_path, output_file_path, key):
    cipher_suite = Fernet(key)
    
    with open(input_file_path, 'rb') as file:
        file_data = file.read()
        
    encrypted_data = cipher_suite.encrypt(file_data)

    with open(output_file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)


def decrypt_file(input_file_path, output_file_path, key):
    cipher_suite = Fernet(key)
    
    with open(input_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    
    with open(output_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)
        

def bytes_to_gb(bytes_value):
    gb_value = bytes_value / (1024 * 1024 * 1024)
    return gb_value


def get_disk_usage(folder_path):
    all_storage = []
    overall_used = 0
    length = 0
    total_used = 0
    total = 0
    
    for shared_folder in folder_path:
        if os.path.exists(shared_folder):
            disk_usage = shutil.disk_usage(shared_folder)
        
            percent_used = round(((disk_usage.used / disk_usage.total) * 100), 2)
            
            overall_used += percent_used
            length += 1
            
            overall = round(overall_used / length , 2)
            
            total_used += round(bytes_to_gb(disk_usage.used), 2)
            total += round(bytes_to_gb(disk_usage.total), 2)
            
            all_storage.append({
                'disk_used': round(bytes_to_gb(disk_usage.used), 2),
                'disk_total': round(bytes_to_gb(disk_usage.total), 2),
                
                'disk_percentage': percent_used
            })
            
            overall = round(overall, 2)
            total_used = round(total_used, 2)
            total = round(total, 2)

    return all_storage, overall, total_used, total


def disk_usage_view(request):
    
    contents = os.listdir(settings.MEDIA_ROOT)

    folders = [item for item in contents if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
    
    disk = [item for item in contents]
    
    drive = os.path.join(settings.MEDIA_ROOT, disk[0], 'drives.txt')
    
    shared_folder = []
    
    if os.path.exists(drive):
        with open(drive, 'r') as file:
            contents = file.read()
            # Process the contents as needed
            shared_folder = contents.strip().split('\n')
    else:
        print("File 'drives.txt' does not exist.")
    
    disk_usage_percentage, overall_used, total_used, total = get_disk_usage(shared_folder)
    
    context = {
        'disk_usage_percentage': disk_usage_percentage,
        'overall_used': overall_used,
        'total_used': total_used,
        'total': total
    }
    
    return render(request, 'disk_storage.html', context)


def admindashboard(request):
    username = request.session.get('username', None)
    if username:
        users = Users.objects.all()
        return render(request, 'useraccountsadmin.html', {'users': users})
    else:
        return redirect('adminlogin')


def adminlogin(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            request.session['username'] = user.username
            request.session['userid'] = user.id
            login(request, user)
            return redirect('admindashboard')
        else:
            errors = "Username or Password is incorrect"
            return render(request, 'adminlogin.html', {'errors': errors})
    else:
        return render(request, 'adminlogin.html')


def users_admin(request):
    users = Users.objects.all()
    return render(request, 'useraccountsadmin.html', {'users': users})


def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = Users.objects.get(userid=user_id)
            
            user_folders = [os.path.join(settings.MEDIA_ROOT, user_folder) for user_folder in os.listdir(settings.MEDIA_ROOT) if os.path.isdir(os.path.join(settings.MEDIA_ROOT, user_folder))]
            for folder in user_folders:
                dir = os.path.join(folder, user.username)
                if os.path.exists(dir):
                    shutil.rmtree(dir)   
            
            user.delete()
            messages.success(request, "Account Deletion successfully!")
            return redirect('admindashboard')
        except Users.DoesNotExist:
            pass
    return redirect('admindashboard')


def edit_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = Users.objects.get(userid=user_id)
            return render (request, 'editaccount.html', {'user': user})
        except Users.DoesNotExist:
            pass
    return redirect('admindashboard')


def save_edit_account(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')

        try:
            user = Users.objects.get(userid=user_id) 
            user.firstname = firstname
            user.lastname = lastname
            user.username = username
            user.email = email
            
            user.save()
            messages.success(request, "Account Details Update successfully!")
            return redirect('admindashboard')
        
        except Users.DoesNotExist:
            errors = "User does not exist"
            return render(request, 'edit_account.html', {'errors': errors})
    
    else:
        return redirect('admindashboard')


def new_pass(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = Users.objects.get(userid=user_id)
            return render (request, 'changepassword.html', {'user': user})
        except Users.DoesNotExist:
            pass
    return redirect('admindashboard')


def save_new_pass_acc(request):
    if request.method == 'POST':
        user_id = request.POST.get("user_id")
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("password2")
        
        if new_password == confirm_password:
            user = Users.objects.get(userid=user_id)
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Password updated successfully!")
        else:
            messages.error(request, "New password and confirm password do not match!")
            
    return redirect('admindashboard')


def trackfiledetails(request):
    username = request.session.get('username', None)
    if username:
        filedetails = FileDetails.objects.all()
        return render(request, 'trackfiledetails.html', {'filedetails': filedetails})
    else:
        return redirect('adminlogin')


def view_file_details(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        print(file_id)
        try:
            filedetails = FileDetails.objects.get(file_id=file_id)
            return render (request, 'viewfiledetails.html', {'filedetails': filedetails})
        except Users.DoesNotExist:
            pass
    return redirect('admindashboard')


def tracksharefiles(request):
    username = request.session.get('username', None)
    if username:
        sharedfiles = SharingFiles.objects.all()
        return render(request, 'tracksharedfiles.html', {'sharedfiles': sharedfiles})
    else:
        return redirect('adminlogin')
    

def view_share_files(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        print(file_id)
        try:
            sharefiles = SharingFiles.objects.get(file_id=file_id)
            return render (request, 'viewsharedfiles.html', {'sharefiles': sharefiles})
        except Users.DoesNotExist:
            pass

    return redirect('admindashboard')


def dashboard(request):
    for filename in os.listdir(settings.MEDIA_TEMP):
        file_path = os.path.join(settings.MEDIA_TEMP, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                continue
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    
    username = request.session.get('username', None)
    userid = request.session.get('userid', None)
    
    contents = os.listdir(settings.MEDIA_ROOT)

    folders = [item for item in contents if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
    
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
        
        request.session['current-section'] = 'MyDrive'

        return render(request, 'dashboardextend.html', {'username': username, 'uploaded_files': uploaded_files})
    else:
        return redirect('login')


def convert_size(size_bytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    divisor = 1024

    for suffix in suffixes:
        if size_bytes < divisor:
            return f"{size_bytes:.2f} {suffix}"
        size_bytes /= divisor

    return f"{size_bytes:.2f} {suffixes[-1]}"


def download_file(request):
    if request.method == 'POST':
        file_id = request.POST.get('itemid')
        
        file_details = FileDetails.objects.get(file_id=file_id)
        
        paths = file_details.get_paths()
        random.shuffle(paths)  # Shuffle the list of paths
        
        for file_path in paths:
            if os.path.exists(file_path):
                print(file_path)
                temp_path = os.path.join(settings.MEDIA_TEMP, file_details.filename + file_details.extension)
                
                encrypted_filepath = os.path.join(file_path, file_details.filename + file_details.extension)
                if os.path.exists(encrypted_filepath):
                    
                    decrypt_file(encrypted_filepath, temp_path, file_details.key)
                    
                    if os.path.exists(temp_path):
                        response = FileResponse(open(temp_path, 'rb'), content_type='application/force-download')
                        response['Content-Disposition'] = f'attachment; filename="{file_details.filename}{file_details.extension}"'
                        return response
                else:
                    continue  # Try the next path if decryption fails or file doesn't exist
        else:
            # If none of the paths were successful
            return redirect('dashboard')
    else:
        messages.error(request, f'Method not allowed.')
        return redirect('dashboard')


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
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        else:
                            pass
            
            file_details.delete()
            if share_details:
                share_details.delete()
            
            messages.success(request, 'File Deleted Successfully.')
            return redirect('dashboard')
            
        except FileDetails.DoesNotExist:
            return HttpResponse("File not found", status=404)
        except SharingFiles.DoesNotExist:
            return HttpResponse("Sharing information not found", status=404)
        
    else:
        return HttpResponse("Method not allowed", status=405)


def get_folder_contents(folder_path):
    contents = []
    for item_name in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item_name)
        is_dir = os.path.isdir(item_path)
        item_info = {'name': item_name, 'is_dir': is_dir}
        if is_dir:
            item_info['contents'] = get_folder_contents(item_path)
        item_info['full_path'] = item_path
        contents.append(item_info)
    return contents


def share_file(request):
    if request.method == 'POST':
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
                errors = "Account does not exist."
                return redirect('dashboard', {"errors": errors})
            
            messages.success(request, f'File shared with {email} successfully!')
        except FileDetails.DoesNotExist:
            messages.error(request, f'File with id {itemid} does not exist in the specified path!')
        except Users.DoesNotExist:
            messages.error(request, f'User with email {email} does not exist!')
            
        return redirect('dashboard')
    else:
        return redirect('dashboard')


def share_files_section(request):
    username = request.session.get('username', None)
    
    if username:
        fileuser = Users.objects.get(username=username)
        
        share_file_details = []

        shared_files = SharingFiles.objects.filter(share_to=fileuser.email)
        file_ids = [shared_file.file_id for shared_file in shared_files]
        file_details = FileDetails.objects.filter(file_id__in=file_ids)

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
                    
        request.session['current-section'] = 'SharedFiles'

        return render(request, 'sharedfiles.html', {'shared_files': share_file_details})
    else:
        return render(request, 'error.html', {'message': 'Username not found in session'})


def search(request):
    query = request.GET.get('query')
    username = request.session.get('username')
    userid = request.session.get('userid', None)
    
    fileuser = Users.objects.get(username=username)
    if query == "":
        return render(request, 'dashboardextend.html')
    
    current_section = request.session.get('current-section')
    
    if current_section == "MyDrive":
    
        files = FileDetails.objects.filter(Q(filename__icontains=query), user_id=userid).values('file_id', 'filename', 'size', 'extension', 'upload_date', 'path')
    
    else:
        files = []

        shared_files = SharingFiles.objects.filter(share_to=fileuser.email)
        file_ids = [shared_file.file_id for shared_file in shared_files]
        file_details = FileDetails.objects.filter(file_id__in=file_ids)

        for share in shared_files:
            for details in file_details:
                if details.file_id == share.file_id:
                    files.append({
                        'fileid': details.file_id,
                        'filename': share.filename,
                        'extension': share.extension,
                        'share_by': share.share_by,
                        'share_to': share.share_to,
                        'path': share.path,
                        'size': details.size,
                        'upload_date': details.upload_date
                    })
    
    return render(request, 'search_form.html', {
        'current_section': current_section,
        'search_results': files,
        'query': query,
        'username': username
    })


def is_folder_accessible_upload(folder_path):
    # Check if the folder exists
    path = os.path.join(settings.MEDIA_ROOT, folder_path)
    if not os.path.exists(path):
        return False
    
    try:
        _ = os.listdir(path)
        return True
    except Exception as e:
        print(f"Error accessing folder: {e}")
        return False


# def handle_file_upload(request):
#     if request.method == 'POST':
#         if 'file' in request.FILES:
#             uploaded_files = request.FILES.getlist('file')
            
#             username = request.session.get('username')
#             userid = request.session.get('userid', None)
            
#             if username:
#                 user = Users.objects.get(userid=userid)

#                 for uploaded_file in uploaded_files:
#                     try:
#                         contents = os.listdir(settings.MEDIA_ROOT)
                        
#                         newcontentlist = []
                        
#                         for folder in contents:
#                             if is_folder_accessible_upload(folder):
#                                 newcontentlist.append(folder)
                                
#                         folders = [item for item in newcontentlist if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
                        
#                         key = Fernet.generate_key()
                        
#                         size = len(folders)
#                         if size <= 3:
#                             distribute = size
#                         elif size == 3:
#                             distribute = 3
#                         else:
#                             distribute = int(size / 3) + 1
                        
#                         list_of_dir_copy = []
                        
#                         start_time = time.time()  # Start measuring time
                        
#                         for i in range(distribute):
#                             ran = random.choice(folders)
                            
#                             user_directory = os.path.join(settings.MEDIA_ROOT, ran, username)
                            
#                             if not os.path.exists(user_directory):
#                                 os.makedirs(user_directory, exist_ok=True)
                            
#                             list_of_dir_copy.append(user_directory)
#                             fs = FileSystemStorage(location=user_directory)
#                             fs.save(uploaded_file.name, uploaded_file)
                            
#                             input_file_path = os.path.join(user_directory, uploaded_file.name)
#                             output_file_path = os.path.join(user_directory, uploaded_file.name)
#                             encrypt_file(input_file_path, output_file_path, key)
#                             folders.remove(ran)
                            
#                         file_details = get_file_details(uploaded_file, list_of_dir_copy)
#                         save_file_details(user, file_details, key)
                        
#                         end_time = time.time()  # End measuring time
#                         upload_time = end_time - start_time  # Calculate total upload time
                        
#                         print(f"Total upload time: {upload_time} seconds")
                        
#                         messages.success(request, f'Upload File Successful.')
#                         return redirect('dashboard')
                    
#                     except Exception as e:
#                         return render(request, 'basedashboard.html', {'error': str(e)})
                    
#                 return redirect('dashboard')
#             else:
#                 return redirect('dashboard')
#     return redirect('dashboard')


#NEW FILE UPLOAD IN TEMP FOLDER 2 ------------------------

# def handle_file_upload(request):
#     if request.method == 'POST':
#         if 'file' in request.FILES:
#             uploaded_files = request.FILES.getlist('file')
            
#             username = request.session.get('username')
#             userid = request.session.get('userid', None)
            
#             if username:
#                 user = Users.objects.get(userid=userid)

#                 for uploaded_file in uploaded_files:
#                     try:
#                         contents = os.listdir(settings.MEDIA_ROOT)
                        
#                         newcontentlist = []
                        
#                         for folder in contents:
#                             if is_folder_accessible_upload(folder):
#                                 newcontentlist.append(folder)
                                
#                         folders = [item for item in newcontentlist if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
                        
#                         key = Fernet.generate_key()
                        
#                         size = len(folders)
#                         if size <= 3:
#                             distribute = size
#                         elif size == 3:
#                             distribute = 3
#                         else:
#                             distribute = int(size / 3) + 1
                        
#                         list_of_dir_copy = []
                        
#                         start_time = time.time()  # Start measuring time
                        
#                         fs = FileSystemStorage(location=settings.MEDIA_TEMP2)
#                         fs.save(uploaded_file.name, uploaded_file)
                        
#                         input_file_path = os.path.join(settings.MEDIA_TEMP2, uploaded_file.name)
#                         output_file_path = os.path.join(settings.MEDIA_TEMP2, uploaded_file.name)
#                         print(output_file_path)
#                         encrypt_file(input_file_path, output_file_path, key)
                        
#                         for i in range(distribute):
#                             ran = random.choice(folders)
                            
#                             user_directory = os.path.join(settings.MEDIA_ROOT, ran, username)
                            
#                             if not os.path.exists(user_directory):
#                                 os.makedirs(user_directory, exist_ok=True)
                            
#                             list_of_dir_copy.append(user_directory)
#                             fs = FileSystemStorage(location=user_directory)
#                             fs.save(uploaded_file.name, open(output_file_path, 'rb'))
                            
#                             folders.remove(ran)
                            
#                         file_details = get_file_details(uploaded_file, list_of_dir_copy)
#                         save_file_details(user, file_details, key)
                        
#                         os.remove(input_file_path)
                        
#                         end_time = time.time()  # End measuring time
#                         upload_time = end_time - start_time  # Calculate total upload time
                        
#                         print(f"Total upload time: {upload_time} seconds")
                        
#                         messages.success(request, f'Upload File Successful.')
#                         return redirect('dashboard')
                    
#                     except Exception as e:
#                         return render(request, 'basedashboard.html', {'error': str(e)})
                    
#                 return redirect('dashboard')
#             else:
#                 return redirect('dashboard')
#     return redirect('dashboard')


# NEW FILE UPLOAD WITH PARALLEL UPLOAD

def handle_file_upload(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_files = request.FILES.getlist('file')
            username = request.session.get('username')
            userid = request.session.get('userid', None)
            
            if username:
                user = Users.objects.get(userid=userid)
                contents = os.listdir(settings.MEDIA_ROOT)
                folders = [folder for folder in contents if is_folder_accessible_upload(folder)]
                
                def upload_file(uploaded_file):
                    try:
                        key = Fernet.generate_key()
                        size = len(folders)
                        if size <= 3:
                            distribute = size
                        elif size == 3:
                            distribute = 3
                        else:
                            distribute = int(size / 3) + 1
                        
                        # Temporary file storage
                        fs_temp = FileSystemStorage(location=settings.MEDIA_TEMP)
                        fs_temp.save(uploaded_file.name, uploaded_file)
                        input_file_path = os.path.join(settings.MEDIA_TEMP, uploaded_file.name)
                        output_file_path = os.path.join(settings.MEDIA_TEMP, uploaded_file.name)
                        encrypt_file(input_file_path, output_file_path, key)
                        
                        # Parallel upload to selected folders
                        list_of_dir_copy = []
                        with ThreadPoolExecutor() as executor:
                            for i in range(distribute):
                                ran = random.choice(folders)
                                user_directory = os.path.join(settings.MEDIA_ROOT, ran, username)
                                os.makedirs(user_directory, exist_ok=True)
                                list_of_dir_copy.append(user_directory)
                                executor.submit(upload_to_folder, user_directory, uploaded_file.name, output_file_path)
                                folders.remove(ran)
                        
                        # Record file details and save to the database
                        file_details = get_file_details(uploaded_file, list_of_dir_copy)
                        save_file_details(user, file_details, key)
                        
                        # Remove temporary file
                        os.remove(input_file_path)
                        
                    except Exception as e:
                        return str(e)

                start_time = time.time()  # Start measuring time
                with ThreadPoolExecutor() as executor:
                    for result in executor.map(upload_file, uploaded_files):
                        if result is not None:
                            return render(request, 'basedashboard.html', {'error': result})
                
                end_time = time.time()  # End measuring time
                upload_time = end_time - start_time  # Calculate total upload time
                print(f"Total upload time: {upload_time} seconds")
                messages.success(request, f'Upload File Successful.')
                return redirect('dashboard')
            
            else:
                return redirect('dashboard')
    
    return redirect('dashboard')

def upload_to_folder(user_directory, filename, file_path):
    fs = FileSystemStorage(location=user_directory)
    fs.save(filename, open(file_path, 'rb'))


def get_file_details(uploaded_file, file_path):

    file_name = uploaded_file.name
    file_name_without_extension = os.path.splitext(file_name)[0]
    file_size = uploaded_file.size
    file_extension = os.path.splitext(file_name)[-1]
    
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
        filename=file_details['filename'],
        extension=file_details['extension'],
        size=file_details['size'],
        upload_date=file_details['upload_date'],
        key=key
    )
    file_details_object.set_paths(file_details['path'])
    file_details_object.save()
    return file_details_object
    
    
def addaccount(request):
    if request.method == 'POST':
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password2')
        
        if fname == "" or lname == "" or uname == "" or email == "" or pass1 == "" or pass2 == "":
            errors = "Don't leave it blank."
            return render(request, 'signup2.html', {'errors': errors})
        
        # Check if the email matches the custom pattern
        if not re.match(r'^[a-zA-Z0-9._%+-]+@g\.batstate-u\.edu\.ph$', email):
            errors = "Please enter a valid email address in the format 'ict@g.batstate-u.edu.ph'."
            return render(request, 'signup2.html', {'errors': errors})

        if Users.objects.filter(username=uname).exists():
            errors = "Username already exists."
            return render(request, 'signup2.html', {'errors': errors})

        if Users.objects.filter(email=email).exists():
            errors = "Account already exists."
            return render(request, 'signup2.html', {'errors': errors})
        
        if pass1 != pass2:
            errors = "Your password is not the same !!"
            return render(request, 'signup2.html', {'errors': errors})
        
        else:
            hashed_password = make_password(pass1)
            my_user = Users(firstname=fname, lastname=lname, username=uname, email=email, password=hashed_password)
            my_user.save()
            
            contents = os.listdir(settings.MEDIA_ROOT)

            folders = [item for item in contents if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]

            for folder in folders:
                user_directory = os.path.join(settings.MEDIA_ROOT, folder, uname)
                os.makedirs(user_directory, exist_ok=True)
            message = "Account Successfully Added."
            return render(request, 'signup2.html', {'errors': message})
        
    else:
        return render(request, 'signup2.html')
    

def loginPage2(request):
    if request.method == 'POST':

        email = request.POST.get("email")
        pass1 = request.POST.get("password")
        
        try:
            user = Users.objects.get(email=email)
            
            if check_password(pass1, user.password):
                request.session['username'] = user.username
                request.session['userid'] = user.userid
                return redirect('dashboard')
            else:
                errors = "Username or Password is incorrect"
                return render(request, 'login2.html', {'errors': errors})
            
        except Users.DoesNotExist:
            errors = "User does not exist!!"
            return render(request, 'login2.html', {'errors': errors})
        
    else:
        return render(request, 'login2.html')

def logout(request):
    request.session.flush()
    return redirect('login2')