from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Assessment, Question, Option, Attempt, Answer

    
from django.db.models import Q
from django.utils import timezone
from django.db.models import Q
from django.utils import timezone

@login_required
def student_assessments(request):
    user = request.user
    now = timezone.localtime()

    assessments = Assessment.objects.filter(
        is_published=True,
        class_name=str(user.student_class)
    ).filter(
        Q(section=user.section) | Q(section="")
    ).order_by("-id")

    return render(request, "assessments/student/dashboard.html", {
        "assessments": assessments,
        "now": now
    })

@login_required
def play_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    user = request.user

    # 🔒 Time check (safe)
    now = timezone.now()
    if assessment.start_datetime and now < assessment.start_datetime:
        return redirect("student_assessments")

    if assessment.end_datetime and now > assessment.end_datetime:
        return redirect("student_assessments")

    # 🧠 Attempt (single active)
    attempt, created = Attempt.objects.get_or_create(
        student=user,
        assessment=assessment,
        is_submitted=False,
        defaults={
            "time_left": 0,
            "current_question": 1
        }
    )

    # 🔒 Lock check
    if attempt.is_locked or attempt.is_submitted:
        return redirect("student_assessments")

    # 📚 Questions
    questions = list(assessment.questions.order_by("order"))
    total_questions = len(questions)

    if total_questions == 0:
        return redirect("student_assessments")

    current_index = attempt.current_question - 1

    # ✅ If finished
    if current_index >= total_questions:
        return redirect("submit_assessment", assessment.id)

    question = questions[current_index]

    # ⏱ Timer setup
    if attempt.time_left == 0:
        attempt.time_left = question.time_limit_seconds or 30
        attempt.save()

    # ================= HANDLE POST =================
    if request.method == "POST":

        selected_option_id = request.POST.get("option")
        text_answer = request.POST.get("text_answer", "").strip()

        # 🔥 Always create/update answer safely
        answer, _ = Answer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                "selected_option": None,
                "text_answer": "",
                "is_correct": False,
                "marks_obtained": 0
            }
        )

        # ================= MCQ =================
        if question.question_type == "mcq":

            if selected_option_id:
                try:
                    option = Option.objects.get(id=selected_option_id)
                    answer.selected_option = option

                    if option.is_correct:
                        answer.is_correct = True
                        answer.marks_obtained = question.marks

                except Option.DoesNotExist:
                    pass  # safe fallback

        # ================= TEXT =================
        elif question.question_type == "text":

            answer.text_answer = text_answer

            if question.correct_answer:
                if text_answer and text_answer.strip().lower() == question.correct_answer.strip().lower():
                    answer.is_correct = True
                    answer.marks_obtained = question.marks

        answer.save()

        # ➡ Move to next
        attempt.current_question += 1
        attempt.time_left = 0
        attempt.save()

        return redirect("play_assessment", assessment.id)

    # ================= RENDER =================
    return render(request, "assessments/student/play.html", {
        "assessment": assessment,
        "question": question,
        "attempt": attempt,
        "q_number": attempt.current_question,
        "total": total_questions
    })


