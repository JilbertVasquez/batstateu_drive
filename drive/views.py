from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect
# from django.contrib.auth.models import User
from .models import Users
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
import os
from django.core.files.storage import FileSystemStorage
from django.contrib import messages


# Create your views here.

def dashboard(request):
    username = request.session.get('username', None)
    uploaded_files = os.listdir('D:/uploadedfiles/' + username)
    # uploaded_files = os.path
    # print(os.path())
    if username:
        # Pass the username to the template
        return render(request, 'dashboard.html', {'username': username, 'uploaded_files': uploaded_files})
    else:
        # Handle the case if user is not logged in
        return redirect('login')
    
def download_file(request, file_name):
    username = request.session.get('username', None)
    file_path = os.path.join('D:/uploadedfiles/' + username + "/", file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/force-download')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)
    
# def handle_upload(request):
#     if request.method == 'POST' and request.FILES['file']:
#         uploaded_file = request.FILES['file']
#         print(uploaded_file)
#         fs = FileSystemStorage()
#         fs.save(uploaded_file.name, uploaded_file)
#         return redirect('dashboard')  # Assuming you have a URL named 'dashboard'
#     return render(request, 'dashboard.html')  # Render the same page if no file is uploaded or request method is not POST
    
def handle_upload(request):
    username = request.session.get('username', None)
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # Do something with the uploaded file, e.g., save it
        with open('D:/uploadedfiles/' + username + "/" + uploaded_file.name, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return redirect('dashboard')  # Redirect after successful upload
    else:
        # Handle the case if no file is uploaded or request method is not POST
        return render(request, 'dashboard.html')
    
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
            
            user_directory = os.path.join('D:/uploadedfiles', uname)
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

