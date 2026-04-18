from django.db import models
from django.db import models
from apps.schools.models import School
from apps.accounts.models import User


# 🔥 1. Attendance Session (One day per school)
class AttendanceSession(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    date = models.DateField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_locked = models.BooleanField(default=False)  # 🔒 Trainer cannot edit after submit

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['school', 'date']  # ❗ Prevent duplicate attendance per day
        ordering = ['-date']

    def __str__(self):
        return f"{self.school.name} - {self.date}"


# 🔥 2. Attendance Record (Per student per day)
class AttendanceRecord(models.Model):

    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records'
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['session', 'student']  # ❗ one record per student per day

    def __str__(self):
        return f"{self.student.username} - {self.status}"


# 🔥 3. Attendance Summary (OPTIONAL but powerful)
# (Used for fast percentage calculation)
class AttendanceSummary(models.Model):
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )

    total_classes = models.IntegerField(default=0)
    attended_classes = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    def calculate_percentage(self):
        if self.total_classes == 0:
            self.percentage = 0
        else:
            self.percentage = (self.attended_classes / self.total_classes) * 100

        self.save()

    def __str__(self):
        return f"{self.student.username} - {self.percentage:.2f}%"
    
    
    
    from django.db import models
from apps.accounts.models import User
from apps.schools.models import School


class Attendance(models.Model):

    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE
    )

    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='taken_attendance'
    )

    student_class = models.CharField(max_length=50)
    section = models.CharField(max_length=20)

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 PREVENT DUPLICATE
    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"