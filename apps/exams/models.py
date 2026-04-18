from django.db import models
from apps.courses.models import CourseRegistration

class Exam(models.Model):
    registration = models.OneToOneField(
        CourseRegistration,
        on_delete=models.CASCADE,
        related_name='exam'
    )

    student_name = models.CharField(max_length=255)
    reg_no = models.CharField(max_length=100)

    course_name = models.CharField(max_length=255)
    exam_fee = models.DecimalField(max_digits=8, decimal_places=2)

    class_name = models.CharField(max_length=50, blank=True, null=True)
    section = models.CharField(max_length=50, blank=True, null=True)

    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.course_name}"