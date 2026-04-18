from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.schools.models import School


class User(AbstractUser):

    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('school_admin', 'School Admin'),
        ('trainer', 'Trainer'),
        ('student', 'Student'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    # =========================
    # COMMON
    # =========================
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # =========================
    # SCHOOL LINK (STUDENT + SCHOOL ADMIN)
    # =========================
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users'
    )

    # =========================
    # 🔥 NEW: TRAINER → ASSIGNED SCHOOL
    # =========================
    assigned_school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_trainers'
    )

    # =========================
    # STUDENT FIELDS
    # =========================
    student_photo = models.ImageField(upload_to='students/', null=True, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    student_class = models.CharField(max_length=50, blank=True)
    section = models.CharField(max_length=20, blank=True)
    is_active_student = models.BooleanField(default=True)

    # =========================
    # TRAINER FIELDS
    # =========================
    trainer_reg_no = models.CharField(max_length=50, unique=True, null=True, blank=True)

    trainer_photo = models.ImageField(upload_to='trainer/photos/', null=True, blank=True)
    document = models.FileField(upload_to='trainer/documents/', null=True, blank=True)

    qualification = models.CharField(max_length=255, blank=True)
    experience = models.CharField(max_length=255, blank=True)

    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    designation = models.CharField(max_length=100, default="Trainer")
    department = models.CharField(max_length=100, blank=True)

    is_active_trainer = models.BooleanField(default=True)

    # =========================
    # AUTO REG NO
    # =========================
    def save(self, *args, **kwargs):

        if self.role == 'trainer' and not self.trainer_reg_no:
            last = User.objects.filter(role='trainer').order_by('-id').first()

            if last and last.trainer_reg_no:
                num = int(last.trainer_reg_no.split('/')[-1]) + 1
            else:
                num = 1

            self.trainer_reg_no = f"NEXO/TR/{str(num).zfill(4)}"

        super().save(*args, **kwargs)

    # =========================
    # DISPLAY
    # =========================
    def __str__(self):
        if self.role == 'trainer':
            return f"{self.username} ({self.trainer_reg_no})"
        return f"{self.username} ({self.role})"