from django.db import models
from django.contrib.auth.models import User


class Form(models.Model):
    type = models.CharField(max_length=100)    # either SEAF or RAF
    date = models.DateTimeField('date published')
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    is_main = models.BooleanField()    # Only 2 forms have this
    is_started = models.BooleanField()
    is_finished = models.BooleanField()    # About the lab study
    is_completed = models.BooleanField()    # About the form itself (confirmed by the lab assistant 1 more time)

    approved_labassist = models.BooleanField()    # for SEAF
    approved_teacher = models.BooleanField()  # for SEAF
    approved_director = models.BooleanField()  # both SEAF and RAF
    approved_safety = models.BooleanField()  # for RAF

    def __str__(self):
        return str(self.is_main) + " " + self.type + ", " + self.person.first_name + " " + self.person.last_name +\
               ", " + str(self.date)


class FormInfo(models.Model):
    type = models.CharField(max_length=100)  # either SEAF or RAF
    date_created = models.DateTimeField('date published')
    date_lab = models.DateTimeField()
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000)


class FormQuestion(models.Model):
    order = models.IntegerField()
    form = models.ForeignKey("Form", on_delete=models.CASCADE)
    question = models.TextField(max_length=1000)
    tooltip = models.TextField(max_length=1000)
    is_choice = models.BooleanField()
    is_text = models.BooleanField()
    is_necessary = models.BooleanField()

    def __str__(self):
        return self.question


class FormAnswer(models.Model):
    question = models.ForeignKey("FormQuestion", on_delete=models.CASCADE)
    value = models.TextField(max_length=1000)

    def __str__(self):
        return self.value


class ContentChoice(models.Model):
    text = models.CharField(max_length=2000)
    question = models.ForeignKey("FormQuestion", on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField(max_length=2000)
    form = models.ForeignKey("Form", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=100)    # either Student, Teacher, LabAssist, Safety, Inspector or Director
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    approved = models.BooleanField()
    temp_password = models.BooleanField()    # means that the password ISN'T temporary

    def __str__(self):
        return self.first_name + " " + self.last_name
