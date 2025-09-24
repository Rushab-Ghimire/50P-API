from django.contrib import admin


from card.models import ContextCard

class ContextCardAdmin(admin.ModelAdmin):
    list_display = ["title", "context"]


admin.site.register(ContextCard, ContextCardAdmin)
