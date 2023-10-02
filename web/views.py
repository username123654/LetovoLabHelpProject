from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.views.decorators.clickjacking import xframe_options_exempt

import datetime
import yagmail

from .models import Form, FormQuestion, FormAnswer, ContentChoice, Comment, Person


def index(request):
    return redirect(main)


def main(request):
    if not request.user.is_authenticated:    # MAIN NO LOGIN (LOGIN BUTTON)
        return render(request, 'web/mains/main_nologin.html', {})

    elif request.user.person.role != "student" and request.user.person.approved is False:    # NOT APPROVED BY IT YET
        return redirect(not_approved)

    elif request.user.person.role == "student":    # MAIN STUDENT (CREATE FORM, YOUR FORMS, NOTIFY LAB)
        form_list = Form.objects.filter(person=Person.objects.get(user=request.user), is_main=False)
        return render(request, 'web/mains/main_student.html', {"form_list": form_list})

    elif request.user.person.role == "teacher":    # MAIN TEACHER (APPROVE FORM, APPROVE USER)
        form_list = Form.objects.filter(type="SEAF", approved_teacher=False, is_finished=False, is_completed=False)
        app_person_list = Person.objects.filter(approved=False)
        return render(request, 'web/mains/main_teacher.html', {"form_list": form_list,
                                                               "app_person_list": app_person_list})

    elif request.user.person.role == "labassist":    # MAIN LAB ASSISTANT (APPROVE FORM, END FORM, APPROVE USER)
        form_list = Form.objects.filter(type="SEAF", approved_labassist=False, is_finished=False, is_completed=False)
        form_list_finish = Form.objects.filter(is_finished=True, is_completed=False)
        app_person_list = Person.objects.filter(approved=False)
        return render(request, 'web/mains/main_labassist.html',
                      {"form_list": form_list, "form_list_finish": form_list_finish,
                       "app_person_list": app_person_list})

    elif request.user.person.role == "safety":    # MAIN SAFETY INSPECTOR (APPROVE FORM, APPROVE USER)
        form_list = Form.objects.filter(type="RAF", approved_safety=False)
        app_person_list = Person.objects.filter(approved=False)
        return render(request, 'web/mains/main_safety.html', {"form_list": form_list,
                                                              "app_person_list": app_person_list})

    elif request.user.person.role == "director":    # MAIN LAB DIRECTOR (APPROVE FORM TWICE, APPROVE USER)
        form_list_seaf = Form.objects.filter(type="SEAF", approved_director=False, is_completed=False)
        form_list_raf = Form.objects.filter(type="RAF", approved_director=False, is_completed=False)
        app_person_list = Person.objects.filter(approved=False)
        return render(request, 'web/mains/main_director.html',
                      {"form_list_seaf": form_list_seaf, "form_list_raf": form_list_raf,
                       "app_person_list": app_person_list})

    elif request.user.person.role == "inspector":    # MAIN IT INSPECTOR (CHANGE THE PASSWORD OF ACCOUNT, EDIT USER)
        person_list = Person.objects.filter(temp_password=False)
        app_person_list = Person.objects.filter(approved=False)
        all_person_list = Person.objects.filter()
        forms_list = Form.objects.filter()
        return render(request, 'web/mains/main_inspector.html', {"person_list": person_list,
                                                                 "app_person_list": app_person_list,
                                                                 "all_person_list": all_person_list,
                                                                 "forms_list": forms_list})

    else:    # LOGIN ERROR (LOGIN BUTTON, JUST IN CASE)
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)


def create_question(request):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role != "director":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    return render(request, 'web/form/create_question.html', {})


@xframe_options_exempt
def form_view(request, form_id):
    form_type = Form.objects.get(pk=form_id).type
    main_form_id = 1
    if form_type is "RAF":
        main_form_id = 2
    question_list = FormQuestion.objects.filter(form=Form.objects.get(pk=main_form_id)).order_by('order')
    is_choice_list = [i.is_choice for i in question_list]
    is_text_list = [i.is_choice for i in question_list]
    choice_list = [ContentChoice.objects.filter(question=i) for i in question_list]
    form_fn = Form.objects.get(pk=form_id).person.first_name
    form_ln = Form.objects.get(pk=form_id).person.last_name
    return render(request, 'web/form/form_view.html', {"question_list": question_list,
                  "is_choice_list": is_choice_list, "is_text_list": is_text_list, "choice_list": choice_list,
                  "form_id": form_id, "form_type": form_type, "form_fn": form_fn, "form_ln": form_ln})


@xframe_options_exempt
def form_sent(request, form_id):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role != "student":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    return render(request, 'web/form/form_sent.html', {})


