from django.contrib import admin
from .models import Form, FormQuestion, FormAnswer, ContentChoice, Comment, Person

admin.site.register(Form)
admin.site.register(FormQuestion)
admin.site.register(FormAnswer)
admin.site.register(ContentChoice)
admin.site.register(Person)
