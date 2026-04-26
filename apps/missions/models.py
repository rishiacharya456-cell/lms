from django.db import models
from django.contrib.auth import get_user_model
from apps.syllabus.models import Topic

User = get_user_model()


class Mission(models.Model):

    MISSION_TYPE = (
        ("bug", "Fix Bug"),
        ("fill", "Fill Code"),
        ("output", "Output"),
        ("normal", "Write Code"),
    )

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="missions")
    allow_for_trainee = models.BooleanField(default=False)

    # 🎮 GAME INFO
    title = models.CharField(max_length=200)
    story = models.TextField()  # shown to students (game style)

    mission_type = models.CharField(max_length=10, choices=MISSION_TYPE)

    # 🧠 RAW CODING DATA (ADMIN SIDE)
    starter_code = models.TextField(blank=True)
    correct_answer = models.TextField()

    # 🎯 OPTIONAL (for better UX)
    hint = models.TextField(blank=True)
    explanation = models.TextField(blank=True)

    # 🏆 GAME REWARD
    xp = models.IntegerField(default=10)

    # 🔓 CONTROL
    order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
    
    
    
    
class MissionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    attempts = models.IntegerField(default=0)
    
    
    
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="player")

    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user} | L{self.level} ({self.xp} XP)"



class MissionUnlock(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE)

    is_unlocked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.school} - {self.mission}"
    
    
    
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class MissionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey("Mission", on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.mission}"