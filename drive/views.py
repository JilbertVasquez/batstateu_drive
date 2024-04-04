from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .models import Users
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import JsonResponse


# Create your views here.

def dashboard(request):
    username = request.session.get('username', None)
    user_upload_dir = os.path.join(settings.MEDIA_ROOT, username)
    uploaded_files = []

    if username:
        for file_name in os.listdir(user_upload_dir):
            file_path = os.path.join(user_upload_dir, file_name)
            is_dir = os.path.isdir(file_path)
            uploaded_files.append({'name': file_name, 'is_dir': is_dir, 'full_path': file_path})  # Add full_path
        return render(request, 'dashboardextend.html', {'username': username, 'uploaded_files': uploaded_files})
    else:
        return redirect('login')

    
# def download_file(request, file_name):
#     username = request.session.get('username', None)
#     file_path = os.path.join(settings.MEDIA_ROOT, username, file_name)
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as file:
#             response = HttpResponse(file.read(), content_type='application/force-download')
#             response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#             return response
#     else:
#         return HttpResponse("File not found", status=404)


# def download_file(request, file_name):
#     username = request.session.get('username', None)
#     current_directory = request.POST.get('current_directory')
#     file_path = os.path.join(settings.MEDIA_ROOT, username, current_directory, file_name)
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as file:
#             response = HttpResponse(file.read(), content_type='application/force-download')
#             response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#             return response
#     else:
#         return HttpResponse("File not found", status=404)


def download_file(request, file_name):
    username = request.session.get('username', None)
    current_directory = request.GET.get('current_directory', '')  # Use request.GET to get query parameters
    if username:
        file_path = os.path.join(settings.MEDIA_ROOT, username, current_directory, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/force-download')
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response
        else:
            return HttpResponse("File not found", status=404)
    else:
        return HttpResponse("User not authenticated", status=401)
    

import os
import shutil
from django.conf import settings
from django.http import HttpResponse, JsonResponse

def delete_item(request):
    if request.method == 'POST':
        username = request.session.get('username', None)
        item_path = request.POST.get('item_path')  # Get the full item path
        if username and item_path:
            if os.path.exists(item_path):
                try:
                    if os.path.isdir(item_path):
                        # Use shutil.rmtree for recursive deletion of folders and files
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)  # Delete file
                    # return JsonResponse({'success': True, 'message': 'Item deleted successfully'})
                    deleted_item_directory = os.path.dirname(item_path)
                    return redirect('view_folder', folder_path=deleted_item_directory)
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error deleting item: {str(e)}'})
            else:
                return HttpResponse("Item not found", status=404)
        else:
            return HttpResponse("Invalid request", status=400)
    else:
        return HttpResponse("Method not allowed", status=405)



# def view_folder(request, folder_name):
#     username = request.session.get('username', None)
#     folder_path = os.path.join(settings.MEDIA_ROOT, username, folder_name)
#     uploaded_items = []

#     # Check if the folder exists
#     if os.path.exists(folder_path) and os.path.isdir(folder_path):
#         # Iterate over items (files and subfolders) in the folder
#         for item_name in os.listdir(folder_path):
#             item_path = os.path.join(folder_path, item_name)
#             item_type = 'file' if os.path.isfile(item_path) else 'folder'
#             uploaded_items.append({'name': item_name, 'type': item_type})
#     else:
#         # Handle case where folder does not exist or is not a directory
#         return HttpResponse("Folder not found", status=404)

#     return render(request, 'dashboardextend.html', {'uploaded_files': uploaded_items, 'current_directory': folder_name})


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
        return render(request, 'dashboardextend.html', {'uploaded_files': uploaded_items, 'current_directory': folder_path, 'parent_directory': parent_directory})


# def rename_item(request):
#     if request.method == 'POST':
#         item_name = request.POST.get('item_name')
#         new_name = request.POST.get('new_name')
#         print(item_name, new_name)
#         # Add your renaming logic here, e.g., using filesystem operations
#         # After renaming, you may redirect to the current directory or any other appropriate page
#         return JsonResponse({'success': True})  # You can return any JSON response as needed
#     else:
#         return redirect('dashboard')  # Redirect to dashboard if accessed via GET request

# def rename_item(request):
#     if request.method == 'POST':
#         item_path = request.POST.get('item_path')
#         new_name = request.POST.get('new_name')
#         print(item_path, new_name)

#         # Perform renaming operation (replace this with your logic)
#         # For demonstration, we'll just return a success response
#         return JsonResponse({'success': True})
#     else:
#         # Handle GET request or invalid method
#         return JsonResponse({'success': False, 'error': 'Method not allowed'})


# def rename_item(request):
#     if request.method == 'POST':
#         item_path = request.POST.get('item_path')
#         new_name = request.POST.get('new_name')

