from django.core.management.base import BaseCommand
from database.models import StudentScore
from django.db.models import Avg, F
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Trains grade prediction models for total and individual components'

    def handle(self, *args, **options):
        # Create model directory if needed
        os.makedirs('model', exist_ok=True)
        
        # Get all student data with calculated totals (excluding attendance)
        students = StudentScore.objects.values('student').distinct()
        rows = []
        
        for student in students:
            student_id = student['student']
            semesters = StudentScore.objects.filter(
                student=student_id
            ).values('semester').distinct()
            
            sem_nums = sorted(set([s['semester'] for s in semesters]))
            
            for i in range(1, len(sem_nums)):
                prev_sems = sem_nums[:i]
                
                # Get previous semester component averages and total
                prev_data = StudentScore.objects.filter(
                    student=student_id,
                    semester__in=prev_sems
                ).aggregate(
                    prev_assignments=Avg('assignments'),
                    prev_tutorial=Avg('tutorial'),
                    prev_final=Avg('final'),
                    prev_total=Avg(F('assignments') + F('tutorial') + F('final'))
                )
                
                # Get current semester component averages and total
                current_data = StudentScore.objects.filter(
                    student=student_id,
                    semester=sem_nums[i]
                ).aggregate(
                    current_assignments=Avg('assignments'),
                    current_tutorial=Avg('tutorial'),
                    current_final=Avg('final'),
                    current_total=Avg(F('assignments') + F('tutorial') + F('final'))
                )
                
                # Only add if all values are available
                if all(v is not None for v in prev_data.values()) and all(v is not None for v in current_data.values()):
                    rows.append({
                        # Features (previous performance)
                        'cumulative_prev_avg': prev_data['prev_total'],
                        'prev_assignments': prev_data['prev_assignments'],
                        'prev_tutorial': prev_data['prev_tutorial'],
                        'prev_final': prev_data['prev_final'],
                        
                        # Targets (current performance)
                        'current_avg': current_data['current_total'],
                        'current_assignments': current_data['current_assignments'],
                        'current_tutorial': current_data['current_tutorial'],
                        'current_final': current_data['current_final']
                    })

        if not rows:
            self.stdout.write(self.style.ERROR('No valid training data available!'))
            return

        df = pd.DataFrame(rows)
        
        # Print debug info
        self.stdout.write(f"\nData Sample (first 5 rows):")
        self.stdout.write(str(df.head()))
        self.stdout.write(f"\nColumns: {list(df.columns)}")
        
        # Train models - keep your existing total score model
        X_total = df[['cumulative_prev_avg']]  # Same as before
        y_total = df['current_avg']
        
        # Additional models for components
        X_components = df[['prev_assignments', 'prev_tutorial', 'prev_final']]
        y_assignments = df['current_assignments']
        y_tutorial = df['current_tutorial']
        y_final = df['current_final']
        
        # Initialize models
        model_total = RandomForestRegressor(n_estimators=100, random_state=42)
        model_assignments = RandomForestRegressor(n_estimators=100, random_state=42)
        model_tutorial = RandomForestRegressor(n_estimators=100, random_state=42)
        model_final = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Train models
        model_total.fit(X_total, y_total)  # Your original model
        model_assignments.fit(X_components, y_assignments)
        model_tutorial.fit(X_components, y_tutorial)
        model_final.fit(X_components, y_final)
        
        # Save models
        model_path = os.path.join(settings.BASE_DIR, 'model')
        joblib.dump(model_total, os.path.join(model_path, 'grade_predictor.joblib'))  # Your original model
        joblib.dump(model_assignments, os.path.join(model_path, 'assignments_predictor.joblib'))
        joblib.dump(model_tutorial, os.path.join(model_path, 'tutorial_predictor.joblib'))
        joblib.dump(model_final, os.path.join(model_path, 'final_predictor.joblib'))
        
        # Print results
        self.stdout.write(self.style.SUCCESS(
            f"\nSuccess! Models trained with {len(df)} samples."
            f"\nTotal Score R²: {model_total.score(X_total, y_total):.2f}"
            f"\nAssignments R²: {model_assignments.score(X_components, y_assignments):.2f}"
            f"\nTutorial R²: {model_tutorial.score(X_components, y_tutorial):.2f}"
            f"\nFinal Exam R²: {model_final.score(X_components, y_final):.2f}"
        ))