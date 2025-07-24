from django.urls import path
from studentApp import views

urlpatterns=[
    path('student/register',views.StudentRegisterView.as_view(),name="student_register"),
    path('student/login',views.StudentLoginView.as_view(),name="student_login"),
    path('student/home',views.StudentHome.as_view(),name="student_home"),
    path('student/course/detail/<int:id>',views.CourseDetail.as_view(),name="course_detail"),
    path('student/course/cart/<int:id>',views.AddToCart.as_view(),name="addtocart_view"),
    path('student/cart/summary',views.CartSummary.as_view(),name="cartsummary_view"),
    path('student/cart/delete/<int:id>',views.CartDelete.as_view(),name="cartdelete_view"),
]