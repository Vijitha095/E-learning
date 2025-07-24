from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import signals
from embed_video.fields import EmbedVideoField
from django.db.models import Max

# Create your models here.
class User(AbstractUser):
    options=(
        ('student','student'),
        ('instructor','instructor')
    )
    role=models.CharField(max_length=100,choices=options,default="student")


class InstructorProfile(models.Model):
    owner=models.OneToOneField(User,on_delete=models.CASCADE,related_name='instructor')
    image=models.ImageField(upload_to='profilepicture',default="profilepicture/default.png",null=True,blank=True)
    expertise=models.CharField(max_length=100,null=True,blank=True)
    description=models.TextField(null=True,blank=True)

def create_instructor_profile(sender,instance,created,**kwargs):
    print("function executed")
    if created and instance.role=="instructor":
        print("profile added")
        InstructorProfile.objects.create(owner=instance)

signals.post_save.connect(create_instructor_profile,User)


class Category(models.Model):
    name=models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name
    

class Course(models.Model):
    owner=models.ForeignKey(User,on_delete=models.SET_NULL,
                            null=True,related_name="courses")
    category_instance=models.ManyToManyField(Category,related_name='category')
    title=models.CharField(max_length=100)
    description=models.TextField()
    price=models.DecimalField(max_digits=5,decimal_places=2)
    is_free=models.BooleanField(default=False)
    image=models.ImageField(upload_to="courseimages",
                            null=True,blank=True,default="courseimages/default.png")
    thumbnail=EmbedVideoField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Module(models.Model):
    title=models.CharField(max_length=100)
    course_instance=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='modules')
    order=models.PositiveIntegerField()

    def save(self,*args,**kwargs):
        module_count=Module.objects.filter(course_instance=self.course_instance).aggregate(max=Max("order")).get("max") or 0 # {'max':2}
        self.order=module_count+1
        super().save(*args,**kwargs)

    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    title=models.CharField(max_length=100)
    module_instance=models.ForeignKey(Module,on_delete=models.CASCADE,related_name="lesson")
    order=models.PositiveIntegerField()
    video=EmbedVideoField()

    def save(self,*args,**kwargs):
        lesson_count=Lesson.objects.filter(module_instance=self.module_instance).aggregate(max=Max('order')).get("max") or 0
        self.order=lesson_count+1
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.module_instance.title}+{self.title}"
    

class Cart(models.Model):
    user_instance=models.ForeignKey(User,on_delete=models.CASCADE,related_name="cart_user")
    course_instance=models.ForeignKey(Course,on_delete=models.CASCADE,related_name="user_course")
    added_date=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.course_instance.title
    








# python django -Course
# 1.python fundamentals
# 2.core python
# 3.
# 4.ghj