def form_created(request, form_type):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role != "student":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    if form_type != "SEAF" and form_type != "RAF":
        request.session['error_page_title'] = 'No access'
        request.session['error_page_content'] = 'You can\'t access this page right now'
        return redirect(error_general)
    new_form = Form(type=form_type, date=datetime.datetime.now(), person=request.user.person, is_main=False,
                    is_started=False, is_finished=False, is_completed=False,
                    approved_labassist=False, approved_teacher=False, approved_director=False,
                    approved_safety=False)
    new_form.save()
    return redirect(form_view, form_id=new_form.pk)


def form_approved(request, form_id):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role == "student" or request.user.person.role == "inspector":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    return render(request, 'web/form/form_approved.html', {})


def form_disapproved(request, form_id):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role == "student" or request.user.person.role == "inspector":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    return render(request, 'web/form/form_disapproved.html', {})


def form_deleted(request, form_id):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role != "student" and request.user.person.role != "inspector":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    return render(request, 'web/form/form_disapproved.html', {})


def person_approved(request, person_id):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role == "student":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    person = Person.objects.get(pk=person_id)
    person.approved = 1
    person.save()
    return render(request, 'web/person/person_approved.html', {})


def person_deleted(request, person_id):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role == "student":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    person = Person.objects.get(pk=person_id)
    person.delete()
    return render(request, 'web/person/person_deleted.html', {})


def password_changed(request, person_id):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role != "inspector":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    if request.method == 'POST':
        newpass = request.POST['newpass' + str(person_id)]
        if len(newpass) == 0:
            request.session['error_page_title'] = 'Empty password'
            request.session['error_page_content'] = 'The password field is empty'
            return redirect(error_general)
        person = Person.objects.get(pk=person_id)
        user = person.user
        user.password = newpass
        person.temp_password = True
        user.save()
        person.save()
    else:
        request.session['error_page_title'] = 'No access'
        request.session['error_page_content'] = 'You can\'t access this page right now'
        return redirect(error_general)
    return render(request, 'web/person/password_changed.html', {})


def role_changed(request, person_id):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.role != "inspector":
        request.session['error_page_title'] = 'No permission'
        request.session['error_page_content'] = 'You have no permission to view this page'
        return redirect(error_general)

    if request.method == 'POST':
        newrole = request.POST['newrole' + str(person_id)]
        person = Person.objects.get(pk=person_id)
        person.role = newrole
        person.save()
    else:
        request.session['error_page_title'] = 'No access'
        request.session['error_page_content'] = 'You can\'t access this page right now'
        return redirect(error_general)
    return render(request, 'web/person/role_changed.html', {})


def login_view(request):
    return render(request, 'web/login/login.html', {})


def after_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is None:
            request.session['error_page_title'] = 'Login failed'
            request.session['error_page_content'] = 'Login failed; wrong email or password'
            return redirect(error_general)
        else:
            login(request, user)
    else:
        request.session['error_page_title'] = 'No access'
        request.session['error_page_content'] = 'You can\'t access this page right now'
        return redirect(error_general)
    return render(request, 'web/login/after_login.html', {})


def register(request):
    return render(request, 'web/login/register.html', {})


def after_register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = User.objects.make_random_password()
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        role = request.POST['role']
        try:
            user_object = User.objects.get(username=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email, email, password)
            user.save()
            user_full = Person(user=user, role=role, first_name=first_name, last_name=last_name, temp_password=False,
                               approved=False)
            user_full.save()
            yagmail.register('letovolabprojecthelp@gmail.com', 'hgsf atlj wybo eejo')
            test_email = yagmail.SMTP('letovolabprojecthelp@gmail.com', 'hgsf atlj wybo eejo')
            content = ['Your password: ' + password + '\nIt is temporary and will be changed later']
            test_email.send(email, 'LetovoLab Password', content)
        else:
            request.session['error_page_title'] = 'Account already exists'
            request.session['error_page_content'] = 'This account already exists'
            return redirect(error_general)
    else:
        request.session['error_page_title'] = 'No access'
        request.session['error_page_content'] = 'You can\'t access this page right now'
        return redirect(error_general)
    return render(request, 'web/login/after_register.html', {})


def logout_view(request):
    logout(request)
    return redirect(main)


def table(request):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    return render(request, 'web/other/table.html', {})


def not_approved(request):
    if not request.user.is_authenticated:
        return render(request, 'web/mains/main_nologin.html', {})
    elif request.user.person.approved:
        return redirect(main)
    return render(request, 'web/person/not_approved.html', {})


@xframe_options_exempt
def about(request):
    return render(request, 'web/other/about.html', {})


def error_general(request):
    return render(request, 'web/error_general.html', {})


def error_404(request):
    return render(request, '404.html', {})


def error_500(request):
    return render(request, '500.html', {})
