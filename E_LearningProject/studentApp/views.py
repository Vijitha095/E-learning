from django.shortcuts import render,redirect
from django.views import View
from instructorApp.forms import InstructorCreateForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from instructorApp.models import Course,Cart
# Create your views here.

class StudentRegisterView(View):
    def get(self,request):
        form=InstructorCreateForm()
        return render(request,'student_register.html',{'form':form})
    
    def post(self,request):
        form=InstructorCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_login')
        else:
            return render(request,'student_register.html',{'form':form})
        
class StudentLoginView(View):
    def get(self,request):
        return render(request,'student_login.html')
    
    def post(self,request):
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(request,username=username,password=password)
        if user:
            if user.role=="student":
                login(request,user)
                return redirect("student_home")
        else:
            messages.warning(request,"Invalid username or password")
            return redirect("student_login")
    

class StudentHome(View):
    def get(self,request):
        course_instances=Course.objects.all()
        return render(request,'student_home.html',{'courses':course_instances})
    

class CourseDetail(View):
    def get(self,request,**kwargs):
        course=Course.objects.get(id=kwargs.get("id"))
        return render(request,"student_course_detail.html",{"course":course})
    
class AddToCart(View):
    def get(self,request,*args,**kwargs):
        course_instance=Course.objects.get(id=kwargs.get("id"))
        user_instance=request.user
        # Cart.objects.create(course_instance=course_instance,user_instance=user_instance)
        cart_instance,created=Cart.objects.get_or_create(course_instance=course_instance,user_instance=user_instance)
        print(cart_instance,created)
        return redirect("student_home")
    
class CartSummary(View):
    def get(self,request):
        # cart_items=Cart.objects.filter(user_instance=request.user)
        cart_items=request.user.cart_user.all()
        return render(request,'student_cart_summary.html',{'cart_items':cart_items})
    

class CartDelete(View):
    def get(self,request,*args,**kwargs):
        Cart.objects.get(id=kwargs.get("id")).delete()
        return redirect("cartsummary_view")
    
    