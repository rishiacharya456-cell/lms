from django.shortcuts import render
from apps.exams.models import Exam


def student_exams(request):
    exams = Exam.objects.filter(registration__student=request.user)
    return render(request, 'exams/student_exams.html', {'exams': exams})