from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('request/wait', views.wait, name='wait'),
    path('request', views.request, name='request'),
    path('request/', views.request, name='request'),
    path('request/<guid>', views.request, name='request_guid'),
    path('request/<guid>/choose_bank', views.choose_bank, name='choose_bank'),
    path('request/<guid>/bank_form/<bankID>',
         views.bank_form, name='bank_form'),
    path('request/<guid>/bank_form/<bankID>/<job_id>',
         views.bank_form, name='bank_form_status'),
    path('request/<guid>/session_status_json/<bankID>/<job_id>',
         views.session_status_json, name='session_status_json'),
    path('request/<guid>/session_status/<bankID>/<job_id>',
         views.session_status, name='session_status'),
    path('request/<guid>/success/<bankID>/<job_id>',
         views.success, name='success'),
    path('request/<guid>/challenge_response/<bankID>/<job_id>',
         views.challenge_response, name='challenge_response'),
    path('request/<guid>/challenge_response_dropdown/<bankID>/<job_id>',
         views.challenge_response_dropdown, name='challenge_response_dropdown'),
    path('request/<guid>/challenge_response_image/<bankID>/<job_id>',
         views.challenge_response_image, name='challenge_response_image'),
    path('request/<guid>/provide_challenge_response/<bankID>/<job_id>',
         views.provide_challenge_response, name='provide_challenge_response'),
]