from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def student_assessments(request):
    user = request.user
    now = timezone.localtime()

    assessments = Assessment.objects.filter(
        is_published=True,
        class_name=str(user.student_class)
    ).order_by("-id")

    enriched = []
    submitted_count = 0
    total_obtained = 0
    total_possible = 0

    for a in assessments:

        # 🔥 ALL attempts for this assessment
        attempts = Attempt.objects.filter(
            student=user,
            assessment=a
        ).order_by("-id")

        att = None

        # 🔥 1. pick attempt that has answers (MOST IMPORTANT FIX)
        for c in attempts:
            if c.answers.exists():
                att = c
                break

        # 🔥 2. fallback to latest
        if not att:
            att = attempts.first()

        # 🔥 TOTAL MARKS (assessment)
        total_marks = a.questions.aggregate(
            total=Sum("marks")
        )["total"] or 0

        if att and att.is_submitted:

            obtained_marks = att.answers.aggregate(
                total=Sum("marks_obtained")
            )["total"] or 0

            submitted = True
            submitted_count += 1
            total_obtained += obtained_marks

        else:
            obtained_marks = 0
            submitted = False

        total_possible += total_marks

        enriched.append({
            "assessment": a,
            "submitted": submitted,
            "obtained": obtained_marks,
            "total": total_marks
        })

    return render(request, "assessments/student/dashboard.html", {
        "assessments": enriched,
        "total_assessments": len(enriched),
        "submitted_count": submitted_count,
        "total_obtained": total_obtained,
        "total_possible": total_possible,
        "now": now
    })
    
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def track_tab_switch(request, attempt_id):
    if request.method == "POST":
        attempt = get_object_or_404(Attempt, id=attempt_id)

        attempt.tab_switch_count += 1

        # 🔥 lock if exceeded limit
        if attempt.tab_switch_count >= attempt.assessment.tab_switch_limit:
            attempt.is_locked = True

        attempt.save()

        return JsonResponse({
            "status": "ok",
            "tab_switch_count": attempt.tab_switch_count,
            "locked": attempt.is_locked
        })

    return JsonResponse({"status": "invalid"})
    
    
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def add_questions(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)

    if request.method == "POST":

        existing_questions = Question.objects.filter(assessment=assessment)
        existing_ids = set(existing_questions.values_list("id", flat=True))

        received_ids = set()

        i = 0
        created_count = 0

        while True:
            q_text = request.POST.get(f"q_{i}_text")

            # 🔥 stop when no more questions
            if not q_text:
                break

            q_id = request.POST.get(f"q_{i}_id")
            q_type = request.POST.get(f"q_{i}_type")
            marks = int(request.POST.get(f"q_{i}_marks") or 1)
            time = int(request.POST.get(f"q_{i}_time") or 30)

            # ================= UPDATE EXISTING =================
            if q_id:
                question = Question.objects.get(id=q_id)
                question.text = q_text
                question.question_type = q_type
                question.marks = marks
                question.time_limit_seconds = time
                question.order = i
                question.save()

                received_ids.add(question.id)

                # 🔥 clear old options before re-adding
                question.options.all().delete()

            # ================= CREATE NEW =================
            else:
                question = Question.objects.create(
                    assessment=assessment,
                    text=q_text,
                    question_type=q_type,
                    marks=marks,
                    time_limit_seconds=time,
                    order=i
                )

            created_count += 1

            # ================= MCQ =================
            if q_type == "mcq":
                correct_index = request.POST.get(f"q_{i}_correct")

                j = 0
                while True:
                    opt_text = request.POST.get(f"q_{i}_opt_{j}")
                    if not opt_text:
                        break

                    Option.objects.create(
                        question=question,
                        text=opt_text,
                        is_correct=(str(j) == correct_index)
                    )
                    j += 1

            # ================= TEXT =================
            elif q_type == "text":
                question.correct_answer = request.POST.get(f"q_{i}_answer")
                question.save()

            i += 1

        # 🔥 DELETE REMOVED QUESTIONS
        to_delete = existing_ids - received_ids
        if to_delete:
            Question.objects.filter(id__in=to_delete).delete()

        # ================= VALIDATION =================
        if created_count == 0:
            messages.error(request, "⚠️ Please add at least one question.")
            return redirect(request.path)

        # ================= PUBLISH =================
        assessment.is_published = True
        assessment.save()

        # ================= SUCCESS =================
        messages.success(request, "✅ Questions saved and assessment published!")

        # 🔥 stay on same page to show saved questions
        return redirect("add_questions", assessment_id=assessment.id)

    # ================= GET =================
    questions = Question.objects.filter(
        assessment=assessment
    ).prefetch_related("options").order_by("order")

    return render(request, "assessments/trainee/add_questions.html", {
        "assessment": assessment,
        "questions": questions
    })
    
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def school_assessments(request):
    if request.user.role != "school_admin":
        return redirect("school_admin_dashboard")

    return render(request, "assessments/school/dashboard.html")

from apps.syllabus.models import Syllabus

