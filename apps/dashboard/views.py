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

from apps.syllabus.models import Syllabus
from apps.syllabus.models import Syllabus

# =========================================
# 🔥 SCHOOL ADMIN DASHBOARD
# =========================================
@login_required
def school_admin_dashboard(request):

    school = request.user.school

    students_qs = User.objects.filter(role='student', school=school)

    # 🔥 TRY MATCH BY CLASS (IF EXISTS)
    school_class = str(getattr(school, 'assigned_class', '')).strip()

    syllabus = None

    if school_class:
        syllabus = Syllabus.objects.filter(
            class_name__icontains=school_class,
            allow_for_trainee=True
        ).first()

    # 🔥 FALLBACK (IMPORTANT — NEVER RETURN NONE)
    if not syllabus:
        syllabus = Syllabus.objects.filter(
            allow_for_trainee=True
        ).first()

    context = {
        "school": school,
        "students_count": students_qs.count(),

        "trainers_count": User.objects.filter(
            role='trainer',
            assigned_school=school
        ).count(),

        "courses_count": Course.objects.count(),
        "recent_students": students_qs.order_by('-id')[:5],

        # 🔥 ALWAYS NOT NONE NOW
        "syllabus": syllabus
    }

    return render(request, "dashboard/school_admin.html", context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.syllabus.models import Syllabus
from apps.missions.models import Mission


@login_required
def student_dashboard(request):

    user = request.user
    school = getattr(user, "school", None)

    syllabus = None
    missions = []

    if user.role == "student":

        student_class = str(getattr(user, "student_class", "")).strip()

        # 🔥 FLEXIBLE MATCH
        syllabus = Syllabus.objects.filter(
            class_name__icontains=student_class,
            allow_for_trainee=True
        ).first()

        # 🔥 FETCH ONLY UNLOCKED MISSIONS FOR THIS SCHOOL
        if school:
            missions = Mission.objects.filter(
                allow_for_trainee=True,
                is_active=True,
                missionunlock__school=school,
                missionunlock__is_unlocked=True
            ).distinct()

        # 🔍 DEBUG
        print("DEBUG → student_class:", student_class)
        print("DEBUG → syllabus found:", syllabus)
        print("DEBUG → missions count:", missions.count())

    context = {
        "student": user,
        "school": school,
        "syllabus": syllabus,
        "missions": missions,   # 🔥 IMPORTANT
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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Count
from datetime import date
from apps.accounts.models import User
from apps.schools.models import School
from attendance.models import Attendance
from apps.syllabus.models import Syllabus

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

    # ✅ NEW: SYLLABUS (IMPORTANT FIX)
    syllabus = None

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

        # ✅ NEW: AUTO GET SYLLABUS FROM FIRST CLASS
        first_class = classes[0] if classes else None

        if first_class:
            syllabus = Syllabus.objects.filter(class_name=first_class).first()

    context = {
        "trainer": trainer,
        "school": school,
        "classes": classes,
        "sections": sections,

        "attendance_today": attendance_today,
        "total_taken": total_taken,
        "daily": daily,

        "class_labels": class_labels,
        "class_data": class_data,
        "class_stats": class_stats,

        # ✅ IMPORTANT
        "syllabus": syllabus,
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



from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # your ready template