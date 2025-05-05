from django.contrib import admin
from .models import Questions
from django_summernote.widgets import SummernoteWidget
from django.db import models

class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': SummernoteWidget},
    }

admin.site.register(Questions, QuestionAdmin) 