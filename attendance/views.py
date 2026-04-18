from django.shortcuts import render
from django.shortcuts import render
from attendance.models import AttendanceSession

def attendance_list(request):
    if request.user.role != 'super_admin':
        return redirect('login')

    sessions = AttendanceSession.objects.all().order_by('-date')

    return render(request, 'attendance/super_admin/list.html', {
        'sessions': sessions
    })
    
    
    
    
from django.shortcuts import render, get_object_or_404, redirect
from attendance.models import AttendanceSession

def attendance_detail(request, session_id):
    if request.user.role != 'super_admin':
        return redirect('login')

    session = get_object_or_404(AttendanceSession, id=session_id)
    records = session.records.all()

    return render(request, 'attendance/super_admin/detail.html', {
        'session': session,
        'records': records
    })
    
    
    
    
from django.shortcuts import redirect, get_object_or_404
from attendance.models import AttendanceSession

def unlock_attendance(request, session_id):
    if request.user.role != 'super_admin':
        return redirect('login')

    session = get_object_or_404(AttendanceSession, id=session_id)

    session.is_locked = False
    session.save()

    return redirect('attendance_detail', session_id=session.id)



def edit_attendance(request, id):

    record = Attendance.objects.get(id=id)

    # 🔒 ONLY SCHOOL ADMIN + PERMISSION
    if request.user.role != 'school_admin':
        return redirect('login')

    if not request.user.school.allow_attendance_edit:
        return redirect('school_attendance')

    if request.method == 'POST':
        record.status = request.POST.get('status')
        record.save()

    return redirect('school_attendance')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from apps.accounts.models import User
from .models import Attendance


@login_required(login_url='/login/')
def take_attendance(request):

    # 🔒 ONLY TRAINER
    if request.user.role != 'trainer':
        return redirect('/login/')

    trainer = request.user
    school = trainer.assigned_school

    # 🔒 NO SCHOOL
    if not school:
        return render(request, 'attendance/no_school.html')

    today = date.today()

    # 🔥 FILTERS
    selected_class = request.GET.get('class') or request.POST.get('class')
    selected_section = request.GET.get('section') or request.POST.get('section')

    # 🔥 STUDENTS
    students = User.objects.filter(role='student', school=school)

    if selected_class:
        students = students.filter(student_class=selected_class)

    if selected_section:
        students = students.filter(section=selected_section)

    # 🔥 CLASSES
    classes = User.objects.filter(
        role='student',
        school=school
    ).values_list('student_class', flat=True).distinct()

    # 🔥 SECTIONS (BASED ON CLASS)
    if selected_class:
        sections = User.objects.filter(
            role='student',
            school=school,
            student_class=selected_class
        ).values_list('section', flat=True).distinct()
    else:
        sections = []

    # 🔥 HANDLE POST
    if request.method == 'POST':

        date_str = request.POST.get('date')
        selected_date = (
            datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str else today
        )

        existing_records = Attendance.objects.filter(
            school=school,
            trainer=trainer,
            date=selected_date,
            student_class=selected_class,
            section=selected_section
        )

        already_marked = existing_records.exists()

        # 🚫 NO CLASS
        if request.POST.get('no_class'):
            if not already_marked:
                Attendance.objects.create(
                    school=school,
                    trainer=trainer,
                    date=selected_date,
                    student_class=selected_class,
                    section=selected_section,
                    status="no_class"
                )
            return redirect('trainee_dashboard')

        # 🔒 GLOBAL LOCK CHECK (IMPORTANT)
        if school.attendance_locked and not school.trainer_can_edit:
            return redirect('trainee_dashboard')

        # 🔒 CLASS LOCK (ALLOW IF PERMISSION ON)
        if already_marked and not school.trainer_can_edit:
            return redirect('trainee_dashboard')

        # ✅ SAVE / UPDATE (EDIT MODE ENABLED)
        for student in students:
            status = request.POST.get(f'status_{student.id}')

            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={
                        "school": school,
                        "trainer": trainer,
                        "student_class": student.student_class,
                        "section": student.section,
                        "status": status
                    }
                )

        return redirect('trainee_dashboard')

    # 🔒 UI LOCK CHECK
    today_records = Attendance.objects.filter(
        school=school,
        trainer=trainer,
        date=today,
        student_class=selected_class,
        section=selected_section
    )

    # 🔥 IMPORTANT FIX HERE
    already_marked = today_records.exists() and not school.trainer_can_edit

    # 🔥 EXISTING DATA (FOR EDIT MODE)
    existing_attendance = {
        a.student_id: a.status
        for a in today_records if a.student
    }

    context = {
        "students": students if selected_class and selected_section else [],
        "classes": classes,
        "sections": sections,
        "selected_class": selected_class,
        "selected_section": selected_section,
        "today": today,

        # 🔥 IMPORTANT
        "already_marked": already_marked,
        "existing_attendance": existing_attendance,
        "school": school,   # ✅ REQUIRED FOR TEMPLATE
    }

    return render(request, 'attendences/take_attendance.html', context)



