from django.shortcuts import render,redirect
from django.views import View
from instructorApp.forms import InstructorCreateForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from instructorApp.models import Course,Cart,Order,Module,Lesson
from django.db.models import Sum
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
        purchased_courses=Order.objects.filter(student=request.user).values_list("course_objects",flat=True)  # [1,2,3]
        print(purchased_courses,"===================")
        return render(request,'student_home.html',{'courses':course_instances,'purchased_courses':purchased_courses})
    

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
        cart_items=request.user.cart_user.all()  # [cartobject1,cartobj1]
        total_price=cart_items.values("course_instance__price").aggregate(total=Sum("course_instance__price")).get("total") #{'total':1000}
        return render(request,'student_cart_summary.html',{'cart_items':cart_items,'total_price':total_price})
    

class CartDelete(View):
    def get(self,request,*args,**kwargs):
        Cart.objects.get(id=kwargs.get("id")).delete()
        return redirect("cartsummary_view")
    

class CheckOutView(View):
    def get(self,request,*args,**kwargs):
        cart_list=request.user.cart_user.all() #[cartobj,obj1]
        total=sum([cart.course_instance.price for cart in cart_list])  #[500,300]
        order_instance=Order.objects.create(student=request.user,total=total)
        if cart_list:
            for ci in cart_list:
                order_instance.course_objects.add(ci.course_instance)
                ci.delete()
            order_instance.save()
            return redirect('student_home')
        
class MyCourses(View):
    def get(self,request,*args,**kwargs):
        # my_orders=request.user.student_orders.all()
        my_orders=Order.objects.filter(student=request.user)
        return render(request,'student_courses_list.html',{'orders':my_orders})
    

# http://127.0.0.1:8000/student/courses/1/watch?module=1&lesson=1
# ? optional parameter values

class LessonView(View):
    def get(self,request,*args,**kwargs):
        course_id=kwargs.get("course_id")
        course_instance=Course.objects.get(id=course_id)
        if "module" in request.GET:
            module_id=request.GET.get("module")
        if "lesson" in request.GET:
            lesson_id=request.GET.get("lesson")
        module_instance=Module.objects.get(id=module_id)
        lesson_instance=Lesson.objects.get(id=lesson_id)