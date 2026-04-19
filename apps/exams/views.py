from django.shortcuts import render, redirect
from apps.courses.models import CourseRegistration
from .models import ExamRegistration


def exam_registration(request):
    student = request.user
    school = student.school

    # 🔥 Approved courses only
    approved_courses = CourseRegistration.objects.filter(
        student=student,
        school=school,
        status='approved'
    ).select_related('course')

    # 🔥 Total fee
    total_amount = sum(reg.course.exam_fee for reg in approved_courses)

    # 🔥 Check if already submitted
    existing = ExamRegistration.objects.filter(
        student=student,
        school=school
    ).first()

    # =====================================================
    # 🔥 HANDLE PAYMENT SUBMISSION (QR FLOW)
    # =====================================================
    if request.method == "POST" and not existing:

        receipt = request.FILES.get('receipt')
        remarks = request.POST.get('remarks')

        for reg in approved_courses:
            ExamRegistration.objects.create(
                student=student,
                school=school,
                course=reg.course,
                amount=reg.course.exam_fee,
                is_paid=True,          # student submitted payment
                is_verified=False,     # admin will verify
                receipt=receipt,
                remarks=remarks
            )

        # 🔁 reload page to update UI state
        return redirect('exam_registration')

    # =====================================================
    # CONTEXT
    # =====================================================
    return render(request, 'exams/exam_registration.html', {
        "student": student,
        "approved_courses": approved_courses,
        "total_amount": total_amount,
        "existing": existing   # 🔥 VERY IMPORTANT
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ExamRegistration


# 🔥 SUPER ADMIN PAYMENT DASHBOARD
def admin_payments(request):

    payments = ExamRegistration.objects.select_related(
        'student', 'course', 'school'
    ).order_by('-created_at')

    return render(request, 'exams/admin_payments.html', {
        'payments': payments
    })


# 🔥 APPROVE PAYMENT
def approve_payment(request, id):

    reg = get_object_or_404(ExamRegistration, id=id)

    # prevent double approve
    if reg.status == 'approved':
        messages.info(request, "Already approved")
        return redirect('admin_payments')

    reg.is_verified = True
    reg.status = 'approved'
    reg.save()

    messages.success(request, "Payment approved successfully")

    return redirect('admin_payments')


# 🔥 REJECT PAYMENT
def reject_payment(request, id):

    reg = get_object_or_404(ExamRegistration, id=id)

    reg.status = 'rejected'
    reg.is_verified = False
    reg.save()

    messages.warning(request, "Payment rejected")

    return redirect('admin_payments')


# 🔥 SET EXAM DATE
def set_exam_date(request, id):

    reg = get_object_or_404(ExamRegistration, id=id)

    if request.method == "POST":

        exam_date = request.POST.get('exam_date')

        if not exam_date:
            messages.error(request, "Please select a valid date")
            return redirect('admin_payments')

        reg.exam_date = exam_date
        reg.save()

        messages.success(request, "Exam date updated")

    return redirect('admin_payments')


# 🔥 GENERATE HALL TICKET (CLASS-WISE)
def generate_hall_ticket(request):

    selected_class = request.GET.get('class')

    regs = ExamRegistration.objects.filter(
        status='approved',
        is_verified=True
    ).select_related('student', 'course', 'school')

    # 🔥 filter by class
    if selected_class:
        regs = regs.filter(student__student_class=str(selected_class))

    # 🔥 unique class list
    classes = (
        ExamRegistration.objects
        .filter(status='approved', is_verified=True)
        .values_list('student__student_class', flat=True)
        .distinct()
    )

    return render(request, 'exams/hall_ticket.html', {
        'registrations': regs,
        'classes': classes,
        'selected_class': selected_class
    })
    
    
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ExamRegistration


def admin_exam_dashboard(request):

    # 🔥 fetch all exam registrations
    exams = ExamRegistration.objects.select_related(
        'student', 'course', 'school'
    ).order_by('-created_at')

    # 🔥 filters (optional but useful)
    status_filter = request.GET.get('status')
    class_filter = request.GET.get('class')

    if status_filter:
        exams = exams.filter(status=status_filter)

    if class_filter:
        exams = exams.filter(student__student_class=class_filter)

    # 🔥 class list for filter UI
    classes = (
        ExamRegistration.objects
        .values_list('student__student_class', flat=True)
        .distinct()
    )

    context = {
        "exams": exams,
        "classes": classes,
        "selected_status": status_filter,
        "selected_class": class_filter,
    }

    return render(request, 'exams/admin_exam_dashboard.html', context)



from django.shortcuts import render
from apps.accounts.models import User
from .models import ExamRegistration


def school_exam_dashboard(request):

    school = request.user.school
    selected_class = request.GET.get('class')

    # 🔥 all students of school
    students = User.objects.filter(
        role='student',
        school=school
    )

    if selected_class:
        students = students.filter(student_class=selected_class)

    # 🔥 classes list
    classes = User.objects.filter(
        role='student',
        school=school
    ).values_list('student_class', flat=True).distinct()

    # 🔥 exam registrations (approved only)
    exam_regs = ExamRegistration.objects.filter(
        school=school,
        is_verified=True,
        status='approved'
    ).select_related('student', 'course')

    # 🔥 map student → payment status
    reg_map = {}
    for reg in exam_regs:
        reg_map.setdefault(reg.student_id, []).append(reg)

    return render(request, 'exams/school_exam_dashboard.html', {
        "students": students,
        "classes": classes,
        "selected_class": selected_class,
        "reg_map": reg_map
    })
    
    
    
def student_hall_ticket(request, student_id):

    regs = ExamRegistration.objects.filter(
        student_id=student_id,
        status='approved',
        is_verified=True
    ).select_related('student', 'course')

    student = regs.first().student if regs else None

    return render(request, 'exams/hall_ticket_single.html', {
        "registrations": regs,
        "student": student
    })
    
    
    
def print_all_hall_tickets(request, class_name):

    regs = ExamRegistration.objects.filter(
        student__student_class=class_name,
        status='approved',
        is_verified=True
    ).select_related('student', 'course')

    return render(request, 'exams/hall_ticket_bulk.html', {
        "registrations": regs
    })
    
    
    
def student_hall_ticket(request, student_id):

    regs = ExamRegistration.objects.filter(
        student_id=student_id,
        status='approved',
        is_verified=True
    ).select_related('student', 'course')

    if not regs.exists():
        return redirect('school_exam_dashboard')

    student = regs.first().student

    return render(request, 'exams/hall_ticket_single.html', {
        "registrations": regs,
        "student": student
    })
    
    
    
def print_all_hall_tickets(request, class_name):

    regs = ExamRegistration.objects.filter(
        student__student_class=class_name,
        status='approved',
        is_verified=True
    ).select_related('student', 'course')

    return render(request, 'exams/hall_ticket_bulk.html', {
        "registrations": regs,
        "class_name": class_name
    })
    
