from django.core.management.base import BaseCommand
from database.models import StudentScore
from django.db.models import Avg, Min, Max, Count, Q, F

class Command(BaseCommand):
    help = 'Validates training data structure for grade prediction model'

    def handle(self, *args, **options):
        self.stdout.write("=== Training Data Validation ===")
        
        # Check student records
        student_count = StudentScore.objects.values('student').distinct().count()
        self.stdout.write(f"Students with records: {student_count}")
        
        # Check semester progression (minimum 2 semesters needed for meaningful training)
        problematic_students = []
        for student in StudentScore.objects.values('student').distinct():
            semesters = StudentScore.objects.filter(
                student=student['student']
            ).values_list('semester', flat=True).distinct()
            
            if len(semesters) < 2:
                problematic_students.append(student['student'])
        
        if problematic_students:
            self.stdout.write(self.style.ERROR(
                f"{len(problematic_students)} students lack consecutive semesters:"
            ))
            for s in problematic_students[:5]:  # Show first 5 as examples
                self.stdout.write(f"- {s}")
        else:
            self.stdout.write(self.style.SUCCESS(
                "All students have multiple semesters"
            ))

        # Check score distribution using NEW total calculation (assignments + tutorial + final)
        stats = StudentScore.objects.annotate(
            calculated_total=F('assignments') + F('tutorial') + F('final')  # Excludes attendance
        ).aggregate(
            min_score=Min('calculated_total'),
            avg_score=Avg('calculated_total'),
            max_score=Max('calculated_total'),
            null_scores=Count('pk', filter=Q(
                Q(assignments__isnull=True) |
                Q(tutorial__isnull=True) |
                Q(final__isnull=True)
            ))
        )
        
        self.stdout.write("\nScore Statistics (assignments + tutorial + final):")
        self.stdout.write(f"Min: {stats['min_score']}")
        self.stdout.write(f"Avg: {stats['avg_score']:.2f}")
        self.stdout.write(f"Max: {stats['max_score']}")
        self.stdout.write(self.style.WARNING(
            f"Null scores: {stats['null_scores']}"
        ))

        # Final validation
        if student_count == 0:
            self.stdout.write(self.style.ERROR("CRITICAL: No student records found"))
        elif len(problematic_students) == student_count:
            self.stdout.write(self.style.ERROR("CRITICAL: No students have consecutive semester data"))
        elif stats['null_scores'] > 0:
            self.stdout.write(self.style.ERROR("WARNING: Null scores will break training"))
        else:
            self.stdout.write(self.style.SUCCESS("Data validation complete - ready for model training"))