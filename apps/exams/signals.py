from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.courses.models import CourseRegistration
from .models import Exam

@receiver(post_save, sender=CourseRegistration)
def create_exam(sender, instance, **kwargs):

    if instance.status == 'approved':
        if not hasattr(instance, 'exam'):
            Exam.objects.create(
                registration=instance,
                student_name=instance.student.get_full_name(),
                reg_no=str(instance.student.id),
                course_name=instance.course.name,
                exam_fee=instance.course.exam_fee,
                class_name=instance.course.class_name,
                section=instance.course.section
            )