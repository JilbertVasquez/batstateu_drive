from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect
# from django.contrib.auth.models import User
from .models import Users
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password

# Create your views here.

def dashboard(request):
    return render(request, 'dashboard.html')

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
                return redirect('dashboard')
            else:
                print(email, pass1)
                return HttpResponse("Username or Password is incorrect")
        except Users.DoesNotExist:
            return HttpResponse("User does not exist!!")
                
        
    else:
        return render(request, 'login.html')

