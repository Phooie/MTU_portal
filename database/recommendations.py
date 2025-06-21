import os
import openai
import numpy as np
from PyPDF2 import PdfReader
from docx import Document
from django.shortcuts import render, get_object_or_404
from .models import Student, StudentScore,UserEnrollment
from .books import Course,Resource,News,Books_table,Research,Course_table
from django.db.models import Q
import pickle
from django.db.models import F, Avg
import joblib
from django.conf import settings
from elasticsearch_dsl.query import MultiMatch
from .documents import ResourceDocument,BookDocument,CourseDocument,ResearchDocument,NewsDocument
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from .models import UserProfile




def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if 'student_id' not in request.session:
            # messages.error(request, 'Please login to access this page')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# Load model at startup
try:
    model = pickle.load(open('semester_model.pkl', 'rb'))
except:
    model = None

def select_student(request):
    students = Student.objects.all()
    return render(request, 'scores.html', {'students': students})




# views.py

def news_page(request):
    now = timezone.now()

    active_news = News.objects.filter(
        end_date__gte=now
    ).order_by('-start_date')

    return render(request, 'news.html', {'news_list': active_news})



from .recommendation_engine import recommendation_engine




def book_search(request):
    q = request.GET.get("q", "")
    # resource_type = "BOOK"  
    category = request.GET.get("category")

    context = {
        'query': q,
        # 'resource_type': resource_type,
        'category': category,
        'categories': Books_table.objects.values_list('category', flat=True).distinct().order_by("category")
    }

    # If no query but category exists
    if not q and category:
        context["resources"] = Books_table.objects.filter(category=category)[:50]
        return render(request, "libiary.html", context)

    # If no query and no category filter
    if not q and not category:
        context["resources"] = Books_table.objects.all()
        return render(request, "libiary.html", context)

    # Elasticsearch Search with Fixes
    if q:
        query = MultiMatch(
            query=q,
            fields=["title", "author", "description", "category"],
            fuzziness="AUTO"
        )
        s = BookDocument.search().query(query)

        # Applying category filter if provided
        if category:
            s = s.filter('term', category=category)

        context["resources"] = s[:20]

    # Semantic Recommendations
    if q:
        context["books"] = recommendation_engine.get_recommendations(
            query=q,
            category=category
        )

    return render(request, "libiary.html", context)




@login_required_custom
def course_search(request):
    q = request.GET.get("q", "")
    # resource_type = "BOOK"  
    category = request.GET.get("category")

    context = {
        'query': q,
        # 'resource_type': resource_type,
        'category': category,
        'categories': Course_table.objects.values_list('category', flat=True).distinct().order_by("category")
    }


    student_id = request.session.get('student_id')




    if request.user.is_authenticated:
        try:
            enrollments = UserEnrollment.objects.filter(student=student_id)
            enrolled_courses = [enrollment.course for enrollment in enrollments]
            enrolled_categories = set(course.category for course in enrolled_courses)
            recommended_courses = Course_table.objects.filter(
                category__in=enrolled_categories
            ).exclude(id__in=[course.id for course in enrolled_courses])[:5]
            context["recommended_courses"] = recommended_courses
        except Student.DoesNotExist:
            pass



    # if request.user.is_authenticated:
    #     try:
    #         enrollments = UserEnrollment.objects.filter(student=student_id)
    #         enrolled_courses = [enrollment.course for enrollment in enrollments]
    #         enrolled_categories = set(course.category for course in enrolled_courses)
            
    #         # Get text from enrolled courses for semantic search
    #         enrolled_text = " ".join([course.title + " " + course.description for course in enrolled_courses if course.title and course.description])
            
    #         if enrolled_text:  # Only perform semantic search if we have text to search with
    #             # Create a more_like_this query for semantic recommendations
    #             query = {
    #                 "more_like_this": {
    #                     "fields": ["title", "description", "instructor"],
    #                     "like": enrolled_text,
    #                     "min_term_freq": 1,
    #                     "min_doc_freq": 1,
    #                     "max_query_terms": 25
    #                 }
    #             }
                
    #             # Filter by enrolled categories and exclude already enrolled courses
    #             s = CourseDocument.search().query(query)
    #             s = s.filter('terms', category=list(enrolled_categories))
    #             s = s.exclude('terms', id=[course.id for course in enrolled_courses])
                
    #             recommended_courses = s[:10].to_queryset()
    #             context["recommended_courses"] = recommended_courses
                
    #     except Student.DoesNotExist:
    #         pass




    # If no query but category exists
    if not q and category:
        context["resources"] = Course_table.objects.filter(category=category)[:50]
        return render(request, "course.html", context)

    # If no query and no category filter
    if not q and not category:
        context["resources"] = Course_table.objects.all()
        return render(request, "course.html", context)

    # Elasticsearch Search with Fixes
    if q:
        query = MultiMatch(
            query=q,
            fields=["title", "instructor", "description", "category"],
            fuzziness="AUTO"
        )
        s = CourseDocument.search().query(query)

        # Applying category filter if provided
        if category:
            s = s.filter('term', category=category)

        context["resources"] = s[:20]

    # Semantic Recommendations
    if q:
        context["books"] = recommendation_engine.get_recommendations(
            query=q,
            category=category
        )

    if student_id:
        
            student = Student.objects.get(student_id=student_id)
            user_profile, _ = UserProfile.objects.get_or_create(student=student)
            
            # Add current search to history if it exists
            if q:
                user_profile.add_search_query(q)
            
            # Get recommendations based on past searches
            past_queries = user_profile.search_history[-3:]  # Get last 3 searches
            search_recommendations = []
            for query in past_queries:
                query_recommend = MultiMatch(
                    query=query, 
                    fields=["title", "instructor", "description", "category"], 
                    fuzziness="AUTO"
                )
                search_recommendations.extend(CourseDocument.search().query(query_recommend)[:5])
            
            context['search_recommendations'] = search_recommendations

    return render(request, "course.html", context)