from datetime import datetime
from .models import Attendance

def student_attendance(request):

    if request.user.role != 'student':
        return redirect('login')

    student = request.user

    month = request.GET.get('month')

    records = Attendance.objects.filter(student=student)

    if month:
        records = records.filter(date__month=month)

    return render(request, 'attendance/student_report.html', {
        "records": records,
        "student": student
    })
    
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from django.urls import reverse
from apps.accounts.models import User
from attendance.models import Attendance


@login_required(login_url='/login/')
def school_attendance(request):

    # 🔒 ONLY SCHOOL ADMIN
    if request.user.role != 'school_admin':
        return redirect('/login/')

    school = request.user.school

    # 🔥 FILTERS
    selected_class = request.GET.get('class') or request.POST.get('class')
    selected_section = request.GET.get('section') or request.POST.get('section')

    # 🔥 BASE STUDENTS
    students = User.objects.filter(
        role='student',
        school=school
    )

    # 🔥 APPLY FILTERS
    if selected_class:
        students = students.filter(student_class=selected_class)

    if selected_section:
        students = students.filter(section=selected_section)

    # 🔥 CLASSES
    classes = User.objects.filter(
        role='student',
        school=school
    ).values_list('student_class', flat=True).distinct()

    # 🔥 SECTIONS (BASED ON CLASS)
    if selected_class:
        sections = User.objects.filter(
            role='student',
            school=school,
            student_class=selected_class
        ).values_list('section', flat=True).distinct()
    else:
        sections = []

    # 🔥 HANDLE EDIT SAVE
    if request.method == 'POST' and school.school_can_edit:

        date_str = request.POST.get('date')
        selected_date = (
            datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str else date.today()
        )

        for student in students:

            status = request.POST.get(f'status_{student.id}')

            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={
                        "school": school,
                        "student_class": student.student_class,
                        "section": student.section,
                        "status": status
                    }
                )

        # ✅ FIXED REDIRECT (NO ERROR)
        url = reverse('school_attendance')
        return redirect(f"{url}?class={selected_class or ''}&section={selected_section or ''}")

    # 🔥 REPORT DATA
    student_data = []

    for s in students:

        records = Attendance.objects.filter(
            student=s
        ).exclude(status='no_class')

        total = records.count()
        present = records.filter(status='present').count()
        absent = records.filter(status='absent').count()

        percentage = int((present / total) * 100) if total > 0 else 0

        # 🔥 GET LATEST DATE
        latest_record = records.order_by('-date').first()

        student_data.append({
            "student": s,
            "class": s.student_class,
            "section": s.section,
            "total": total,
            "present": present,
            "absent": absent,
            "percentage": percentage,
            "last_date": latest_record.date if latest_record else None
        })

    context = {
        "student_data": student_data,
        "students": students,
        "classes": classes,
        "sections": sections,
        "selected_class": selected_class,
        "selected_section": selected_section,
        "school": school,
    }

    return render(request, 'attendences/school_report.html', context)
    
    
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from apps.schools.models import School


