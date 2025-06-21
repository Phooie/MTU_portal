from django.urls import path
from . import views
from . import book_views
from .views import set_language
from .import recommendations
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('change-language/', set_language, name='set_language'),
    path('uslogin/', RedirectView.as_view(url='/us/login/', permanent=True)),
    path('mylogin/', RedirectView.as_view(url='/my/login/', permanent=True)),

    path('usregister/', RedirectView.as_view(url='/us/register/', permanent=True)),
    path('myregister/', RedirectView.as_view(url='/my/register/', permanent=True)),

    path('ussample/', RedirectView.as_view(url='/us/sample/', permanent=True)),
    path('mysample/', RedirectView.as_view(url='/my/sample/', permanent=True)),

    path('usscores/', RedirectView.as_view(url='/us/scores/', permanent=True)),
    path('myscores/', RedirectView.as_view(url='/my/scores/', permanent=True)),

    path('usscores2/', RedirectView.as_view(url='/us/scores2/', permanent=True)),
    path('myscores2/', RedirectView.as_view(url='/my/scores2/', permanent=True)),

    path('ushome/', RedirectView.as_view(url='/us/home/', permanent=True)),
    path('myhome/', RedirectView.as_view(url='/my/home/', permanent=True)),

    path('uscampus/', RedirectView.as_view(url='/us/campus/', permanent=True)),
    path('mycampus/', RedirectView.as_view(url='/my/campus/', permanent=True)),

    path('uscourse/', RedirectView.as_view(url='/us/course/', permanent=True)),
    path('mycourse/', RedirectView.as_view(url='/my/course/', permanent=True)),

    path('uscourse2/', RedirectView.as_view(url='/us/course2/', permanent=True)),
    path('mycourse2/', RedirectView.as_view(url='/my/course2/', permanent=True)),

    path('usnews/', RedirectView.as_view(url='/us/news/', permanent=True)),
    path('mynews/', RedirectView.as_view(url='/my/news/', permanent=True)),

    path('uslibiary/', RedirectView.as_view(url='/us/libiary/', permanent=True)),
    path('mylibiary/', RedirectView.as_view(url='/my/libiary/', permanent=True)),

    path('usresearch/', RedirectView.as_view(url='/us/research/', permanent=True)),
    path('myresearch/', RedirectView.as_view(url='/my/research/', permanent=True)),

    path('usdepartment/', RedirectView.as_view(url='/us/department/', permanent=True)),
    path('mydepartment/', RedirectView.as_view(url='/my/department/', permanent=True)),

    path('uspredict/', RedirectView.as_view(url='/us/predict/', permanent=True)),
    path('mypredict/', RedirectView.as_view(url='/my/predict/', permanent=True)),

    path('ussearch/', RedirectView.as_view(url='/us/search/', permanent=True)),
    path('mysearch/', RedirectView.as_view(url='/my/search/', permanent=True)),
    

    path('', views.home, name='home'),
    path('sample/', views.sample, name='sample'),
    path('search/', book_views.search, name='search'),
    path('home/', views.home, name='home'),
    path('track-course-click/', views.track_course_click, name='track_course_click'),
    path('course2/', recommendations.course_search2, name='course2'),
    path('scores2/', views.scores2, name='scores2'),

    path('course/', recommendations.course_search, name='course'),
    path('course2/', recommendations.course_search, name='course2'),
    path('scores/', views.scores, name='scores'),
    
     path('register/', views.register, name='register'),
    path('login/', views.student_login, name='login'),

    path('department/', views.department, name='departments'),
    # path('news/', recommendations.news, name='news'),
    path('events/', recommendations.events, name='events'),
    path('research/', recommendations.research_search, name='research'),
    path('upload/', views.upload_document, name='upload_document'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('news/', recommendations.news_page, name='news'),
    path('campus/', views.campus, name='campus'),

    path('predict/', recommendations.predict_grade, name='predict'),
    # path('books/', recommend_books_view, name='recommend_books')
    path('libiary/', recommendations.book_search, name='libiary'),
    path('check-progress/', views.check_progress, name='check_progress'),
    path('logout/', views.student_logout, name='logout'),


]