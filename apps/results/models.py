from django.db import models
from apps.accounts.models import User
from apps.schools.models import School
from apps.courses.models import Course
from apps.exams.models import ExamRegistration

from django.db import models
from apps.accounts.models import User
from apps.schools.models import School
from apps.courses.models import Course


class Result(models.Model):

    # 🔗 RELATIONS
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_results'   # ✅ FIX
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='school_results'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_results'
    )

    # 🔥 MARKS
    theory_marks = models.IntegerField(default=0)
    internal_marks = models.IntegerField(default=0)
    total = models.IntegerField(default=0)

    # 🔥 GRADE
    grade = models.CharField(max_length=2, blank=True)
    grade_point = models.FloatField(default=0)

    # 🔥 STATUS
    is_pass = models.BooleanField(default=False)

    # 🔥 WHO UPLOADED
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_results'   # ✅ FIX
    )

    # 🔒 LOCK AFTER PUBLISH
    is_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.name}"

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-created_at']
        
        
        
# apps/results/models.py

from django.db import models
from apps.schools.models import School


class ResultPublish(models.Model):
    school = models.OneToOneField(School, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.school.name} - {'Published' if self.is_published else 'Draft'}"