def course_search2(request):
    q = request.GET.get("q", "")
    # resource_type = "BOOK"  
    category = request.GET.get("category")

    context = {
        'query': q,
        # 'resource_type': resource_type,
        'category': category,
        'categories': Course_table.objects.values_list('category', flat=True).distinct().order_by("category")
    }

    if not q and category:
        context["resources"] = Course_table.objects.filter(category=category)[:50]
        return render(request, "course2.html", context)

    # If no query and no category filter
    if not q and not category:
        context["resources"] = Course_table.objects.all()
        return render(request, "course2.html", context)

    # Elasticsearch Search with Fixes
    if q:
        query = MultiMatch(
            query=q,
            fields=["title", "instructor", "description", "category"],
            fuzziness="AUTO"
        )
        s = CourseDocument.search().query(query)

        # Applying category filter if provided
        if category:
            s = s.filter('term', category=category)

        context["resources"] = s[:20]

    # Semantic Recommendations
    if q:
        context["books"] = recommendation_engine.get_recommendations(
            query=q,
            category=category
        )

    return render(request, "course2.html", context)

def research_search(request):
    q = request.GET.get("q", "")
    # resource_type = "BOOK"  
    category = request.GET.get("category")

    context = {
        'query': q,
        # 'resource_type': resource_type,
        'category': category,
        'categories': Research.objects.values_list('category', flat=True).distinct().order_by("category")
    }

    # If no query but category exists
    if not q and category:
        context["resources"] = Research.objects.filter(category=category)[:50]
        return render(request, "research.html", context)

    # If no query and no category filter
    if not q and not category:
        context["resources"] = Research.objects.all()
        return render(request, "research.html", context)

    # Elasticsearch Search with Fixes
    if q:
        query = MultiMatch(
            query=q,
            fields=["title", "researcher", "abstract", "category"],
            fuzziness="AUTO"
        )
        s = ResearchDocument.search().query(query)

        # Applying category filter if provided
        if category:
            s = s.filter('term', category=category)

        context["resources"] = s[:20]

    # Semantic Recommendations
    if q:
        context["books"] = recommendation_engine.get_recommendations(
            query=q,
            category=category
        )

    return render(request, "research.html", context)




# def hybrid_search(request):
#     q = request.GET.get("q", "")
#     resource_type = "BOOK"  # Use the actual value from RESOURCE_TYPES
#     category = request.GET.get("category")
#     context = {
#         'query': q, 
#         'resource_type': resource_type, 
#         'category': category,
#         'categories': Resource.objects.filter(resource_type='BOOK').values_list('category', flat=True).distinct()
#     }

#     # When no search query but category filter exists
#     if not q and category:
#         context["resources"] = Resource.objects.filter(
#             resource_type='BOOK',
#             category=category
#         )[:50]
#         return render(request, "libiary.html", context)

