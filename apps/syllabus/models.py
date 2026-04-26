from django.db import models
from django.conf import settings
from apps.schools.models import School

from django.db import models
from django.conf import settings

# 🔥 Assuming you already have School model
from apps.accounts.models import School   # adjust if your path is different


# 📘 Syllabus (Class 6, 7, 8, 9, 10 per school)
class Syllabus(models.Model):

    # 🔥 LINK TO SCHOOL (IMPORTANT FIX)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="syllabus"
    )

    # Class name (6, 7, 8, etc.)
    class_name = models.CharField(max_length=10)

    # ✅ CONTROL: allow trainee to VIEW syllabus
    allow_for_trainee = models.BooleanField(default=True)

    # ✅ CONTROL: allow trainee to UPLOAD topics
    allow_edit_for_trainee = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.school.name} - Class {self.class_name}"

    class Meta:
        ordering = ['class_name']
        unique_together = ('school', 'class_name')  # 🔥 Prevent duplicates

    # 📦 Phase (Session)
class Phase(models.Model):
    syllabus = models.ForeignKey(
        Syllabus,
        on_delete=models.CASCADE,
        related_name="phases"
    )
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    # 🔥 ADD THIS
    allow_for_view = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# 📘 Topic (Lesson inside phase)
class Topic(models.Model):
    phase = models.ForeignKey(
        Phase,
        on_delete=models.CASCADE,
        related_name="topics"
    )

    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    # 📁 CONTENT
    file = models.FileField(upload_to='syllabus/files/', blank=True, null=True)
    image = models.ImageField(upload_to='syllabus/images/', blank=True, null=True)

    # ✅ CONTROL: who can see this topic
    allow_for_view = models.BooleanField(default=True)

    # ✅ TRACK: who uploaded this
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# 🔓 Unlock system (School-based control)
class TopicUnlock(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_unlocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('school', 'topic')

    def __str__(self):
        return f"{self.school} - {self.topic} - {'Unlocked' if self.is_unlocked else 'Locked'}"


# ✅ Student Progress
class Progress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user} - {self.topic} - {'Done' if self.completed else 'Pending'}"