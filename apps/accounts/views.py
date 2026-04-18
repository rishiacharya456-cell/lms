from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def role_login(request, role):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        # ❌ Invalid credentials
        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect('role_login', role=role)

        # ❌ Role mismatch
        if user.role != role:
            messages.error(request, "Invalid role selected")
            return redirect('role_login', role=role)

        # ==============================
        # 🔥 SCHOOL ADMIN CHECK
        # ==============================
        if role == 'school_admin':

            if not user.school:
                messages.error(request, "No school assigned to this account.")
                return redirect('role_login', role=role)

            if user.school.status == 'pending':
                messages.warning(request, "⏳ Your school is under approval.")
                return redirect('role_login', role=role)

            if user.school.status == 'rejected':
                messages.error(request, "❌ Your school request was rejected.")
                return redirect('role_login', role=role)

            if user.school.status != 'approved':
                messages.error(request, "Your school is not approved yet.")
                return redirect('role_login', role=role)

            if hasattr(user.school, 'is_active') and not user.school.is_active:
                messages.error(request, "🚫 Your school is suspended.")
                return redirect('role_login', role=role)

        # ==============================
        # 🔥 STUDENT CHECK
        # ==============================
        if role == 'student':

            if not user.school:
                messages.error(request, "No school assigned.")
                return redirect('role_login', role=role)

            if user.school.status != 'approved':
                messages.error(request, "Your school is not approved yet.")
                return redirect('role_login', role=role)

            if hasattr(user, 'is_active_student') and not user.is_active_student:
                messages.error(request, "Your account is inactive. Contact school.")
                return redirect('role_login', role=role)

        # ==============================
        # 🔥 TRAINER CHECK (NEW)
        # ==============================
        if role == 'trainer':

            if hasattr(user, 'is_active_trainer') and not user.is_active_trainer:
                messages.error(request, "Your trainer account is inactive.")
                return redirect('role_login', role=role)

        # ==============================
        # ✅ LOGIN USER
        # ==============================
        login(request, user)

        print("LOGIN SUCCESS:", user.username, user.role)

        # ==============================
        # 🔁 REDIRECT BASED ON ROLE
        # ==============================
        if role == 'super_admin':
            return redirect('super_admin')

        elif role == 'school_admin':
            return redirect('school_admin_dashboard')

        elif role == 'trainer':
            return redirect('trainee_dashboard')  # ✅ FIXED HERE

        elif role == 'student':
            return redirect('student_dashboard')

        return redirect('/login/')

    return render(request, 'accounts/login.html', {'role': role})



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .utils import generate_reg_no
from apps.schools.models import Section   # 🔥 IMPORTANT

User = get_user_model()


def add_student(request):

    school = request.user.school

    # 🔥 FETCH SECTIONS FOR DROPDOWN
    sections = Section.objects.filter(school=school)

    if request.method == "POST":

        student_class = request.POST.get('student_class')
        section = request.POST.get('section')

        reg_no = generate_reg_no(school, student_class, section)
        dob = request.POST.get('dob')

        section = request.POST.get('section')

        # 🔥 HANDLE NEW SECTION
        if section == "__new__":
            new_section = request.POST.get('new_section')

            if new_section:
                section_obj = Section.objects.create(
                    name=new_section,
                    school=school
                )
                section = section_obj.name
            else:
                messages.error(request, "Please enter section name")
                return redirect('add_student')

        # 🔥 CREATE STUDENT
        user = User.objects.create_user(
            username=reg_no,
            password=dob,  # DOB as password
            role='student',
            school=school,

            first_name=request.POST.get('name'),
            dob=dob,
            father_name=request.POST.get('father_name'),
            mother_name=request.POST.get('mother_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            student_class=request.POST.get('student_class'),
            section=section,
            is_active_student=True
        )

        # 🔥 HANDLE PHOTO
        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')
            user.save()

        messages.success(request, "Student added successfully!")

        return render(request, "accounts/student_slip.html", {
            "student": user
        })

    return render(request, "accounts/add_student.html", {
        "sections": sections   # 🔥 IMPORTANT
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def student_list(request):

    students = User.objects.filter(
        role='student',
        school=request.user.school
    ).order_by('-id')

    return render(request, 'accounts/student_list.html', {
        'students': students
    })
    
    
    
@login_required
def delete_student(request, id):
    student = User.objects.get(id=id, role='student')
    student.delete()
    return redirect('student_list')


@login_required
def edit_student(request, id):

    student = User.objects.get(id=id, role='student')

    if request.method == "POST":
        student.first_name = request.POST.get('name')
        student.student_class = request.POST.get('student_class')
        student.section = request.POST.get('section')
        student.phone = request.POST.get('phone')

        if request.FILES.get('photo'):
            student.photo = request.FILES.get('photo')

        student.save()
        return redirect('student_list')

    return render(request, 'accounts/edit_student.html', {
        'student': student
    })
from django.shortcuts import render, redirect
from apps.accounts.models import User

from django.shortcuts import render, redirect
from apps.accounts.models import User


def add_trainer(request):

    # 🔐 Restrict access
    if request.user.role != 'super_admin':
        return redirect('login')

    # 📩 Handle form submit
    if request.method == 'POST':

        email = request.POST.get('email')
        dob = request.POST.get('dob')

        # 🔥 CHECK DUPLICATE EMAIL
        if User.objects.filter(email=email).exists():
            return render(request, 'attendences/super_admin/add_trainer.html', {
                'error': 'Trainer with this email already exists'
            })

        # =====================================
        # ✅ STEP 1: CREATE USER (NO USERNAME YET)
        # =====================================
        user = User(
            email=email,
            role='trainer',

            dob=dob,
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),

            qualification=request.POST.get('qualification'),
            experience=request.POST.get('experience'),

            salary=request.POST.get('salary'),
            joining_date=request.POST.get('joining_date'),

            trainer_photo=request.FILES.get('photo'),
            document=request.FILES.get('document'),
        )

        user.save()  # 🔥 IMPORTANT → generates trainer_reg_no

        # =====================================
        # ✅ STEP 2: SET USERNAME = REG NO
        # =====================================
        user.username = user.trainer_reg_no

        # 🔐 PASSWORD = DOB
        user.set_password(dob)

        user.save()

        # 🔁 REDIRECT TO APPOINTMENT LETTER
        return redirect('trainer_appointment', user.id)

    # 📄 LOAD FORM PAGE
    return render(request, 'attendences/super_admin/add_trainer.html')




def trainer_appointment(request, id):
    trainer = User.objects.get(id=id)

    return render(request, 'attendences/super_admin/appointment_letter.html', {
        'trainer': trainer
    })