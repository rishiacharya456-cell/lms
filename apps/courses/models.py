from django.db import models
from apps.accounts.models import User
from apps.schools.models import School


class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('hidden', 'Hidden'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # 💰 Fee
    exam_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    # 🎓 Class (MAIN FILTER FIELD)
    class_name = models.CharField(max_length=50, blank=True, null=True)

    # 📊 Academic Fields
    credit_hour = models.IntegerField(default=0)

    # 📊 Marks
    full_marks = models.IntegerField(default=100)
    pass_marks = models.IntegerField(default=40)

    # 🔥 NEW (IMPORTANT)
    theory_marks = models.IntegerField(default=70)
    internal_marks = models.IntegerField(default=30)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    schools = models.ManyToManyField(
        School,
        through='CourseAssignment',
        related_name='courses'
    )

    def __str__(self):
        return self.name

    # ✅ VALIDATION (VERY IMPORTANT)
    def save(self, *args, **kwargs):
        if self.theory_marks + self.internal_marks != self.full_marks:
            raise ValueError("Theory + Internal must equal Full Marks")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


# ------------------------------------

class CourseAssignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='course_assignments'
    )

    is_visible = models.BooleanField(default=False)

    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course} → {self.school}"

    class Meta:
        unique_together = ('course', 'school')


# ------------------------------------
from django.db import models
from apps.accounts.models import User
from apps.schools.models import School


class CourseRegistration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_registrations'
    )

    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='student_registrations'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # 🔥 NEW: marks fields
    internal_obtained = models.PositiveIntegerField(default=0)
    theory_obtained = models.PositiveIntegerField(default=0)

    # 🔥 OPTIONAL: auto total (good for future)
    def total_obtained(self):
        return self.internal_obtained + self.theory_obtained

    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course}"

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-registered_at']