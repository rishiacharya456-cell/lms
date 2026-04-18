from django.db import models
from apps.schools.models import School

class Payment(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.school.name} - {self.amount}"