#     # When no search query and no category filter
#     if not q and not category:
#         context["resources"] = Resource.objects.filter(resource_type='BOOK')[:50]
#         return render(request, "libiary.html", context)
    
#     # Elasticsearch Results for books only
    
#     if q:
#         query = MultiMatch(
#             query=q, 
#             fields=["title", "instructor", "description", "category"],
#             fuzziness="AUTO"
#         )
#         s = ResourceDocument.search().query(query).filter('term', resource_type='BOOK')
        
#         if category:
#             s = s.filter('term', category=category)
            
#         context["resources"] = s[:20]
    
#     # Semantic Book Recommendations
#     if q:
#         context["books"] = recommendation_engine.get_recommendations(
#             query=q,
#             resource_type=resource_type,
#             category=category
#         )

#     return render(request, "libiary.html", context)







# def course_hybrid_search(request):
#     q = request.GET.get("q", "")
#     resource_type = "COURSE"  # Use the actual value from RESOURCE_TYPES
#     category = request.GET.get("category")
#     context = {
#         'query': q, 
#         'resource_type': resource_type, 
#         'category': category,
#         'categories': Resource.objects.filter(resource_type='COURSE').values_list('category', flat=True).distinct()
#     }

#     # When no search query but category filter exists
#     if not q and category:
#         context["resources"] = Resource.objects.filter(
#             resource_type='COURSE',
#             category=category
#         )[:50]
#         return render(request, "course.html", context)

#     # When no search query and no category filter
#     if not q and not category:
#         context["resources"] = Resource.objects.filter(resource_type='COURSE')[:50]
#         return render(request, "course.html", context)
    
#     # Elasticsearch Results for books only
#     if q:
#         query = MultiMatch(
#             query=q, 
#             fields=["title", "instructor", "description", "category"],
#             fuzziness="AUTO"
#         )
#         s = ResourceDocument.search().query(query).filter('term', resource_type='COURSE')
        
#         if category:
#             s = s.filter('term', category=category)
            
#         context["resources"] = s[:20]
    
#     # Semantic Book Recommendations
#     if q:
#         context["course"] = recommendation_engine.get_recommendations(
#             query=q,
#             resource_type=resource_type,
#             category=category
#         )

#     return render(request, "course.html", context)























def course_hybrid_search(request):
    q = request.GET.get("q", "")
    resource_type = "COURSE"
    category = request.GET.get("category")
    
    # Get the student (assuming you have authentication)
    student = request.user.student if hasattr(request.user, 'student') else None
    
    context = {
        'query': q, 
        'resource_type': resource_type, 
        'category': category,
        'categories': Resource.objects.filter(resource_type='COURSE').values_list('category', flat=True).distinct()
    }

    # Track search interaction if there's a query and a student is logged in
    if q and student:
        Interaction.objects.create(
            student=student,
            interaction_type='SEARCH',
            weight=1.0
        )

    # When no search query but category filter exists
    if not q and category:
        context["resources"] = Resource.objects.filter(
            resource_type='COURSE',
            category=category
        )[:50]
        return render(request, "course.html", context)

    # When no search query and no category filter
    if not q and not category:
        context["resources"] = Resource.objects.filter(resource_type='COURSE')[:50]
        return render(request, "course.html", context)
    
    # Elasticsearch Results for courses only
    if q:
        query = MultiMatch(
            query=q, 
            fields=["title", "instructor", "description", "category"],
            fuzziness="AUTO"
        )
        s = ResourceDocument.search().query(query).filter('term', resource_type='COURSE')
        
        if category:
            s = s.filter('term', category=category)
            
        context["resources"] = s[:20].to_queryset()  # Convert to queryset for template
    
    # Semantic Course Recommendations
    if q:
        context["course"] = recommendation_engine.get_recommendations(
            query=q,
            resource_type=resource_type,
            category=category
        )

    return render(request, "course.html", context)




# def course_hybrid_search(request):
#     q = request.GET.get("q", "")
#     resource_type = "COURSE"  # Use the actual value from RESOURCE_TYPES
#     category = request.GET.get("category")
#     context = {
#         'query': q, 
#         'resource_type': resource_type, 
#         'category': category,
#         'categories': Resource.objects.filter(resource_type='COURSE').values_list('category', flat=True).distinct()
#     }

#     # When no search query but category filter exists
#     if not q and category:
#         context["resources"] = Resource.objects.filter(
#             resource_type='COURSE',
#             category=category
#         )[:50]
#         return render(request, "course.html", context)

