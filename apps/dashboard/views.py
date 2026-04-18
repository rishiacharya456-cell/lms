from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from apps.schools.models import School
from apps.courses.models import Course
from apps.payments.models import Payment

User = get_user_model()


# =========================================
# 🔥 SUPER ADMIN DASHBOARD
# =========================================
@login_required
def super_admin_dashboard(request):

    # 🔹 BASE QUERY (SCHOOLS)
    schools_qs = School.objects.all().order_by('-id')

    # 🔍 SEARCH
    search_query = request.GET.get('search')
    if search_query:
        schools_qs = schools_qs.filter(name__icontains=search_query)

    # 🎯 FILTER
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        schools_qs = schools_qs.filter(status=status_filter)

    # 🔥 FETCH TRAINEES
    trainees = User.objects.filter(role='trainer').order_by('-id')

    context = {
        # 📊 COUNTS
        "total_schools": School.objects.count(),
        "total_users": User.objects.count(),
        "total_courses": Course.objects.count(),
        "total_revenue": sum(p.amount for p in Payment.objects.all()),

        # 📊 STATUS COUNTS
        "pending_schools": School.objects.filter(status='pending').count(),
        "approved_schools": School.objects.filter(status='approved').count(),
        "rejected_schools": School.objects.filter(status='rejected').count(),

        # 📋 FILTERED DATA
        "schools": schools_qs,

        # 🆕 RECENT
        "recent_schools": School.objects.all().order_by('-id')[:5],

        # 🔥 TRAINEES (IMPORTANT FOR ASSIGN DROPDOWN)
        "trainees": trainees,
        "total_trainees": trainees.count(),

        # 🔁 KEEP FILTER VALUES
        "search_query": search_query,
        "status_filter": status_filter,
    }

    return render(request, "dashboard/super_admin.html", context)


# =========================================
# 🔥 SCHOOL ADMIN DASHBOARD
# =========================================
@login_required
def school_admin_dashboard(request):

    school = request.user.school

    students_qs = User.objects.filter(role='student', school=school)

    context = {
        "school": school,
        "students_count": students_qs.count(),

        # ⚠️ FIXED: trainers should come from assigned_school
        "trainers_count": User.objects.filter(
            role='trainer',
            assigned_school=school
        ).count(),

        "courses_count": Course.objects.count(),
        "recent_students": students_qs.order_by('-id')[:5],
    }

    return render(request, "dashboard/school_admin.html", context)


# =========================================
# 🔥 STUDENT DASHBOARD
# =========================================
@login_required
def student_dashboard(request):

    user = request.user

    context = {
        "student": user,
        "school": user.school,
    }

    return render(request, "dashboard/student.html", context)

# =========================================
# 🔥 TRAINEE DASHBOARD
# =========================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.accounts.models import User

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Count
from apps.accounts.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import date
from django.db.models import Count
from apps.accounts.models import User
from apps.schools.models import School
from attendance.models import Attendance


@login_required
def trainee_dashboard(request):

    # 🔒 ONLY TRAINER
    if request.user.role != 'trainer':
        return redirect('login')

    trainer = request.user
    school = trainer.assigned_school

    today = date.today()

    classes = []
    sections = []

    attendance_today = False
    total_taken = 0
    daily = []

    # 🔥 NEW DATA
    class_labels = []
    class_data = []
    class_stats = []

    if school:

        students = User.objects.filter(
            role='student',
            school=school
        )

        # 🎯 CLASSES
        classes = students.values_list(
            'student_class', flat=True
        ).distinct()

        # 🎯 SECTIONS
        sections = students.values_list(
            'section', flat=True
        ).distinct()

        # 🔥 TODAY STATUS
        attendance_today = Attendance.objects.filter(
            trainer=trainer,
            school=school,
            date=today
        ).exclude(status='no_class').exists()

        # 🔥 TOTAL RECORDS
        total_taken = Attendance.objects.filter(
            trainer=trainer,
            school=school
        ).count()

        # 🔥 DAILY CHART
        daily_qs = Attendance.objects.filter(
            trainer=trainer,
            school=school
        ).values('date').annotate(count=Count('id')).order_by('-date')[:7]

        daily = list(reversed(daily_qs))

        # 🔥 CLASS-WISE PIE + STATS
        for c in classes:

            present_count = Attendance.objects.filter(
                school=school,
                student_class=c,
                status='present'
            ).count()

            absent_count = Attendance.objects.filter(
                school=school,
                student_class=c,
                status='absent'
            ).count()

            total = present_count + absent_count

            percentage = int((present_count / total) * 100) if total > 0 else 0

            today_done = Attendance.objects.filter(
                school=school,
                student_class=c,
                date=today
            ).exists()

            # 🔥 PIE DATA
            class_labels.append(f"Class {c}")
            class_data.append(total)

            # 🔥 CARD DATA
            class_stats.append({
                "class": c,
                "present": present_count,
                "absent": absent_count,
                "total": total,
                "percentage": percentage,
                "today_done": today_done
            })

    context = {
        "trainer": trainer,
        "school": school,
        "classes": classes,
        "sections": sections,

        "attendance_today": attendance_today,
        "total_taken": total_taken,
        "daily": daily,

        # 🔥 NEW
        "class_labels": class_labels,
        "class_data": class_data,
        "class_stats": class_stats,
    }

    return render(request, 'dashboard/trainee_dashboard.html', context)


# =========================================
# 🔥 ASSIGN TRAINER TO SCHOOL
# =========================================
def assign_trainer_dashboard(request):

    if request.method == 'POST':
        school_id = request.POST.get('school_id')
        trainee_id = request.POST.get('trainee')

        school = School.objects.get(id=school_id)
        trainee = User.objects.get(id=trainee_id)

        trainee.assigned_school = school
        trainee.save()

    return redirect('super_admin')