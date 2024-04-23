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
    
    folder1 = [item for item in os.listdir(os.path.join(settings.MEDIA_ROOT, folders[0], username)) if os.path.isdir(os.path.join(settings.MEDIA_ROOT, folders[0], username, item))]
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
        return render(request, 'dashboardextend.html', {'username': username, 'uploaded_files': uploaded_files, 'folders': folder1})
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
        userid = request.session.get('userid', None)
        
        
        file_id = request.POST.get('itemid')
        
        file_details = FileDetails.objects.get(file_id=file_id)
        retrieved_paths_list = file_details.get_paths()


        path_index = 0
        
        while True:
            file_path = file_details.get_paths()[path_index]
            
            if os.path.exists(file_path):
                print(file_path)
                temp_path = os.path.join(settings.MEDIA_TEMP, file_details.filename + file_details.extension)
                
                encrypted_filepath = os.path.join(file_path, file_details.filename + file_details.extension)
                if os.path.exists(file_path):

                    decrypt_file(encrypted_filepath, temp_path, file_details.key)
                    
                    if os.path.exists(temp_path):
                        
                        response = FileResponse(open(temp_path, 'rb'), content_type='application/force-download')
                        response['Content-Disposition'] = f'attachment; filename="{file_details.filename}{file_details.extension}"'
                        
                        return response
                    else:
                        path_index += 1
                        # return HttpResponse("Decrypted file not found", status=404)
                else:
                    path_index += 1
                
            else:
                path_index += 1
                # return HttpResponse("File not found", status=404)
    else:
        return HttpResponse("Method not allowed", status=405)


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
        item_path = request.POST.get('item_path')
        item_name = request.POST.get('item_name')
        if username and item_path:
            if os.path.exists(item_path):
                try:
                    os.remove(os.path.join(item_path))
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


def view_folder(request, folder_path):
    username = request.session.get('username', None)
    userid = request.session.get('userid', None)
    folder_path = os.path.join(settings.MEDIA_ROOT, username, folder_path)
    uploaded_items = []

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        uploaded_items = get_folder_contents(folder_path)
    else:
        return HttpResponse("Folder not found", status=404)

    for item in uploaded_items:
        item['full_path'] = os.path.join(folder_path, item['name'])
        
    parent_directory = os.path.dirname(folder_path)
    if parent_directory == settings.MEDIA_ROOT:
        return redirect('dashboard')
    else:
        return render(request, 'dashboardextend.html', {'uploaded_files': uploaded_items, 'current_directory': folder_path, 'parent_directory': parent_directory, 'username': username})


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
        except FileDetails.DoesNotExist:
            messages.error(request, f'File with id {itemid} does not exist in the specified path!')
        except Users.DoesNotExist:
            messages.error(request, f'User with email {email} does not exist!')
            

        return redirect('dashboard')
    else:
        pass


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

        return render(request, 'sharedfiles.html', {'shared_files': share_file_details})
    else:
        return render(request, 'error.html', {'message': 'Username not found in session'})


def search(request):
    query = request.GET.get('query')
    username = request.session.get('username')
    userid = request.session.get('userid', None)
    
    if query == "":
        return render(request, 'dashboardextend.html')
    
    files = FileDetails.objects.filter(Q(filename__icontains=query), user_id=userid).values('file_id', 'filename', 'size', 'extension', 'upload_date', 'path')
    
    return render(request, 'search_form.html', {
        'search_results': files,
        'query': query,
        'username': username
    })


def rename_file(request):
    if request.method == 'POST':
        username = request.session.get('username')  
        item_path = request.POST.get('item_path')

        last_name = request.POST.get('lastname')
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
        try:
            os.rename(item_path, os.path.join(os.path.dirname(item_path), new_name))
            
            user = Users.objects.get(username=username)
            userid = user.userid
            useremail = user.email
            
            file_detail = FileDetails.objects.get(filename=last_name2, extension=last_name3 ,path=current_dir, user_id=userid)
            file_detail.filename = new_name2
            file_detail.extension = new_name3
            file_detail.save()
            
            shared_files = SharingFiles.objects.filter(share_by=useremail, filename=last_name2, extension=last_name3, path=current_dir)
            for shared_file in shared_files:
                shared_file.filename = new_name2
                shared_file.extension = new_name3
                shared_file.save()

            if current_dir == "":
                return redirect("dashboard")
            else:
                return redirect('view_folder', folder_path=current_dir)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
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
            
            os.rename(item_path, os.path.join(os.path.dirname(item_path), new_name))
            if current_dir == "":
                return redirect("dashboard")
            else:
                return redirect('view_folder', folder_path=current_dir)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'})





def is_folder_accessible_upload(folder_path):
    # Check if the folder exists
    path = os.path.join(settings.MEDIA_ROOT, folder_path)
    if not os.path.exists(path):
        # print("NOOOOOO", path)
        return False
    
    try:
        _ = os.listdir(path)
        # print("YESSSSS", path)
        return True
    except Exception as e:
        print(f"Error accessing folder: {e}")
        return False


