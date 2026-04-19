from django.db import models
from apps.accounts.models import User
from apps.schools.models import School
from apps.courses.models import Course


class ExamRegistration(models.Model):

    # 🔗 RELATIONS
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exam_registrations'
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='exam_registrations'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='exam_registrations'
    )

    # 💰 PAYMENT DETAILS
    amount = models.IntegerField(default=0)

    is_paid = models.BooleanField(default=False)        # student submitted payment
    is_verified = models.BooleanField(default=False)    # super admin verified

    # 📊 STATUS (NEW)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # 🧾 PAYMENT PROOF
    receipt = models.ImageField(
        upload_to='receipts/',
        null=True,
        blank=True
    )

    remarks = models.CharField(
        max_length=255,
        blank=True,
        help_text="Student should enter Name - RegNo - School"
    )

    # 📅 EXAM DETAILS (NEW)
    exam_date = models.DateField(
        null=True,
        blank=True
    )

    # 📅 TIMESTAMP
    created_at = models.DateTimeField(auto_now_add=True)

    # 🧠 DISPLAY
    def __str__(self):
        return f"{self.student.username} - {self.course.name}"

    # 🔒 PREVENT DUPLICATE REGISTRATION
    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-created_at']