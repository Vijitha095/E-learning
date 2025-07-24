from django.urls import path
from instructorApp import views

urlpatterns=[
    path('instructor/register',views.InstructorCreateView.as_view(),name="instructor_create")
]