#         # Perform renaming operation
#         try:
#             # Example renaming logic (replace this with your actual renaming code)
#             # For demonstration, we'll assume 'os.rename' function for renaming
#             import os
#             os.rename(item_path, os.path.join(os.path.dirname(item_path), new_name))
#             # Render the same page again (you can pass any necessary context)
#             return render(request, 'basedashboard.html', context={})
#         except Exception as e:
#             # Handle renaming errors
#             return JsonResponse({'success': False, 'error': str(e)})
#     else:
#         # Handle GET request or invalid method
#         return JsonResponse({'success': False, 'error': 'Method not allowed'})

def rename_file(request):
    if request.method == 'POST':
        item_path = request.POST.get('item_path')
        new_name = request.POST.get('new_name')
        current_dir = request.POST.get("current_directory")
        # print("HELLO WORLD", current_dir)

        try:
            # Rename the file
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

def rename_folder(request):
    if request.method == 'POST':
        item_path = request.POST.get('item_path')
        new_name = request.POST.get('new_name')
        current_dir = request.POST.get("current_directory")

        try:
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


    
# def handle_upload(request):
#     if request.method == 'POST' and request.FILES['file']:
#         uploaded_file = request.FILES['file']
#         print(uploaded_file)
#         fs = FileSystemStorage()
#         fs.save(uploaded_file.name, uploaded_file)
#         return redirect('dashboard')  # Assuming you have a URL named 'dashboard'
#     return render(request, 'dashboard.html')  # Render the same page if no file is uploaded or request method is not POST
    
    
    
# def handle_upload(request):
#     username = request.session.get('username', None)
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']
#         # Do something with the uploaded file, e.g., save it
#         with open('D:/uploadedfiles/' + username + "/" + uploaded_file.name, 'wb+') as destination:
#             for chunk in uploaded_file.chunks():
#                 destination.write(chunk)
#         return redirect('dashboard')  # Redirect after successful upload
#     else:
#         # Handle the case if no file is uploaded or request method is not POST
#         return render(request, 'dashboard.html')
    
    
    
# def handle_file_upload(request):
#     if request.method == 'POST':
#         # Check if files were uploaded
#         if 'file' in request.FILES:
#             uploaded_files = request.FILES.getlist('file')  # Get list of uploaded files
#             username = request.session.get('username', None)
#             if username:
#                 user_upload_dir = os.path.join(settings.MEDIA_ROOT, username)
#                 if not os.path.exists(user_upload_dir):
#                     os.makedirs(user_upload_dir)
#                 fs = FileSystemStorage(location=user_upload_dir)
#                 for uploaded_file in uploaded_files:
#                     fs.save(uploaded_file.name, uploaded_file)  # Save each uploaded file
#                 return redirect('dashboard')  # Redirect after successful upload
#             else:
#                 return redirect('login')  # Redirect to login if user is not authenticated
#     return render(request, 'dashboard.html')  # Render the same page if no file is uploaded or request method is not POST


from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponseRedirect

# def handle_file_upload(request):
#     if request.method == 'POST':
#         # Check if files were uploaded
#         if 'file' in request.FILES:
#             uploaded_files = request.FILES.getlist('file')  # Get list of uploaded files
#             username = request.session.get('username')
#             if username:
#                 user_upload_dir = os.path.join(settings.MEDIA_ROOT, username)
#                 if not os.path.exists(user_upload_dir):
#                     os.makedirs(user_upload_dir)
#                 fs = FileSystemStorage(location=user_upload_dir)
#                 for uploaded_file in uploaded_files:
#                     try:
#                         fs.save(uploaded_file.name, uploaded_file)  # Save each uploaded file
#                     except Exception as e:
#                         # Handle file upload error
#                         return render(request, 'upload_error.html', {'error': str(e)})
#                 return render(request, 'dashboard.html')   # Redirect to the current page to update file list
#             else:
#                 return render(request, 'dashboard.html')   # Redirect to login if user is not authenticated
#     return render(request, 'dashboard.html') 


# def handle_file_upload(request):
#     if request.method == 'POST':
#         # Check if files were uploaded
#         if 'file' in request.FILES:
#             uploaded_files = request.FILES.getlist('file')  # Get list of uploaded files
#             username = request.session.get('username')
#             if username:
#                 user_upload_dir = os.path.join(settings.MEDIA_ROOT, username)
#                 if not os.path.exists(user_upload_dir):
#                     os.makedirs(user_upload_dir)
#                 fs = FileSystemStorage(location=user_upload_dir)
#                 for uploaded_file in uploaded_files:
#                     try:
#                         fs.save(uploaded_file.name, uploaded_file)  # Save each uploaded file
#                     except Exception as e:
#                         # Handle file upload error
#                         return render(request, 'upload_error.html', {'error': str(e)})
#                 # Return the current page to update the file list
#                 return render(request, 'dashboard.html')
#             else:
#                 return render(request, 'dashboard.html')   # Redirect to login if user is not authenticated
#     return render(request, 'dashboard.html')


