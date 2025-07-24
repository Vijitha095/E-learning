from django.contrib import admin
from instructorApp.models import User,Category,Course,Module,Lesson


# Register your models here.
admin.site.register(User)
admin.site.register(Category)

class ChangeCourseModel(admin.ModelAdmin):
    exclude=('owner',)
    def save_model(self, request, obj, form, change):

        if not change:
            obj.owner=request.user
        return super().save_model(request, obj, form, change)

admin.site.register(Course,ChangeCourseModel)

class ChangeModule(admin.ModelAdmin):
    exclude=('order',)

admin.site.register(Module,ChangeModule)

class ChangeLesson(admin.ModelAdmin):
    exclude=("order",)
    
admin.site.register(Lesson,ChangeLesson)