#     # When no search query and no category filter
#     if not q and not category:
#         context["resources"] = Resource.objects.filter(resource_type='COURSE')[:50]
#         return render(request, "course.html", context)
    
#     # Elasticsearch Results for books only
#     if q:
#         query = MultiMatch(
#             query=q, 
#             fields=["title", "instructor", "description", "category"],
#             fuzziness="AUTO"
#         )
#         s = ResourceDocument.search().query(query).filter('term', resource_type='COURSE')
        
#         if category:
#             s = s.filter('term', category=category)
            
#         context["resources"] = s[:20]
    
#     # Semantic Book Recommendations
#     if q:
#         context["course"] = recommendation_engine.get_recommendations(
#             query=q,
#             resource_type=resource_type,
#             category=category
#         )

#     return render(request, "course.html", context)

@login_required_custom
def predict_grade(request):
    import math
    
    # Load all trained models
    model_path = os.path.join(settings.BASE_DIR, 'model')
    model_total = joblib.load(os.path.join(model_path, 'grade_predictor.joblib'))
    model_assignments = joblib.load(os.path.join(model_path, 'assignments_predictor.joblib'))
    model_tutorial = joblib.load(os.path.join(model_path, 'tutorial_predictor.joblib'))
    model_final = joblib.load(os.path.join(model_path, 'final_predictor.joblib'))
    
    student_id = request.session.get('student_id')
    
    # Get current averages for all components
    current_data = StudentScore.objects.filter(
        student=student_id
    ).aggregate(
        assignments_avg=Avg('assignments'),
        tutorial_avg=Avg('tutorial'),
        final_avg=Avg('final'),
        total_avg=Avg(F('assignments') + F('tutorial') + F('final'))
    )
    
    current_avg = current_data['total_avg']
    assignments_avg = current_data['assignments_avg'] or 0
    tutorial_avg = current_data['tutorial_avg'] or 0
    final_avg = current_data['final_avg'] or 0
    
    # Make predictions if data exists
    predicted_total = None
    predicted_assignments = None
    predicted_tutorial = None
    predicted_final = None
    
    if current_avg:
        # Predict total score
        predicted_total = model_total.predict([[current_avg]])[0]
        
        # Predict individual components (using all three current components as features)
        input_features = [[assignments_avg, tutorial_avg, final_avg]]
        predicted_assignments = model_assignments.predict(input_features)[0]
        predicted_tutorial = model_tutorial.predict(input_features)[0]
        predicted_final = model_final.predict(input_features)[0]
    
    averages = {
        'assignments': assignments_avg,
        'tutorial': tutorial_avg,
        'final': final_avg
    }

    weak_area = min(averages, key=averages.get) if averages else None

    # Handle optional input: goal, assignment, tutorial
    goal = request.GET.get('goal')
    ass_input = request.GET.get('user_assignment')
    tuto_input = request.GET.get('user_tutorial')

    final_required_result = None

    if goal and ass_input and tuto_input:
        try:
            goal = float(goal)
            ass_input = float(ass_input)
            tuto_input = float(tuto_input)

            required = goal - (ass_input + tuto_input)

            if required <= 0:
                final_required_result = f"✅ Already achieved! Total = {ass_input + tuto_input:.1f}/100"
            elif required > 80:
                final_required_result = f"❌ Impossible. Need {required:.1f}/80 in Final (Max = 80)"
            else:
                final_required_result = f"🎯 You need {required:.1f}/80 in Final to reach {goal}%"
        except ValueError:
            final_required_result = "❌ Invalid input."

    return render(request, 'results.html', {
        'student': student_id,
        'current_avg': round(current_avg, 1) if current_avg else "N/A",
        'predicted_grade': round(predicted_total, 1) if predicted_total else "N/A",
        'predicted_assignments': round(predicted_assignments, 1) if predicted_assignments else "N/A",
        'predicted_tutorial': round(predicted_tutorial, 1) if predicted_tutorial else "N/A",
        'predicted_final': round(predicted_final, 1) if predicted_final else "N/A",
        'student_name': request.session.get('student_name'),
        'weak_area': weak_area,
        'score_components': averages,
        'final_required_result': final_required_result
    })


# @login_required_custom
# def predict_grade(request):
#     import math
    
#     # Load the trained model
#     model_path = os.path.join(settings.BASE_DIR, 'model', 'grade_predictor.joblib')
#     model = joblib.load(model_path)
    
#     student_id = request.session.get('student_id')
    
