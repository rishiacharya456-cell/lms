from django.shortcuts import render, redirect
from apps.courses.models import Course
from apps.schools.models import School
from apps.courses.models import CourseAssignment, CourseRegistration
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Course


def create_course(request):
    if request.method == 'POST':
        try:
            # 🔹 Get & clean data
            name = request.POST.get('name')
            description = request.POST.get('description')
            class_name = request.POST.get('class_name')

            exam_fee = float(request.POST.get('exam_fee') or 0)
            credit_hour = int(request.POST.get('credit_hour') or 0)

            full_marks = int(request.POST.get('full_marks') or 0)
            pass_marks = int(request.POST.get('pass_marks') or 0)
            theory_marks = int(request.POST.get('theory_marks') or 0)
            internal_marks = int(request.POST.get('internal_marks') or 0)

            # 🔴 BASIC VALIDATION
            if not name:
                messages.error(request, "Course name is required")
                return redirect('create_course')

            if full_marks and (theory_marks + internal_marks != full_marks):
                messages.error(request, "Theory + Internal must equal Full Marks")
                return redirect('create_course')

            if pass_marks > full_marks:
                messages.error(request, "Pass marks cannot be greater than full marks")
                return redirect('create_course')

            # ✅ CREATE COURSE
            Course.objects.create(
                name=name,
                description=description,
                exam_fee=exam_fee,
                class_name=class_name,

                credit_hour=credit_hour,
                full_marks=full_marks,
                pass_marks=pass_marks,
                theory_marks=theory_marks,
                internal_marks=internal_marks,

                created_by=request.user
            )

            messages.success(request, "Course created successfully")
            return redirect('course_list')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('create_course')

    return render(request, 'courses/create_course.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Course, CourseAssignment
from apps.schools.models import School


def assign_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    schools = School.objects.all()

    # ✅ HANDLE ASSIGN (GET BASED)
    school_id = request.GET.get('school_id')

    if school_id:
        assignment, created = CourseAssignment.objects.get_or_create(
            course=course,
            school_id=school_id
        )

        if created:
            messages.success(request, "Course assigned successfully")
        else:
            messages.info(request, "Already assigned to this school")

        return redirect('assign_course', course_id=course.id)

    # ✅ GET ASSIGNED SCHOOLS
    assigned = CourseAssignment.objects.filter(course=course)
    assigned_school_ids = assigned.values_list('school_id', flat=True)

    return render(request, 'courses/assign_course.html', {
        'course': course,
        'schools': schools,
        'assigned_school_ids': assigned_school_ids
    })

from django.shortcuts import render
from .models import CourseAssignment

from .models import CourseAssignment, CourseRegistration

def school_courses(request):
    school = request.user.school

    assignments = CourseAssignment.objects.filter(
        school=school
    ).select_related('course')

    # group by class
    class_groups = {}
    for a in assignments:
        cls = a.course.class_name or "Other"
        class_groups.setdefault(cls, []).append(a)

    # 🔥 get registrations
    registrations = CourseRegistration.objects.filter(
        school=school
    ).select_related('student', 'course')

    return render(request, 'courses/school_courses.html', {
        'class_groups': class_groups,
        'registrations': registrations
    })


def toggle_course(request, assignment_id):
    assignment = CourseAssignment.objects.get(id=assignment_id)
    assignment.is_visible = not assignment.is_visible
    assignment.save()
    return redirect('school_courses')


from django.shortcuts import render, redirect
from .models import CourseAssignment, CourseRegistration

def student_courses(request):
    student = request.user

    # 🔥 GET APPROVED COURSES
    approved_courses = CourseRegistration.objects.filter(
        student=student,
        status='approved'
    ).select_related('course')

    # 👉 IF APPROVED → SHOW INTERNAL MARKS UI
    if approved_courses.exists():
        return render(request, 'courses/student_courses.html', {
            'approved_courses': approved_courses
        })

    # ❗ ELSE → SHOW NORMAL REGISTRATION
    assignments = CourseAssignment.objects.filter(
        school=student.school,
        is_visible=True,
        course__class_name=student.student_class
    ).select_related('course')

    registered_ids = CourseRegistration.objects.filter(
        student=student
    ).values_list('course_id', flat=True)

    return render(request, 'courses/student_courses.html', {
        'assignments': assignments,
        'registered_ids': registered_ids
    })
from django.shortcuts import redirect
from .models import CourseRegistration


def register_course(request, course_id):
    student = request.user
    school = student.school

    # 🔒 prevent duplicate / modification
    exists = CourseRegistration.objects.filter(
        student=student,
        course_id=course_id
    ).exists()

    if not exists:
        CourseRegistration.objects.create(
            student=student,
            course_id=course_id,
            school=school
        )

    return redirect('student_courses')



def approve_registrations(request):
    regs = CourseRegistration.objects.filter(
        school=request.user.school,
        status='pending'
    )

    return render(request, 'courses/approve.html', {'regs': regs})


def approve_student(request, reg_id):
    reg = CourseRegistration.objects.get(id=reg_id)
    reg.status = 'approved'
    reg.save()   # 🔥 triggers exam creation

    return redirect('approve_registrations')



# apps/courses/views.py

from django.shortcuts import render
from .models import Course

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})



