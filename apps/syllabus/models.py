from django.db import models
from django.conf import settings
from apps.schools.models import School


# 📘 Syllabus (Class 6, 7, 8, 9, 10)
class Syllabus(models.Model):
    class_name = models.CharField(max_length=10)

    def __str__(self):
        return f"Class {self.class_name}"


# 📦 Phase (Session)
class Phase(models.Model):
    syllabus = models.ForeignKey(
        Syllabus,
        on_delete=models.CASCADE,
        related_name="phases"
    )
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

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

    file = models.FileField(upload_to='syllabus/files/', blank=True, null=True)
    image = models.ImageField(upload_to='syllabus/images/', blank=True, null=True)

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
        settings.AUTH_USER_MODEL,   # ✅ FIXED
        on_delete=models.CASCADE
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user} - {self.topic} - {'Done' if self.completed else 'Pending'}"