#     current_avg = StudentScore.objects.filter(
#         student=student_id
#     ).annotate(
#         total=F('assignments') + F('tutorial') + F('final')
#     ).aggregate(avg=Avg('total'))['avg']
    
#     predicted_grade = model.predict([[current_avg]])[0] if current_avg else None

#     scores = StudentScore.objects.filter(student=student_id).aggregate(
#         assignments_avg=Avg('assignments'),
#         tutorial_avg=Avg('tutorial'),
#         final_avg=Avg('final')
#     )

#     assignments = scores['assignments_avg'] or 0
#     tutorial = scores['tutorial_avg'] or 0
#     final = scores['final_avg'] or 0

#     averages = {
#         'assignments': assignments,
#         'tutorial': tutorial,
#         'final': final
#     }

#     weak_area = min(averages, key=averages.get) if averages else None

#     # Handle optional input: goal, assignment, tutorial
#     goal = request.GET.get('goal')
#     ass_input = request.GET.get('user_assignment')
#     tuto_input = request.GET.get('user_tutorial')

#     final_required_result = None

#     if goal and ass_input and tuto_input:
#         try:
#             goal = float(goal)
#             ass_input = float(ass_input)
#             tuto_input = float(tuto_input)

#             required = goal - (ass_input + tuto_input)

#             if required <= 0:
#                 final_required_result = f"✅ Already achieved! Total = {ass_input + tuto_input:.1f}/100"
#             elif required > 80:
#                 final_required_result = f"❌ Impossible. Need {required:.1f}/80 in Final (Max = 80)"
#             else:
#                 final_required_result = f"🎯 You need {required:.1f}/80 in Final to reach {goal}%"
#         except ValueError:
#             final_required_result = "❌ Invalid input."

#     return render(request, 'results.html', {
#         'student': student_id,
#         'current_avg': round(current_avg, 1) if current_avg else "N/A",
#         'predicted_grade': round(predicted_grade, 1) if predicted_grade else "N/A",
#         'student_name': request.session.get('student_name'),
#         'weak_area': weak_area,
#         'score_components': averages,
#         'final_required_result': final_required_result
#     })





# @login_required_custom
# def predict_grade(request):
#     # Load the trained model
#     model_path = os.path.join(settings.BASE_DIR, 'model', 'grade_predictor.joblib')
#     model = joblib.load(model_path)
    
#     # Get the student
#     student_id = request.session.get('student_id')
    
#     # Calculate current average (using assignments + tutorial + final only)
#     current_avg = StudentScore.objects.filter(
#         student=student_id
#     ).annotate(
#         total=F('assignments') + F('tutorial') + F('final')  # Updated calculation
#     ).aggregate(avg=Avg('total'))['avg']
    
#     # Make prediction (input is just the sum of relevant scores)
#     predicted_grade = model.predict([[current_avg]])[0] if current_avg else None

#     # Calculate component averages (excluding attendance)
#     scores = StudentScore.objects.filter(student=student_id).aggregate(
#         assignments_avg=Avg('assignments'),
#         tutorial_avg=Avg('tutorial'),
#         final_avg=Avg('final')
#     )

#     averages = {
#         'assignments': scores['assignments_avg'] or 0,
#         'tutorial': scores['tutorial_avg'] or 0,
#         'final': scores['final_avg'] or 0
#     }

#     # Find weakest component (lowest average)
#     weak_area = min(averages, key=averages.get) if averages else None

#     return render(request, 'results.html', {
#         'student': student_id,
#         'current_avg': round(current_avg, 1) if current_avg else "N/A",
#         'predicted_grade': round(predicted_grade, 1) if predicted_grade else "N/A",
#         'student_name': request.session.get('student_name'),
#         'weak_area': weak_area,
#         'score_components': averages  # Pass all components to template
#     })






# @login_required_custom
# def predict_grade(request):
#     # Load the trained model
#     model_path = os.path.join(settings.BASE_DIR, 'model', 'grade_predictor.joblib')
#     model = joblib.load(model_path)
    
#     # Get the student
#     student_id = request.session.get('student_id')
    
#     # Calculate current average (using the same method as training)
#     current_avg = StudentScore.objects.filter(
#         student=student_id
#     ).annotate(
#         total=F('attendance') + F('assignments') + F('midterm') + F('final')
#     ).aggregate(avg=Avg('total'))['avg']
    
#     # Make prediction
#     predicted_grade = model.predict([[current_avg]])[0]