def unlock_attendance(request, id):
    if request.method == 'POST':
        school = get_object_or_404(School, id=id)
        school.attendance_locked = False
        school.save()
        messages.success(request, f"{school.name} unlocked")
    return redirect('super_admin')


def lock_attendance(request, id):
    if request.method == 'POST':
        school = get_object_or_404(School, id=id)
        school.attendance_locked = True
        school.save()
        messages.success(request, f"{school.name} locked")
    return redirect('super_admin')


def toggle_trainer_permission(request, id):
    if request.method == 'POST':
        school = get_object_or_404(School, id=id)
        school.trainer_can_edit = not school.trainer_can_edit
        school.save()
    return redirect('super_admin')


def toggle_school_permission(request, id):
    if request.method == 'POST':
        school = get_object_or_404(School, id=id)
        school.school_can_edit = not school.school_can_edit
        school.save()
    return redirect('super_admin')



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.schools.models import School
from attendance.models import Attendance


@login_required
def attendance_management(request):

    schools = School.objects.all()

    for s in schools:

        total = Attendance.objects.filter(
            school=s
        ).exclude(status='no_class').count()

        present = Attendance.objects.filter(
            school=s,
            status='present'
        ).count()

        percentage = int((present / total) * 100) if total > 0 else 0

        # attach dynamically
        s.attendance_percentage = percentage

    return render(request, 'attendences/attendance_management.html', {
        "schools": schools
    })
    
    
    
    
@login_required
def admin_school_attendance(request, id):

    school = School.objects.get(id=id)

    selected_date = request.GET.get('date')

    if selected_date:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        selected_date = date.today()

    students = User.objects.filter(
        role='student',
        school=school
    )

    attendance = Attendance.objects.filter(
        school=school,
        date=selected_date
    )

    attendance_dict = {
        a.student_id: a.status
        for a in attendance if a.student
    }

    return render(request, 'attendance/admin_school_attendance.html', {
        "school": school,
        "students": students,
        "attendance": attendance_dict,
        "selected_date": selected_date,
    })
    
    
    
    
from django.http import HttpResponse
from openpyxl import Workbook
from apps.accounts.models import User
from attendance.models import Attendance


def export_attendance_excel(request):

    if request.user.role != 'school_admin':
        return redirect('/login/')

    school = request.user.school

    selected_class = request.GET.get('class')
    selected_section = request.GET.get('section')

    students = User.objects.filter(
        role='student',
        school=school
    )

    if selected_class:
        students = students.filter(student_class=selected_class)

    if selected_section:
        students = students.filter(section=selected_section)

    # 📊 CREATE EXCEL
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance Report"

    # 🔥 HEADERS
    ws.append([
        "Student Name",
        "Reg No",
        "Class",
        "Section",
        "Total Classes",
        "Present",
        "Absent",
        "Percentage"
    ])

    # 🔥 DATA
    for s in students:

        records = Attendance.objects.filter(
            student=s
        ).exclude(status='no_class')

        total = records.count()
        present = records.filter(status='present').count()
        absent = records.filter(status='absent').count()

        percentage = int((present / total) * 100) if total > 0 else 0

        ws.append([
            f"{s.first_name} {s.last_name}",
            s.username,
            s.student_class,
            s.section,
            total,
            present,
            absent,
            f"{percentage}%"
        ])

    # 📥 RESPONSE
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = f'attachment; filename=attendance_class_{selected_class}.xlsx'

    wb.save(response)
    return response



from django.contrib.auth.decorators import login_required
from attendance.models import Attendance

@login_required
def student_attendance(request):

    student = request.user
    school = student.school

    records = Attendance.objects.filter(
        student=student
    ).exclude(status='no_class').order_by('-date')

    total_classes = records.count()
    attended = records.filter(status='present').count()

    percentage = int((attended / total_classes) * 100) if total_classes > 0 else 0

    return render(request, 'attendences/student_attendance.html', {
        "student": student,
        "school": school,
        "records": records,
        "total_classes": total_classes,
        "attended": attended,
        "percentage": percentage
    })