# latest working
# def handle_file_upload(request):
#     if request.method == 'POST':
#         # Check if files were uploaded
#         if 'file' in request.FILES:
#             uploaded_files = request.FILES.getlist('file')  # Get list of uploaded files
#             username = request.session.get('username')
#             if username:
#                 user_upload_dir = os.path.join(settings.MEDIA_ROOT, username)
#                 if not os.path.exists(user_upload_dir):
#                     os.makedirs(user_upload_dir)
#                 fs = FileSystemStorage(location=user_upload_dir)
#                 for uploaded_file in uploaded_files:
#                     try:
#                         fs.save(uploaded_file.name, uploaded_file)  # Save each uploaded file
#                     except Exception as e:
#                         # Handle file upload error
#                         return render(request, 'upload_error.html', {'error': str(e)})
#                 # Get the current directory path from the request
#                 current_directory = request.POST.get('current_directory', '')
#                 if current_directory:
#                     # Redirect to the view_folder page with the current directory path
#                     return redirect(reverse('view_folder', kwargs={'folder_path': current_directory}))
#                 else:
#                     # Redirect to the dashboard page if no current directory is available
#                     return redirect('dashboard')
#             else:
#                 return redirect('dashboard')   # Redirect to login if user is not authenticated
#     # Redirect to the dashboard page if the request method is not POST or no files were uploaded
#     return redirect('dashboard')


def handle_file_upload(request):
    if request.method == 'POST':
        # Check if files were uploaded
        if 'file' in request.FILES:
            uploaded_files = request.FILES.getlist('file')  # Get list of uploaded files
            
            username = request.session.get('username')
            current_directory = request.POST.get('current_directory', '')
            if username:
                # Get the User object for the logged-in user
                user = Users.objects.get(username=username)
                print(user)
                user_upload_dir = os.path.join(settings.MEDIA_ROOT, username, current_directory)
                if not os.path.exists(user_upload_dir):
                    os.makedirs(user_upload_dir)
                fs = FileSystemStorage(location=user_upload_dir)
                for uploaded_file in uploaded_files:
                    try:
                        file_details = get_file_details(uploaded_file, user_upload_dir)
                        fs.save(uploaded_file.name, uploaded_file)  # Save each uploaded file
                        save_file_details(user, file_details)
                    
                        if current_directory:
                            # Redirect back to the view_folder with the current directory path included
                            return redirect(reverse('view_folder', kwargs={'folder_path': current_directory}))
                        else:
                            # Redirect to dashboard if current_directory is empty
                            return redirect('dashboard')
                    
                    except Exception as e:
                        print(str(e))
                        # Handle file upload error
                        return render(request, 'dashboard.html', {'error': str(e)})
                    
                # Redirect to the current page to update file list
                return redirect('dashboard')
            else:
                return redirect('dashboard')   # Redirect to login if user is not authenticated
    return redirect('dashboard')


from django.utils import timezone

def get_file_details(uploaded_file, file_path):
    """
    Function to extract details of an uploaded file.
    Returns a dictionary containing the file's name, size, extension, and upload date.
    """
    file_name = uploaded_file.name
    file_name1 = os.path.splitext(file_name)[0]
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
        
    size_value = round(size_value, 2)
    upload_date = timezone.now().strftime('%Y-%d-%m')
    
    file_details = {
        'name': file_name1,
        'extension': file_extension,
        'size': size_value,
        'size_unit': size_unit,
        'upload_date': upload_date,
        'file_path': file_path,
    }
    
    print(file_details)
    
    return file_details


from .models import Users, FileDetails  # Import your custom Users and FileDetails models

def save_file_details(user, file_details):
    """
    Function to save file details into the database.
    """
    file_details_object = FileDetails.objects.create(
        user=user,  # Ensure you're passing an instance of your custom Users model here
        filename=file_details['name'],
        extension=file_details['extension'],
        size=file_details['size'],
        upload_date=file_details['upload_date'],
        path=file_details['file_path']
    )
    return file_details_object