from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Course

def course_list(request):
    selected_class = request.GET.get('class')

    courses = Course.objects.all()

    # ✅ FILTER
    if selected_class:
        courses = courses.filter(class_name=selected_class)

    # ✅ ONLY SHOW CLASSES THAT EXIST
    classes = (
        Course.objects.exclude(class_name__isnull=True)
        .exclude(class_name__exact="")
        .values_list('class_name', flat=True)
        .distinct()
    )

    # ✅ PAGINATION
    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'courses/course_list.html', {
        'page_obj': page_obj,
        'classes': classes,
        'selected_class': selected_class
    })
    
    
    
from django.shortcuts import get_object_or_404, redirect
from .models import Course

def delete_course(request, id):
    course = get_object_or_404(Course, id=id)
    course.delete()
    return redirect('course_list')


def reject_student(request, reg_id):
    reg = CourseRegistration.objects.get(id=reg_id)
    reg.status = 'rejected'
    reg.save()
    return redirect('school_courses')



def approve_student(request, reg_id):
    reg = CourseRegistration.objects.get(id=reg_id)
    reg.status = 'approved'
    reg.save()

    return redirect(request.META.get('HTTP_REFERER', 'school_courses'))



def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)

    return render(request, 'courses/course_detail.html', {
        'course': course
    })
    
    
    
    
# apps/courses/views.py

from django.shortcuts import render, redirect
from .models import CourseRegistration


def trainee_internal_marks(request):
    selected_class = request.GET.get('class')

    # 🔥 DON'T TRUST trainee.school (FIX)
    registrations = CourseRegistration.objects.select_related(
        'student', 'course', 'school'
    )

    # 🔥 FILTER BY CLASS IF SELECTED
    if selected_class:
        registrations = registrations.filter(
            student__student_class=str(selected_class)
        )

    # 🔥 GET CLASSES FROM DATA
    classes = CourseRegistration.objects.values_list(
        'student__student_class', flat=True
    ).distinct()

    return render(request, 'courses/trainee_marks.html', {
        'registrations': registrations,
        'classes': classes,
        'selected_class': selected_class
    })
    
    
from django.contrib import messages

def save_internal_marks(request, reg_id):
    reg = CourseRegistration.objects.get(id=reg_id)

    if request.method == "POST":
        reg.internal_obtained = request.POST.get('marks') or 0
        reg.save()

        messages.success(request, "Marks saved successfully")

    return redirect(request.META.get('HTTP_REFERER', 'trainee_marks'))



from apps.courses.models import CourseRegistration

def school_internal_marks(request):
    school = request.user.school

    selected_class = request.GET.get('class')
    selected_section = request.GET.get('section')

    # 🔥 base query (ONLY this school)
    registrations = CourseRegistration.objects.filter(
        school=school,
        status='approved'
    ).select_related('student', 'course')

    # 🔥 class filter
    if selected_class:
        registrations = registrations.filter(
            student__student_class=str(selected_class)
        )

    # 🔥 section filter
    if selected_section:
        registrations = registrations.filter(
            student__section=selected_section
        )

    # 🔥 get distinct class + section
    classes = CourseRegistration.objects.filter(
        school=school
    ).values_list('student__student_class', flat=True).distinct()

    sections = CourseRegistration.objects.filter(
        school=school
    ).values_list('student__section', flat=True).distinct()

    return render(request, 'courses/school_internal_marks.html', {
        'registrations': registrations,
        'classes': classes,
        'sections': sections,
        'selected_class': selected_class,
        'selected_section': selected_section,
    })
    
    
    
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import CourseRegistration


def admin_update_marks(request, reg_id):
    reg = get_object_or_404(CourseRegistration, id=reg_id)

    if request.method == "POST":
        marks = request.POST.get("marks")

        try:
            marks = int(marks)
        except:
            marks = 0

        # 🔥 validation (VERY IMPORTANT)
        if marks > reg.course.internal_marks:
            messages.error(request, "Marks cannot exceed full marks")
        else:
            reg.internal_obtained = marks
            reg.save()
            messages.success(request, "Marks updated successfully")

    # 🔁 redirect back to same page (preserve filters)
    return redirect(request.META.get('HTTP_REFERER', '/'))