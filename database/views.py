from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Student, StudentAuth,StudentScore,Semester,Subject
from .books import News

from django.db.models import F
from collections import defaultdict
from elasticsearch_dsl.query import MultiMatch 
from .documents import ResourceDocument,NewsDocument,CourseDocument
from django.http import HttpResponseRedirect
from django.utils.translation import activate, get_language
from django.http import HttpResponseRedirect
from django.urls import translate_url
from django.utils.translation import activate













from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
@csrf_exempt  # Only use this if you're having CSRF issues - better to properly handle CSRF
def track_course_click(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'student'):
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
    
    try:
        data = json.loads(request.body)
        resource_id = data.get('resource_id')
        
        if not resource_id:
            return JsonResponse({'status': 'error', 'message': 'Resource ID required'}, status=400)
            
        resource = Resource.objects.get(resource_id=resource_id)
        
        Interaction.objects.create(
            student=request.user.student,
            resource=resource,
            interaction_type='CLICK',
            weight=1.0  # You can adjust this based on importance
        )
        
        return JsonResponse({'status': 'success'})
        
    except Resource.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Resource not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)














import os
import base64
from django.conf import settings
from .models import Document
from .summarizer import generate_summary

def upload_document(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        document = Document(
            title=request.POST.get('title', 'Untitled Document'),
            pdf_file=request.FILES['pdf_file']
        )
        document.save()
        
        # Generate summary
        file_path = os.path.join(settings.MEDIA_ROOT, document.pdf_file.name)



        request.session['processing'] = True#new
        request.session['document_id'] = document.id#new




        summary = generate_summary(file_path)
        document.summary = summary
        document.save()
        

        request.session['processing'] = False #new
        return redirect('document_detail', pk=document.pk)
    
    return render(request, 'upload.html')


def check_progress(request):
    processing = request.session.get('processing', False)
    document_id = request.session.get('document_id', None)
    
    if document_id and not processing:
        return JsonResponse({
            'status': 'complete',
            'document_id': document_id
        })
    elif processing:
        return JsonResponse({
            'status': 'processing',
            'progress': 50  # In a real app, you'd track actual progress
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'No processing job found'
        })

def document_detail(request, pk):
    document = Document.objects.get(pk=pk)
    
    # Prepare PDF for display
    with open(document.pdf_file.path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    context = {
        'document': document,
        'base64_pdf': base64_pdf
    }
    return render(request, 'detail.html', context)



def set_language(request):
    lang_code = request.POST.get('language')
    next_url = request.POST.get('next', '/')

    if lang_code:
        activate(lang_code)
        request.session['django_language'] = lang_code

        # If English is selected and you want the original path without any language prefix
        if lang_code == 'en':
            # Strip any existing language prefix manually (e.g., /es/login → /login)
            parts = next_url.strip('/').split('/', 1)
            if parts[0] in ['my', 'es','us']:  # add more if needed
                next_url = '/' + (parts[1] if len(parts) > 1 else '')
            return HttpResponseRedirect(next_url or '/')

        # For other languages, use translated URL
        translated_url = translate_url(next_url, lang_code)
        return HttpResponseRedirect(translated_url)

    return HttpResponseRedirect('/')

# def sample(request):
#     q = request.GET.get("q")
#     context = {}
#     if q:
#         query = MultiMatch(query=q, fields=["title", "instructor","description","category","resource_type"], fuzziness="AUTO")
#         s = ResourceDocument.search().query(query)
#         context ["resource"] = s
#     return render (request, "sample.html",context)


from .documents import NewsDocument,BookDocument,ResearchDocument

# def sample(request):
#     q = request.GET.get("q")
#     context = {}

#     if q:
#         # Search across ResourceDocument (Books, Courses, etc.)
#         query_resource = MultiMatch(query=q, fields=["title", "instructor", "description", "category", "resource_type"], fuzziness="AUTO")
#         s_resource = ResourceDocument.search().query(query_resource)

#         query_course = MultiMatch(query=q, fields=["title", "instructor", "description", "category"], fuzziness="AUTO")
#         s_course = CourseDocument.search().query(query_course)

#         # Search across NewsDocument (News articles)
#         query_news = MultiMatch(query=q, fields=["title", "description", "category", "posted_by"], fuzziness="AUTO")
#         s_news = NewsDocument.search().query(query_news)

#         query_books = MultiMatch(
#             query=q,
#             fields=["title", "author", "description", "category"],
#             fuzziness="AUTO"
#         )
#         s_books = BookDocument.search().query(query_books)


#         query_research = MultiMatch(
#             query=q,
#             fields=["title", "researcher", "abstract", "category"],
#             fuzziness="AUTO"
#         )
#         s_research = ResearchDocument.search().query(query_research)

#         # Combine results
#         context["resources"] = s_resource[:20]  # Books, courses, etc.
#         context["courses"] = s_course[:20]
#         context["news"] = s_news[:20]  # News articles
#         context["books"] = s_books[:20]
#         context["research"] = s_research[:20]

#     return render(request, "sample.html", context)









from .models import UserProfile
from .documents import ResourceDocument, NewsDocument, BookDocument, CourseDocument, ResearchDocument  # Import your document classes

def sample(request):
    q = request.GET.get("q")
    context = {}

    if q:

        # Search across multiple document types
        query_resource = MultiMatch(query=q, fields=["title", "description", "category"], fuzziness="AUTO")
        s_resource = ResourceDocument.search().query(query_resource)

        query_news = MultiMatch(query=q, fields=["title", "description", "category"], fuzziness="AUTO")
        s_news = NewsDocument.search().query(query_news)

        query_books = MultiMatch(query=q, fields=["title", "author", "description", "category"], fuzziness="AUTO")
        s_books = BookDocument.search().query(query_books)

        query_courses = MultiMatch(query=q, fields=["title", "instructor", "description", "category"], fuzziness="AUTO")
        s_courses = CourseDocument.search().query(query_courses)

        query_research = MultiMatch(query=q, fields=["title", "researcher", "abstract", "category", "document_link"], fuzziness="AUTO")
        s_researches = ResearchDocument.search().query(query_research)

        # Generate recommendations based on past searches
        # past_queries = user_profile.search_history[-5:]  # Get last 5 searches
        # recommendations = []
        # for query in past_queries:
        #     query_recommend = MultiMatch(query=query, fields=["title", "description", "category"], fuzziness="AUTO")
        #     recommendations.extend(ResourceDocument.search().query(query_recommend)[:5])

        # user_profile.update_recommendations(recommendations)

        # Combine results for template
        context["resources"] = s_resource[:20]
        context["news"] = s_news[:20]
        context["books"] = s_books[:20]
        context["courses"] = s_courses[:20]
        context["researches"] = s_researches[:20]
        # context["recommendations"] = recommendations

    return render(request, "sample.html",context)




def home(request):
    user_language = get_language()  # Fetch the active language
    print(f"Current language: {user_language}")
    now = timezone.now()

    # Fetch latest news
    new_news = News.objects.filter(
        is_new=True,
        end_date__gte=now
    ).order_by('-start_date').first()

    # Fetch personalized recommendations
    # user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    # past_queries = user_profile.search_history[-3:]  # Get last 5 searches

    # recommendations = []
    # for query in past_queries:
    #     query_recommend = MultiMatch(query=query, fields=["title", "description", "category"], fuzziness="AUTO")
    #     recommendations.extend(ResourceDocument.search().query(query_recommend)[:5])

    return render(request, 'home.html', {'new_news': new_news})







# def home(request):
#     user_language = get_language()  # Fetch the active language
#     print(f"Current language: {user_language}")
#     now = timezone.now()

#     new_news = News.objects.filter(
#         is_new=True,
#         end_date__gte=now
#     ).order_by('-start_date').first()

#     return render(request, 'home.html', {'new_news': new_news})

def department(request):
    user_language = get_language()  # Fetch the active language
    print(f"Current language: {user_language}")

    return render(request, 'departments.html')

def campus(request):
    user_language = get_language()  # Fetch the active language
    print(f"Current language: {user_language}")

    return render(request, 'campus.html')


def scores(request):
    all_students=Student.objects.all()
    all_subjects=Subject.objects.all()
    all_scores=StudentScore.objects.all()
    user_language = get_language()  # Fetch the active language
    print(f"Current language: {user_language}")

    return render(request, 'scores.html', {'all_students':all_students,'all_subjects':all_subjects,'all_scores':all_scores})

def register(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validate passwords match
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        # Check password length
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return redirect('register')

        try:
            # Check if student exists
            student = Student.objects.get(student_id=student_id)
            
            # Check if already registered
            if StudentAuth.objects.filter(student=student).exists():
                messages.error(request, 'This student is already registered')
                return redirect('register')
            
            # Create auth record
            auth = StudentAuth(student=student)
            auth.set_password(password)
            auth.save()
            
            messages.success(request, 'Registration successful! Please login')
            return redirect('login')

        except Student.DoesNotExist:
            messages.error(request, 'Student ID not found in our records')
            return redirect('register')
        
    user_language = get_language()  # Fetch the active language
    print(f"Current language: {user_language}")

    return render(request, 'register.html')

# def student_login(request):
#     if request.method == 'POST':
#         student_id = request.POST.get('student_id')
#         password = request.POST.get('password')

#         try:
#             auth = StudentAuth.objects.select_related('student').get(
#                 student__student_id=student_id,
#                 is_active=True
#             )

#             if auth.check_password(password):
#                 # Set session data
#                 request.session['student_id'] = auth.student.student_id
#                 request.session['student_name'] = auth.student.student_name
                
#                 # Update last login
#                 auth.last_login = timezone.now()  # Fixed typo (last.login -> last_login)
#                 auth.save()
                
#                 # Redirect to sample.html
#                 return redirect('home')  # Not 'sample.html' - use URL name
            
#             else:
#                 messages.error(request, 'Invalid password')
                
#         except StudentAuth.DoesNotExist:
#             messages.error(request, 'Student not registered or account inactive')

#     user_language = get_language()  # Fetch the active language
#     print(f"Current language: {user_language}")

#     return render(request, 'login.html')



from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import StudentAuth  # Your existing model

def student_login(request):
    # Admin Login Handling
    if request.method == 'POST' and 'username' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            auth_login(request, user)  # Django's built-in login
            return redirect('search')  # Admin dashboard
        else:
            messages.error(request, 'Invalid admin credentials')
            return redirect('login')

    # Student Login Handling (your existing code)
    elif request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')

        try:
            auth = StudentAuth.objects.select_related('student').get(
                student__student_id=student_id,
                is_active=True
            )

            if auth.check_password(password):
                request.session['student_id'] = auth.student.student_id
                request.session['student_name'] = auth.student.student_name
                auth.last_login = timezone.now()
                auth.save()
                return redirect('home')
            else:
                messages.error(request, 'Invalid password')
                
        except StudentAuth.DoesNotExist:
            messages.error(request, 'Student not registered or account inactive')

    return render(request, 'login.html')

def sample_page(request):
    # Optional authentication check
    if 'student_id' not in request.session:
        return redirect('login')
    user_language = get_language()  # Fetch the active language
    print(f"Current language: {user_language}")

    return render(request, 'sample')

from django.shortcuts import redirect

def scores2(request):
    return redirect('/admin/')

def student_logout(request):
    # Clear all session data
    request.session.flush()
    messages.success(request, 'You have been logged out')
    return redirect('home')

# Custom login required decorator
def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if 'student_id' not in request.session:
            messages.error(request, 'Please login to access this page')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper




@login_required_custom
def scores(request):
    student_id = request.session.get('student_id')
    
    # Get scores for logged-in student only
    scores = StudentScore.objects.filter(
        student__student_id=student_id
    ).select_related('subject', 'subject__semester')
    
    # Organize by semester
    organized_scores = {}
    for score in scores:
        semester = score.subject.semester
        if semester not in organized_scores:
            organized_scores[semester] = []
        organized_scores[semester].append(score)
    
    context = {
        'organized_scores': organized_scores,
        'student_name': request.session.get('student_name')
    }
    return render(request, 'scores.html', context)