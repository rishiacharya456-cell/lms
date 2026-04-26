from django.db import models
from django.conf import settings



User = settings.AUTH_USER_MODEL


# 🧱 QUIZ / ASSESSMENT
class Assessment(models.Model):
    TYPE_CHOICES = (
        ("quiz", "Quiz"),
        ("assignment", "Assignment"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    assessment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # 🎯 Targeting
    class_name = models.CharField(max_length=50, blank=True)
    section = models.CharField(max_length=50, blank=True)

    # ⏰ Timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    # 🚫 Anti-cheating
    tab_switch_limit = models.IntegerField(default=3)
    auto_submit_on_violation = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)



    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title


# 🧱 QUESTIONS
class Question(models.Model):
    TYPE_CHOICES = (
        ("mcq", "MCQ"),
        ("text", "Short Answer"),
    )

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="questions")

    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    marks = models.IntegerField(default=1)

    # ⏱ Per question timer
    time_limit_seconds = models.IntegerField(default=30)

    order = models.IntegerField(default=0)

    # For short answer (optional)
    correct_answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.assessment.title} - Q{self.order}"


# 🧱 OPTIONS (FOR MCQ)
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")

    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


# 🧱 STUDENT ATTEMPT
class Attempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    start_time = models.DateTimeField(auto_now_add=True)

    current_question = models.IntegerField(default=1)
    time_left = models.IntegerField(default=0)

    tab_switch_count = models.IntegerField(default=0)

    is_locked = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.assessment}"


# 🧱 ANSWERS
class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_option = models.ForeignKey(Option, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True, null=True)

    is_correct = models.BooleanField(default=False)
    marks_obtained = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.attempt.student} - Q{self.question.id}"