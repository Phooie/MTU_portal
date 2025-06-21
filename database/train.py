import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grade_predictor.settings")
django.setup()

from database.models import StudentScore
import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
from django.db.models import Avg

# Get all students
students = StudentScore.objects.values_list('student_id', flat=True).distinct()
rows = []

for student in set(students):
    sems = StudentScore.objects.filter(student_id=student).values('semester').distinct()
    sem_nums = sorted(set([s['semester'] for s in sems]))

    for i in range(len(sem_nums) - 1):
        prev_avg = StudentScore.objects.filter(
            student_id=student, 
            semester=sem_nums[i]
        ).aggregate(avg=Avg('total_score'))['avg']
        
        next_avg = StudentScore.objects.filter(
            student_id=student, 
            semester=sem_nums[i+1]
        ).aggregate(avg=Avg('total_score'))['avg']
        
        if prev_avg and next_avg:
            rows.append({'prev_avg': prev_avg, 'next_avg': next_avg})

df = pd.DataFrame(rows)
X = df[['prev_avg']]
y = df['next_avg']

model = LinearRegression()
model.fit(X, y)

with open('semester_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print(f"Model trained with {len(df)} samples. R² score: {model.score(X, y):.2f}")