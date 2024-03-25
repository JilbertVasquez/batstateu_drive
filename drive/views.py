from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect
# from django.contrib.auth.models import User
from .models import Users
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
import os
from django.conf import settings


# Create your views here.

def dashboard(request):
    username = request.session.get('username', None)
    uploaded_files = os.listdir('D:/uploadedfiles')
    if username:
        # Pass the username to the template
        return render(request, 'dashboard.html', {'username': username, 'uploaded_files': uploaded_files})
    else:
        # Handle the case if user is not logged in
        return redirect('login')
    
def handle_upload(request):
    if request.method == 'POST' and request.FILES:
        uploaded_files = request.FILES.getlist('file')
        for uploaded_file in uploaded_files:
            if hasattr(uploaded_file, 'chunks'):
                handle_directory_upload(uploaded_file)
            else:
                handle_file_upload(uploaded_file)
        return HttpResponse("Files uploaded successfully!")
    else:
        return HttpResponse("No files uploaded!")

def handle_file_upload(uploaded_file):
    destination_path = os.path.join('uploadedfiles', uploaded_file.name)
    with open(destination_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

def handle_directory_upload(uploaded_directory):
    destination_path = os.path.join(settings.BASE_DIR, 'uploadedfiles', uploaded_directory.name)
    os.makedirs(destination_path, exist_ok=True)
    for file_name, file_content in uploaded_directory.items():
        with open(os.path.join(destination_path, file_name), 'wb+') as destination:
            for chunk in file_content.chunks():
                destination.write(chunk)

def create_folder(request):
    folder_name = request.POST.get('folder_name')
    if folder_name:
        folder_path = os.path.join(settings.BASE_DIR, 'uploadedfiles', folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return HttpResponse("Folder created successfully!")
    else:
        return HttpResponse("Folder name not provided!")
    


def signupPage(request):
    if request.method == 'POST':
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password2')
        
        print(fname, lname, uname, email, pass1, pass2)
        
        if pass1 != pass2:
            return HttpResponse("Your password is not the same !!")
        else:
            hashed_password = make_password(pass1)
            my_user = Users(firstname=fname, lastname=lname, username=uname, email=email, password=hashed_password)
            my_user.save()
            # return render(request, 'signup.html')
            # return HttpResponse("User has been created successfully!!")
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

