import random
import string
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_reg_no(school, student_class, section):

    # 🔥 SCHOOL CODE (first 3 letters)
    school_code = school.name[:3].upper()

    # 🔥 CLASS (only number)
    class_part = str(student_class)

    # 🔥 SECTION (first letter only)
    section_part = section[:1].upper()

    # 🔥 FILTER EXISTING STUDENTS SAME CLASS + SECTION
    students = User.objects.filter(
        school=school,
        role='student',
        student_class=student_class,
        section=section
    )

    count = students.count() + 1

    number_part = str(count).zfill(2)  # 01, 02

    return f"{school_code}{section_part}{class_part}{number_part}"