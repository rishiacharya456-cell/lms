from django.db import models


class School(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # =========================
    # BASIC INFO
    # =========================
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    student_count = models.IntegerField(null=True, blank=True)
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)

    # =========================
    # STATUS
    # =========================
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)

    # =========================
    # 🔥 ATTENDANCE CONTROL (IMPORTANT)
    # =========================

    # 🔒 Lock attendance (super admin can unlock)
    attendance_locked = models.BooleanField(default=False)

    # 👨‍🏫 Allow trainee to edit attendance
    trainer_can_edit = models.BooleanField(default=False)

    # 🏫 Allow school admin to edit attendance
    school_can_edit = models.BooleanField(default=False)

    # 📊 Cached attendance percentage (optional optimization)
    attendance_percentage = models.FloatField(default=0)

    # =========================
    # META
    # =========================
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# SECTION MODEL
# =========================
class Section(models.Model):
    name = models.CharField(max_length=50)
    school = models.ForeignKey('School', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.school.name})"