def handle_file_upload(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_files = request.FILES.getlist('file')
            
            username = request.session.get('username')
            userid = request.session.get('userid', None)
            current_directory = request.POST.get('current_directory', '')
            
            if username:
                user = Users.objects.get(userid=userid)

                for uploaded_file in uploaded_files:
                    try:
                        contents = os.listdir(settings.MEDIA_ROOT)
                        
                        newcontentlist = []
                        
                        for folder in contents:
                            if is_folder_accessible_upload(folder):
                                newcontentlist.append(folder)
                                
                        
                        folders = [item for item in newcontentlist if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
                        
                        newfolderlist = []
                        
                        key = Fernet.generate_key()
                        
                        size = len(folders)
                        if size <= 3:
                            distribute = size
                        elif size == 3:
                            distribute = 3
                        else:
                            distribute = int(size / 3) + 1
                        
                        
                        list_of_dir_copy = []
                        
                        for i in range(distribute):
                            ran = random.choice(folders)
                            
                            user_directory = os.path.join(settings.MEDIA_ROOT, ran, username)
                            
                            list_of_dir_copy.append(user_directory)
                            fs = FileSystemStorage(location=user_directory)
                            fs.save(uploaded_file.name, uploaded_file)
                            
                            input_file_path = os.path.join(user_directory, uploaded_file.name)
                            output_file_path = os.path.join(user_directory, uploaded_file.name)
                            encrypt_file(input_file_path, output_file_path, key)
                            folders.remove(ran)
                            
                        file_details = get_file_details(uploaded_file, list_of_dir_copy)
                        save_file_details(user, file_details, key)
                        return redirect('dashboard')
                    
                    except Exception as e:
                        return render(request, 'basedashboard.html', {'error': str(e)})
                    
                return redirect('dashboard')
            else:
                return redirect('dashboard')
    return redirect('dashboard')




# def is_folder_accessible(folder_path):
#     # Check if the folder exists
#     if not os.path.exists(folder_path):
#         return False
    
#     # Check network accessibility by attempting to access a file within the folder
#     try:
#         return True
#     except Exception as e:
#         print(f"Error accessing folder: {e}")
#         return False


# def handle_file_upload(request):
#     if request.method == 'POST':
#         if 'file' in request.FILES:
#             uploaded_files = request.FILES.getlist('file')
            
#             username = request.session.get('username')
#             userid = request.session.get('userid', None)
#             current_directory = request.POST.get('current_directory', '')
            
#             if username:
#                 user = Users.objects.get(userid=userid)

#                 for uploaded_file in uploaded_files:
#                     try:
#                         contents = os.listdir(settings.MEDIA_ROOT)
#                         folders = [item for item in contents if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]
                        
                        
                        
#                         list_of_dir_copy = []
#                         key = Fernet.generate_key()
#                         for folder in folders:
#                             user_directory = os.path.join(settings.MEDIA_ROOT, folder, username)
#                             list_of_dir_copy.append(user_directory)
#                             fs = FileSystemStorage(location=user_directory)
#                             fs.save(uploaded_file.name, uploaded_file)
                            
#                             input_file_path = os.path.join(user_directory, uploaded_file.name)
#                             output_file_path = os.path.join(user_directory, uploaded_file.name)
#                             encrypt_file(input_file_path, output_file_path, key)
                            
#                         file_details = get_file_details(uploaded_file, list_of_dir_copy)
#                         save_file_details(user, file_details, key)
                        
#                         return redirect('dashboard')
                    
#                     except Exception as e:
#                         return render(request, 'basedashboard.html', {'error': str(e)})
                    
#                 return redirect('dashboard')
#             else:
#                 return redirect('dashboard')
#     return redirect('dashboard')


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

                folder_name = uploaded_folder.name

                directory_path = os.path.join(user_upload_dir, folder_name)
                os.makedirs(directory_path, exist_ok=True)

                for uploaded_file in uploaded_folder:
                    fs = FileSystemStorage(location=directory_path)
                    fs.save(uploaded_file.name, uploaded_file)
                
                return redirect('dashboard') 
            else:
                return redirect('login')
    return render(request, 'basedashboard.html')


def handle_create_folder(request):
    if request.method == 'POST':
        username = request.session.get('username', None)
        userid = request.session.get('userid', None)

        folder_name = request.POST.get('folder_name')
        current_directory = request.POST.get('current_directory')
        
        if username and folder_name:
            try:
                contents = os.listdir(settings.MEDIA_ROOT)

                folders = [item for item in contents if os.path.isdir(os.path.join(settings.MEDIA_ROOT, item))]

                for folder in folders:
                    user_directory = os.path.join(settings.MEDIA_ROOT, folder, username, folder_name )
                    os.makedirs(user_directory, exist_ok=True)

                if current_directory:
                    return redirect(reverse('view_folder', kwargs={'folder_path': current_directory}))
                else:
                    return redirect('dashboard')
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error creating folder: {str(e)}'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request or missing data'})
    else:
        return HttpResponse('Method not allowed', status=405)


def signupPage(request):
    if request.method == 'POST':
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password2')

        if Users.objects.filter(username=uname).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup.html', {'messages': messages})

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
                request.session['username'] = user.username
                request.session['userid'] = user.userid
                return redirect('dashboard')
            else:
                return HttpResponse("Username or Password is incorrect")
            
        except Users.DoesNotExist:
            return HttpResponse("User does not exist!!")
        
    else:
        return render(request, 'login.html')
    

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
                return HttpResponse("Username or Password is incorrect")
            
        except Users.DoesNotExist:
            return HttpResponse("User does not exist!!")
        
    else:
        return render(request, 'login2.html')

def logout(request):
    request.session.flush()
    return redirect('login')