from django.shortcuts import render,redirect
from django.views import View
from instructorApp.forms import InstructorCreateForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from instructorApp.models import Course,Cart,Order,Module,Lesson
from django.db.models import Sum
import razorpay
# Create your views here.

RZP_KEY_ID="rzp_test_tapimqsLV8XzBE"
RZP_KEY_SECRET="70mIJHlipzSxvPIbjB1L2Js5"

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

            if total>0:
                client=razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))
                print(client)
                DATA={"amount":int(total),"currency":"INR","receipt":"rzp_receipt_1"}
                payment=client.order.create(data=DATA)
                print(payment)
                rzp_order_id=payment.get("id")
                order_instance.rz_order_id=rzp_order_id
                order_instance.save()
                context={
                    "rzp_key_id":RZP_KEY_ID,
                    "amount":int(total),
                    "rzp_order_id":rzp_order_id
                }

                return render(request,'payment.html',context)

            return redirect('student_home')
        
class MyCourses(View):
    def get(self,request,*args,**kwargs):
        # my_orders=request.user.student_orders.all()
        my_orders=Order.objects.filter(student=request.user)
        return render(request,'student_courses_list.html',{'orders':my_orders})
    

# http://127.0.0.1:8000/student/courses/1/watch?module=1&lesson=2
# ? optional parameter values

class LessonView(View):
    def get(self,request,*args,**kwargs):
        course_id=kwargs.get("course_id")
        course_instance=Course.objects.get(id=course_id)
        print(course_instance.modules.all().first().id,"+++++++++++++++")
        module_id=request.GET.get("module") if "module" in request.GET else course_instance.modules.all().first().id
        module_instance=Module.objects.get(id=module_id,course_instance=course_instance)
        print(module_instance.lesson.all().first().id)
        lesson_id=request.GET.get("lesson") if "lesson" in request.GET else module_instance.lesson.all().first().id
        lesson_instance=Lesson.objects.get(id=lesson_id,module_instance=module_instance)
        print(module_instance,"++++++++++")
        print(lesson_instance,"++++++++++")

        return render(request,'lesson_list.html',{"course":course_instance,"lesson":lesson_instance})

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt,name="dispatch")
class PaymentConfirmation(View):
    def post(self,request,*args,**kwargs):
        print(request.POST)
        import razorpay
        client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(request.POST)
            print(request.POST)
            order_id=request.POST.get("razorpay_order_id")
            order_instance=Order.objects.get(rz_order_id=order_id)
            order_instance.is_paid=True
            order_instance.save()
            print("payment success")
        except:
            print("pyment failed")
        return redirect("student_home")

