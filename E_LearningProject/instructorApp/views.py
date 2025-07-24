from django.shortcuts import render,redirect
from django.views import View
from instructorApp.models import User,InstructorProfile
from instructorApp.forms import InstructorCreateForm
from django.http import HttpResponse

# Create your views here.

class InstructorCreateView(View):
    def get(self,request,*args,**kwargs):
        form=InstructorCreateForm()
        return render(request,'instructor_register.html',{'form':form})
    
    def post(self,request,*args,**kwargs):
        form_instance=InstructorCreateForm(request.POST)
        if form_instance.is_valid():
            form_instance.instance.role="instructor"
            form_instance.instance.is_superuser=True
            form_instance.instance.is_staff=True
            form_instance.save()
            return HttpResponse("user added")
        else:
            return redirect('instructor_create')