@login_required
def trainee_assessments(request):

    user = request.user
    school = user.school

    # 🔥 fetch only classes of this school (now works after your model fix)
    classes = Syllabus.objects.filter(
        school=school
    ).order_by("class_name")

    # 🔥 show only this trainee's assessments
    assessments = Assessment.objects.filter(
        created_by=user
    ).order_by("-id")

    if request.method == "POST":

        # 🔥 CREATE ASSESSMENT
        assessment = Assessment.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            assessment_type=request.POST.get("type"),
            created_by=user,
            class_name=request.POST.get("class_name"),
            section=request.POST.get("section"),
            start_datetime=request.POST.get("start_datetime"),
            end_datetime=request.POST.get("end_datetime"),
            tab_switch_limit=int(request.POST.get("tab_limit") or 3),

            # 🔥 IMPORTANT: default not visible to students yet
            is_active=True,
            is_published=False   # 👈 ADD THIS FIELD IN MODEL
        )

        # 🔥 REDIRECT TO ADD QUESTIONS PAGE
        return redirect("add_questions", assessment_id=assessment.id)

    return render(request, "assessments/trainee/dashboard.html", {
        "assessments": assessments,
        "classes": classes
    })
    
    


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def publish_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)

    # 🔒 Only allow POST (safety)
    if request.method != "POST":
        messages.error(request, "❌ Invalid request method.")
        return redirect("add_questions", assessment_id=assessment.id)

    # 🔁 If already published
    if assessment.is_published:
        messages.info(request, "ℹ️ Assessment is already published.")
    else:
        assessment.is_published = True
        assessment.save()
        messages.success(request, "🚀 Assessment published successfully!")

    return redirect("add_questions", assessment_id=assessment.id)



@login_required
def delete_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)

    if request.method == "POST":
        assessment.delete()

    return redirect("trainee_assessments")


from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Assessment, Attempt, Question, Answer, Option

@login_required
def submit_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)

    attempt = Attempt.objects.filter(
        student=request.user,
        assessment=assessment
    ).order_by("-id").first()

    if not attempt:
        return redirect("student_assessments")

    questions = Question.objects.filter(assessment=assessment)

    score = 0
    total = 0
    answers_data = []

    for q in questions:
        total += q.marks

        ans = Answer.objects.filter(
            attempt=attempt,
            question=q
        ).first()

        is_correct = False
        correct_answer = ""
        student_answer = "No answer"

        if ans:
            # MCQ
            if q.question_type == "mcq":
                if ans.selected_option:
                    student_answer = ans.selected_option.text

                correct_option = q.options.filter(is_correct=True).first()
                if correct_option:
                    correct_answer = correct_option.text

                if ans.selected_option and correct_option and ans.selected_option.id == correct_option.id:
                    is_correct = True
                    score += q.marks

            # TEXT
            else:
                student_answer = ans.text_answer

                if q.correct_answer:
                    correct_answer = q.correct_answer

                if ans.text_answer and q.correct_answer and ans.text_answer.strip().lower() == q.correct_answer.strip().lower():
                    is_correct = True
                    score += q.marks

        answers_data.append({
            "question": q,
            "answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    attempt.is_submitted = True
    attempt.save()

    return render(request, "assessments/student/result.html", {
        "attempt": attempt,
        "score": score,
        "total": total,
        "answers": answers_data
    })



from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounts.models import User
from apps.assessments.models import Assessment, Attempt


@login_required
def school_assessments(request):

    selected_class = request.GET.get("class")

    # ✅ CLEAN + ORDERED CLASSES
    classes = list(
        Assessment.objects
        .values_list("class_name", flat=True)
        .distinct()
    )

    students = []

    if selected_class:

        students_qs = User.objects.filter(
            role="student",
            student_class=selected_class
        )

        assessments = Assessment.objects.filter(
            class_name=selected_class
        )

        for s in students_qs:

            attempts = Attempt.objects.filter(
                student=s,
                assessment__in=assessments
            )

            submitted_attempts = attempts.filter(is_submitted=True)

            total_score = 0
            total_possible = 0

            for att in submitted_attempts:

                obtained = att.answers.aggregate(
                    total=Sum("marks_obtained")
                )["total"] or 0

                total = att.assessment.questions.aggregate(
                    total=Sum("marks")
                )["total"] or 0

                total_score += obtained
                total_possible += total

            students.append({
                "student": s,
                "submitted": submitted_attempts.count(),
                "total_assessments": assessments.count(),
                "score": f"{total_score}/{total_possible}" if total_possible else "0/0"
            })

    return render(request, "assessments/school/dashboard.html", {
        "classes": classes,
        "students": students,
        "selected_class": selected_class,
    })