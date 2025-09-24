from django.contrib import admin


from business.models import Entity, Task

class EntityAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]

class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "description"]

admin.site.register(Entity, EntityAdmin)

admin.site.register(Task, TaskAdmin)
