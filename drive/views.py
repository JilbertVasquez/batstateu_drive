from django.shortcuts import render, HttpResponse
# from django.contrib.auth.models import User
from .models import Users, FileDetails
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


# Create your views here.

def dashboard(request):
    username = request.session.get('username', None)
    user_upload_dir = os.path.join(settings.MEDIA_ROOT, username)
    uploaded_files = []

    if username:
        for file_name in os.listdir(user_upload_dir):
            file_path = os.path.join(user_upload_dir, file_name)
            is_dir = os.path.isdir(file_path)
            
            # Get file size and last modified date
            file_size = os.path.getsize(file_path)
            size_label = str(convert_size(file_size))
            last_modified = os.path.getmtime(file_path)
            last_modified_date = time.strftime('%m-%d-%Y', time.localtime(last_modified))

            uploaded_files.append({
                'name': file_name,
                'size': size_label,
                'date': last_modified_date,
                'is_dir': is_dir,
                'full_path': file_path
            })
            print(uploaded_files[0])
            
            # uploaded_files.append({'name': file_name, 'size': file_size, 'last_modified': last_modified_date, 'is_dir': is_dir, 'full_path': file_path})  # Add full_path
            # print(uploaded_files[0])
        return render(request, 'dashboardextend.html', {'username': username, 'uploaded_files': uploaded_files})
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


def delete_item(request):
    if request.method == 'POST':
        username = request.session.get('username', None)
        item_name = request.POST.get('item_name')
        item_path = request.POST.get('item_path')  # Get the full item path
        if username and item_path:
            if os.path.exists(item_path):
                try:
                    if os.path.isdir(item_path):
                        # Use shutil.rmtree for recursive deletion of folders and files
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)  # Delete file
                        
                    # file_detail = FileDetails.objects.get(path=item_path)
                    # file_detail.delete()
                    # print(file_detail)
                    
                    # return JsonResponse({'success': True, 'message': 'Item deleted successfully'})
                    deleted_item_directory = os.path.dirname(item_path)
                    return redirect('view_folder', folder_path=deleted_item_directory)
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error deleting item: {str(e)}'})
            else:
                return HttpResponse("Item not found", status=404)
        else:
            # print(item_path)
            return HttpResponse("Invalid request", status=400)
    else:
        return HttpResponse("Method not allowed", status=405)

def delete_item_search(request):
    if request.method == 'POST':
        username = request.session.get('username', None)
        item_path = request.POST.get('item_path')  # Get the full item path
        item_name = request.POST.get('item_name')
        if username and item_path:
            if os.path.exists(item_path):
                try:
                    # print(os.path.join(item_path, item_name))
                    # print(os.path.dirname(item_path))
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
            print(item_path)
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
    
    # print(search_results)
    
    for filenames_details in search_results:
        # print(filenames_details.filename)
        # print(filenames_details.size)
        # print(filenames_details.extension)
        pass
    
    return render(request, 'search_form.html', {
        'search_results': search_results,
        'current_directory': current_directory,
        'query': query,  # Pass the query back to the template for displaying in the search input field
        'username': username
    })
    
'''

def search(request):
    query = request.GET.get('query')
    username = request.session.get('username')
    current_directory = request.GET.get('current_directory')
    
    if current_directory == "":
        current_directory = os.path.join(settings.MEDIA_ROOT, username)
    
    retrieved_files = []

    if query == "":
        return render(request, 'dashboardextend.html')
    
    search_results = []

    for root, dirs, files in os.walk(current_directory):
        for file_name in files:
            if query.lower() in file_name.lower():
                if current_directory == "":
                    file_path = current_directory
                else:
                    file_path = os.path.join(root, file_name)
                print("ADSAD---------",file_path)
                file_size = os.path.getsize(file_path)
                file_size_formatted = get_formatted_file_size(file_size)
                search_results.append({'filename': file_name, 'size': file_size_formatted, 'path': file_path})
    
    return render(request, 'search_form.html', {
        'search_results': search_results,
        'current_directory': current_directory,
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
                # print(user)
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
                        # print(str(e))
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
    
    # print(file_details)
    
    return file_details


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
        
        # print(fname, lname, uname, email, pass1, pass2)
        
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
            
            user_directory = os.path.join(settings.MEDIA_ROOT, uname)
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
                # print(email, pass1)
                request.session['username'] = user.username  # Storing username in session
                return redirect('dashboard')
            else:
                # print(email, pass1)
                return HttpResponse("Username or Password is incorrect")
            
        except Users.DoesNotExist:
            return HttpResponse("User does not exist!!")
        
    else:
        return render(request, 'login.html')

