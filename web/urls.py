from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),

    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('successful-login/', views.after_login, name='after_login'),
    path('password-sent/', views.after_register, name='after_register'),
    path('logout/', views.logout_view, name='logout_view'),

    path('form/<int:form_id>/', views.form_view, name='form_view'),
    path('form-created/<slug:form_type>/', views.form_created, name='form_created'),
    path('form-sent/<int:form_id>/', views.form_sent, name='form_sent'),
    path('form-approved/<int:form_id>/', views.form_approved, name='form_approved'),
    path('form-finished/<int:form_id>/', views.form_finished, name='form_finished'),
    path('form-disapproved/<int:form_id>/', views.form_disapproved, name='form_disapproved'),
    path('form-deleted/<int:form_id>/', views.form_deleted, name='form_deleted'),
    path('create_question/', views.create_question, name='create_question'),

    path('person-approved/<int:person_id>/', views.person_approved, name='person_approved'),
    path('person-deleted/<int:person_id>/', views.person_deleted, name='person_deleted'),
    path('password-changed/<int:person_id>/', views.password_changed, name='password_changed'),
    path('role-changed/<int:person_id>/', views.role_changed, name='role_changed'),
    path('not-approved/', views.not_approved, name='not_approved'),

    path('table/', views.table, name='table'),
    path('about/', views.about, name='about'),

    path('error/', views.error_general, name='error_general'),
    path('error-form/', views.error_form, name='error_form'),
    path('404/', views.error_404, name='error_404'),
    path('500/', views.error_500, name='error_500'),
]