def handle_folder_upload(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_folder = request.FILES['file']
            username = request.session.get('username', None)
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


        
        
    
# def handle_upload(request):
#     if request.method == 'POST' and request.FILES:
#         uploaded_files = request.FILES.getlist('file')
#         for uploaded_file in uploaded_files:
#             if hasattr(uploaded_file, 'chunks'):
#                 handle_directory_upload(uploaded_file)
#             else:
#                 handle_file_upload(uploaded_file)
#         return HttpResponse("Files uploaded successfully!")
#     else:
#         return HttpResponse("No files uploaded!")

# def handle_file_upload(uploaded_file):
#     destination_path = os.path.join('D:/uploadedfiles', uploaded_file.name)
#     with open(destination_path, 'wb+') as destination:
#         for chunk in uploaded_file.chunks():
#             destination.write(chunk)

# def handle_directory_upload(uploaded_directory):
#     destination_path = os.path.join(settings.BASE_DIR, 'uploadedfiles', uploaded_directory.name)
#     os.makedirs(destination_path, exist_ok=True)
#     for file_name, file_content in uploaded_directory.items():
#         with open(os.path.join(destination_path, file_name), 'wb+') as destination:
#             for chunk in file_content.chunks():
#                 destination.write(chunk)
    
# def handle_create_folder(request):
#     if request.method == 'POST':
#         # Get the current username from session
#         username = request.session.get('username', None)
        
#         # Get the folder name from the POST request
#         folder_name = request.POST.get('folder_name')
#         current_directory = request.POST.get('current_directory')

#         # Check if the current username and folder name are valid
#         if username and folder_name:
#             # Construct the full path to the new folder
#             new_folder_path = os.path.join(settings.MEDIA_ROOT, username, current_directory, folder_name)
            
#             try:
#                 # Create the new folder
#                 os.makedirs(new_folder_path, exist_ok=True)
#                 return JsonResponse({'success': True, 'message': f'Folder "{folder_name}" created successfully'})
#             except Exception as e:
#                 return JsonResponse({'success': False, 'message': f'Error creating folder: {str(e)}'})

#     # Return a JSON response indicating failure if request method is not POST or required data is missing
#     return JsonResponse({'success': False, 'message': 'Invalid request or missing data'})


# latest
# from django.urls import reverse

# def handle_create_folder(request):
#     if request.method == 'POST':
#         # Get the current username from session
#         username = request.session.get('username', None)
        
#         # Get the folder name and current directory from the POST request
#         folder_name = request.POST.get('folder_name')
#         current_directory = request.POST.get('current_directory')

#         # Check if the current username and folder name are valid
#         if username and folder_name:
#             # Construct the full path to the new folder
#             new_folder_path = os.path.join(settings.MEDIA_ROOT, username, current_directory, folder_name)
            
#             try:
#                 # Create the new folder
#                 os.makedirs(new_folder_path, exist_ok=True)
                
#                 # Check if current_directory is not empty
#                 if current_directory:
#                     # Redirect back to the view_folder with the current directory path included
#                     return redirect(reverse('view_folder', kwargs={'folder_path': current_directory}))
#                 else:
#                     # Redirect to dashboard if current_directory is empty
#                     return redirect('dashboard')
#             except Exception as e:
#                 # Handle any errors during folder creation
#                 return JsonResponse({'success': False, 'message': f'Error creating folder: {str(e)}'})
#     else:
#         # return JsonResponse({'success': False, 'message': 'Invalid request or missing data'})
#         return HttpResponse('Method not allowed', status=405)


from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
import os
from django.conf import settings

def handle_create_folder(request):
    if request.method == 'POST':
        # Get the current username from session
        username = request.session.get('username', None)
        
        # Get the folder name and current directory from the POST request
        folder_name = request.POST.get('folder_name')
        current_directory = request.POST.get('current_directory')

        # Check if the current username and folder name are valid
        if username and folder_name:
            # Construct the full path to the new folder
            new_folder_path = os.path.join(settings.MEDIA_ROOT, username, current_directory, folder_name)
            
            try:
                # Create the new folder
                os.makedirs(new_folder_path, exist_ok=True)
                
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
        
        print(fname, lname, uname, email, pass1, pass2)
        
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
            # return render(request, 'signup.html')
            # return HttpResponse("User has been created successfully!!")
            
            user_directory = os.path.join(settings.MEDIA_ROOT, uname)
            os.makedirs(user_directory, exist_ok=True)
            
            return redirect('login')
        
    else:
        return render(request, 'signup.html')

def loginPage(request):
    if request.method == 'POST':

        email = request.POST.get("email")
        pass1 = request.POST.get("password")
        # user = authenticate(request, email=email, password=pass1)
        # if user is not None:
        #     login(request, user)
        #     print(email, pass1)
        #     return redirect ('signup')
        # else:
        #     return HttpResponse("Username or Password is incorrect!!")
        
        try:
            user = Users.objects.get(email=email)
            if check_password(pass1, user.password):
                # Passwords match, user authenticated
                print(email, pass1)
                request.session['username'] = user.username  # Storing username in session
                return redirect('dashboard')
            else:
                print(email, pass1)
                return HttpResponse("Username or Password is incorrect")
        except Users.DoesNotExist:
            return HttpResponse("User does not exist!!")
                
        
    else:
        return render(request, 'login.html')

