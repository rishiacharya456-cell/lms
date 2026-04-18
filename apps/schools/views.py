from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from apps.accounts.models import User
from .models import School
import csv

from django.core.mail import send_mail
from django.conf import settings


# ===============================
# REGISTER SCHOOL
# ===============================
def register_school(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        username = request.POST.get('username')
        admin_email = request.POST.get('admin_email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register_school')

        if School.objects.filter(email=email).exists():
            messages.error(request, "School with this email already exists.")
            return redirect('register_school')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register_school')

        if User.objects.filter(email=admin_email).exists():
            messages.error(request, "Admin email already in use.")
            return redirect('register_school')

        school = School.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            status='pending'
        )

        if request.FILES.get('logo'):
            school.logo = request.FILES.get('logo')
            school.save()

        User.objects.create_user(
            username=username,
            email=admin_email,
            password=password,
            role='school_admin',
            school=school
        )

        messages.success(request, "✅ School registered successfully! Waiting for approval.")
        return redirect('register_school')

    return render(request, 'schools/register_school.html')


# ===============================
# APPROVE SCHOOL
# ===============================
def approve_school(request, pk):
    school = get_object_or_404(School, pk=pk)
    school.status = 'approved'
    school.save()

    send_mail(
        subject="🎉 School Approved - Nexolabs Academy",
        message=f"""
Hello {school.name},

Your school has been approved successfully.

Login:
http://127.0.0.1:8000/login/school_admin/

Nexolabs Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[school.email],
        fail_silently=True,
    )

    messages.success(request, f"{school.name} approved and email sent!")
    return redirect('super_admin')


# ===============================
# REJECT SCHOOL
# ===============================
def reject_school(request, pk):
    school = get_object_or_404(School, pk=pk)

    if request.method == "POST":
        reason = request.POST.get('reason')

        school.status = 'rejected'
        school.save()

        send_mail(
            subject="❌ School Registration Rejected",
            message=f"""
Hello {school.name},

Your school registration was rejected.

Reason:
{reason}

Nexolabs Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[school.email],
            fail_silently=True,
        )

        messages.error(request, f"{school.name} rejected and email sent.")
        return redirect('super_admin')

    return render(request, 'schools/reject_reason.html', {'school': school})


# ===============================
# ADD SCHOOL
# ===============================
def add_school(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        username = request.POST.get('username')
        admin_email = request.POST.get('admin_email')
        password = request.POST.get('password')

        if School.objects.filter(email=email).exists():
            messages.error(request, "School email already exists")
            return redirect('add_school')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('add_school')

        school = School.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            status='approved'
        )

        User.objects.create_user(
            username=username,
            email=admin_email,
            password=password,
            role='school_admin',
            school=school
        )

        messages.success(request, "School added successfully!")
        return redirect('super_admin')

    return render(request, 'schools/add_school.html')


# ===============================
# EDIT SCHOOL
# ===============================
def edit_school(request, pk):
    school = get_object_or_404(School, pk=pk)

    if request.method == "POST":
        school.name = request.POST.get('name')
        school.email = request.POST.get('email')
        school.phone = request.POST.get('phone')
        school.address = request.POST.get('address')
        school.save()

        messages.success(request, "School updated successfully!")
        return redirect('super_admin')

    return render(request, 'schools/edit_school.html', {'school': school})


# ===============================
# DELETE SCHOOL
# ===============================
def delete_school(request, pk):
    school = get_object_or_404(School, pk=pk)
    school.delete()

    messages.success(request, "School deleted successfully!")
    return redirect('super_admin')


from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from apps.accounts.models import User
from apps.schools.models import School
from apps.courses.models import CourseRegistration


def school_detail(request, id):

    school = get_object_or_404(School, id=id)

    selected_class = request.GET.get('class')
    selected_section = request.GET.get('section')
    selected_student = request.GET.get('student')   # 🔥 NEW

    # 🔥 BASE STUDENTS
    students = User.objects.filter(
        role='student',
        school=school
    )

    # 🔥 CLASS FILTER
    if selected_class:
        students = students.filter(student_class=str(selected_class))

    # 🔥 SECTION FILTER
    if selected_section:
        students = students.filter(section=selected_section)

    # 🔥 CLASSES
    classes = User.objects.filter(
        role='student',
        school=school
    ).values_list('student_class', flat=True).distinct()

    # 🔥 SECTIONS (based on filtered students)
    sections = students.values_list('section', flat=True).distinct()

    # 🔥 TRAINERS
    trainers = User.objects.filter(
        role='trainer',
        assigned_school=school
    )

    # 🔥 PAGINATION
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    students_page = paginator.get_page(page_number)

    # =====================================================
    # 🔥 NEW: CLASS SUMMARY
    # =====================================================
    class_summary = []

    for cls in classes:
        total = User.objects.filter(
            role='student',
            school=school,
            student_class=cls
        ).count()

        registered = CourseRegistration.objects.filter(
            school=school,
            student__student_class=cls
        ).count()

        class_summary.append({
            'class': cls,
            'total': total,
            'registered': registered,
            'not_registered': total - registered
        })

    # =====================================================
    # 🔥 NEW: STUDENT MARKS
    # =====================================================
    student_regs = None

    if selected_student:
        student_regs = CourseRegistration.objects.filter(
            student_id=selected_student,
            school=school,
            status='approved'   # IMPORTANT
        ).select_related('course')

    # =====================================================
    # CONTEXT
    # =====================================================
    context = {
        "school": school,
        "classes": classes,
        "sections": sections,
        "students": students_page,
        "trainers": trainers,
        "selected_class": selected_class,
        "selected_section": selected_section,

        # 🔥 NEW
        "class_summary": class_summary,
        "selected_student": selected_student,
        "student_regs": student_regs,
    }

    return render(request, 'attendences/super_admin/school_detail.html', context)


# ===============================
# EXPORT CSV
# ===============================
def export_schools_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="schools.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Status'])

    for s in School.objects.all():
        writer.writerow([s.name, s.email, s.phone, s.status])

    return response


# ===============================
# EXPORT EXCEL
# ===============================
def export_schools_excel(request):

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="schools.xls"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Status'])

    for s in School.objects.all():
        writer.writerow([s.name, s.email, s.phone, s.status])

    return response