#     scores = StudentScore.objects.filter(student=student_id).aggregate(
#         assignment_avg=Avg('assignments'),
#         attendance_avg=Avg('attendance'),
#         midterm_avg=Avg('midterm'),
#         final_avg=Avg('final')
#     )

#     averages = {
#         'assignments': scores['assignment_avg'] or 0,
#         'attendance': scores['attendance_avg'] or 0,
#         'midterm': scores['midterm_avg'] or 0,
#         'final': scores['final_avg'] or 0
#     }

#     weak_area = min(averages, key=averages.get)



    
#     return render(request, 'results.html', {
#         'student': student_id,
#         'current_avg': round(current_avg, 1),
#         'predicted_grade': round(predicted_grade, 1),
#         'student_name': request.session.get('student_name'),
#         'weak_area': weak_area
#     })


@login_required_custom
def department_recommendations(request):
    # Get student ID from session
    student_id = request.session.get('student_id')
    
    try:
        # Get student and their department
        student = Student.objects.get(student_id=student_id)
        department = student.department
        
        # Get all courses the student has taken
        taken_courses = StudentScore.objects.filter(
            student=student
        ).values_list('subject__id', flat=True)
        
        # Get the category choices as a dictionary
        category_choices = dict(Course._meta.get_field('category').choices)
        
        # Get recommended courses (same department, not taken)
        recommended_courses = Course.objects.filter(
            category=department  # Match student's department to course category
        ).exclude(
            id__in=taken_courses
        ).order_by('title')
        
        # Group by category (using the verbose name)
        courses_by_category = {}
        for course in recommended_courses:
            # Get human-readable category name
            category_name = category_choices.get(course.category, 'Other')
            
            if category_name not in courses_by_category:
                courses_by_category[category_name] = []
            courses_by_category[category_name].append(course)
            
    except Student.DoesNotExist:
        return render(request, 'error.html', {'error': 'Student not found'})

    return render(request, 'course.html', {
        'student': student,
        'courses_by_category': courses_by_category,
        'department_name': category_choices.get(department, department)
    })


def department_recommendations(request):
    # Get student ID from session
    student_id = request.session.get('student_id')
    
    try:
        # Get student and their department
        student = Student.objects.get(student_id=student_id)
        department = student.department
        
        # Get all courses the student has taken
        taken_courses = StudentScore.objects.filter(
            student=student
        ).values_list('subject__id', flat=True)
        
        # Get the category choices as a dictionary
        category_choices = dict(Course._meta.get_field('category').choices)
        
        # Get recommended courses (same department, not taken)
        recommended_courses = Course.objects.filter(
            category=department  # Match student's department to course category
        ).exclude(
            id__in=taken_courses
        ).order_by('title')
        
        # Group by category (using the verbose name)
        courses_by_category = {}
        for course in recommended_courses:
            # Get human-readable category name
            category_name = category_choices.get(course.category, 'Other')
            
            if category_name not in courses_by_category:
                courses_by_category[category_name] = []
            courses_by_category[category_name].append(course)
            
    except Student.DoesNotExist:
        return render(request, 'error.html', {'error': 'Student not found'})

    return render(request, 'course.html', {
        'student': student,
        'courses_by_category': courses_by_category,
        'department_name': category_choices.get(department, department)
    })


# def research(request):
#     # Example: Filter by a specific field value
#     filtered_data2 = Resource.objects.filter(resource_type='RESEARCH')

#     # # Example: Filter by date
#     # filtered_data = YourModel.objects.filter(date_field__year=2024)

#     return render(request, 'research.html', {'data2': filtered_data2})


def events(request):
    # Example: Filter by a specific field value
    filtered_data1 = Resource.objects.filter(resource_type='EVENT')

    # # Example: Filter by date
    # filtered_data = YourModel.objects.filter(date_field__year=2024)

    return render(request, 'events.html', {'data1': filtered_data1})


def news(request):
    # Example: Filter by a specific field value
    filtered_data = Resource.objects.filter(resource_type='NEWS')

    # # Example: Filter by date
    # filtered_data = YourModel.objects.filter(date_field__year=2024)

    return render(request, 'news.html', {'data': filtered_data})


def research(request):
    # Example: Filter by a specific field value
    filtered_data2 = Resource.objects.filter(resource_type='RESEARCH')

    # # Example: Filter by date
    # filtered_data = YourModel.objects.filter(date_field__year=2024)

    return render(request, 'research.html', {'data2': filtered_data2})