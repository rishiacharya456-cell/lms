from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Syllabus, Phase, Topic, TopicUnlock, Progress
# 🎓 STUDENT SYLLABUS VIEW
def student_syllabus(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    user = request.user

    # ⚠️ assuming user has school relation
    school = getattr(user, 'school', None)

    # 🔥 ONLY SHOW ENABLED PHASES
    phases = Phase.objects.filter(
        syllabus=syllabus,
        allow_for_view=True
    ).order_by('order')

    data = []

    for phase in phases:

        # 🔥 ONLY SHOW ENABLED TOPICS
        topics = Topic.objects.filter(
            phase=phase,
            allow_for_view=True
        ).order_by('order')

        topic_data = []
        completed_count = 0

        for topic in topics:

            # 🔥 FIXED UNLOCK LOGIC (IMPORTANT)
            unlocked = True  # default visible

            if school:
                unlock = TopicUnlock.objects.filter(
                    school=school,
                    topic=topic
                ).first()

                if unlock:
                    unlocked = unlock.is_unlocked

            # ❌ SKIP if locked
            if not unlocked:
                continue

            # ✅ check completion
            progress = Progress.objects.filter(
                user=user,
                topic=topic,
                completed=True
            ).first()

            is_completed = True if progress else False

            if is_completed:
                completed_count += 1

            topic_data.append({
                "topic": topic,
                "unlocked": True,
                "completed": is_completed
            })

        # 🔥 ONLY SHOW PHASE IF IT HAS VALID TOPICS
        if topic_data:
            data.append({
                "phase": phase,
                "topics": topic_data,
                "completed": completed_count,
                "total": len(topic_data)
            })

    return render(request, "syllabus/student_syllabus.html", {
        "syllabus": syllabus,
        "data": data
    })


# 🔓 UNLOCK TOPIC (TRAINER)
def unlock_topic(request, topic_id):
    user = request.user

    # 🔒 Only trainer or staff
    if not user.is_staff and user.role != "trainer":
        return redirect("trainee_dashboard")

    topic = Topic.objects.get(id=topic_id)

    # 🔥 trainer's school
    school = getattr(user, "school", None)

    if not school:
        return redirect("trainee_dashboard")

    # ✅ CREATE OR UPDATE UNLOCK
    TopicUnlock.objects.update_or_create(
        school=school,
        topic=topic,
        defaults={"is_unlocked": True}
    )

    return redirect(request.META.get("HTTP_REFERER"))

# ✅ MARK TOPIC COMPLETE (STUDENT)
def mark_complete(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    progress, created = Progress.objects.get_or_create(
        user=request.user,
        topic=topic
    )

    progress.completed = True
    progress.save()

    return JsonResponse({"success": True})


# ⚙️ MANAGEMENT PAGE (TEMP)
def manage_syllabus(request):
    return HttpResponse("Syllabus Management Page")


from django.http import JsonResponse

def unlock_phase(request, phase_id):
    if not request.user.is_staff:
        return JsonResponse({"error": "Not allowed"}, status=403)

    phase = Phase.objects.get(id=phase_id)
    phase.is_locked = False
    phase.save()

    return JsonResponse({"success": True})


def mark_complete(request, lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)

    progress, created = Progress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )

    progress.completed = True
    progress.save()

    return JsonResponse({"success": True})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Syllabus, Phase, Topic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Syllabus, Topic


@staff_member_required
def manage_syllabus(request):

    if request.method == "POST":

        # 🔥 1. TOGGLE SYLLABUS (ON/OFF)
        if "toggle_syllabus" in request.POST:
            syllabus_id = request.POST.get("syllabus_id")

            syllabus = get_object_or_404(Syllabus, id=syllabus_id)
            syllabus.allow_for_trainee = not syllabus.allow_for_trainee
            syllabus.save()

            return redirect('manage_syllabus')

        # 🔥 2. TOGGLE TOPIC VISIBILITY (THIS WAS MISSING)
        elif "toggle_topic" in request.POST:
            topic_id = request.POST.get("topic_id")

            topic = get_object_or_404(Topic, id=topic_id)
            topic.allow_for_view = not topic.allow_for_view
            topic.save()

            return redirect('manage_syllabus')

    # NORMAL LOAD
    syllabus_list = Syllabus.objects.all()

    return render(request, "syllabus/manage.html", {
        "syllabus_list": syllabus_list
    })

# ➕ ADD SYLLABUS (Class)
@staff_member_required
def add_syllabus(request):
    if request.method == "POST":
        class_name = request.POST.get("class_name")
        if class_name:
            Syllabus.objects.create(class_name=class_name)

    return redirect('manage_syllabus')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required

from apps.syllabus.models import Syllabus, Phase, Topic, TopicUnlock
from apps.schools.models import School


# ➕ ADD PHASE
@staff_member_required
def add_phase(request):
    if request.method == "POST":
        syllabus_id = request.POST.get("syllabus_id")
        title = request.POST.get("title")

        syllabus = get_object_or_404(Syllabus, id=syllabus_id)

        Phase.objects.create(
            syllabus=syllabus,
            title=title,
            allow_for_view=True   # ✅ default ON
        )

    return redirect('manage_syllabus')


# ➕ ADD TOPIC (STAFF + TRAINEE CONTROL)
def add_topic(request):
    if request.method == "POST":
        phase_id = request.POST.get("phase_id")
        phase = get_object_or_404(Phase, id=phase_id)
        syllabus = phase.syllabus

        # 🔒 PERMISSION CHECK
        if not request.user.is_staff and not syllabus.allow_edit_for_trainee:
            return redirect('trainee_dashboard')

        Topic.objects.create(
            phase=phase,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            file=request.FILES.get("file"),
            image=request.FILES.get("image"),
            uploaded_by=request.user,
            allow_for_view=True   # ✅ visible by default
        )

    return redirect('manage_syllabus')


# 🔥 PHASE TOGGLE (NEW)
def toggle_phase(request):
    if request.method == "POST":
        phase_id = request.POST.get("phase_id")
        phase = get_object_or_404(Phase, id=phase_id)

        # 🔒 ONLY STAFF OR TRAINER
        if not request.user.is_staff and request.user.role != "trainer":
            return redirect('trainee_dashboard')

        phase.allow_for_view = not phase.allow_for_view
        phase.save()

    return redirect('manage_syllabus')


# 🔥 TOPIC TOGGLE (CLEAN VERSION)
def toggle_topic(request):
    if request.method == "POST":
        topic_id = request.POST.get("topic_id")
        topic = get_object_or_404(Topic, id=topic_id)

        # 🔒 ONLY STAFF OR TRAINER
        if not request.user.is_staff and request.user.role != "trainer":
            return redirect('trainee_dashboard')

        topic.allow_for_view = not topic.allow_for_view
        topic.save()

    return redirect('manage_syllabus')


# 🔓 ASSIGN TOPICS (SCHOOL CONTROL - OPTIONAL)
@staff_member_required
def assign_topics(request):
    schools = School.objects.all()
    topics = Topic.objects.select_related('phase', 'phase__syllabus').all()

    selected_school = None
    unlocked_ids = []

    if request.method == "POST":
        school_id = request.POST.get("school")
        selected_topics = request.POST.getlist("topics")

        selected_school = get_object_or_404(School, id=school_id)

        for topic in topics:
            unlock, _ = TopicUnlock.objects.get_or_create(
                school=selected_school,
                topic=topic
            )

            unlock.is_unlocked = str(topic.id) in selected_topics
            unlock.save()

        unlocked_ids = TopicUnlock.objects.filter(
            school=selected_school,
            is_unlocked=True
        ).values_list('topic_id', flat=True)

    return render(request, "syllabus/assign_topics.html", {
        "schools": schools,
        "topics": topics,
        "selected_school": selected_school,
        "unlocked_ids": unlocked_ids
    })


# ❌ DELETE TOPIC
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    if not request.user.is_staff and request.user.role != "trainer":
        return redirect('trainee_dashboard')

    topic.delete()
    return redirect('manage_syllabus')


# ❌ DELETE PHASE
def delete_phase(request, phase_id):
    phase = get_object_or_404(Phase, id=phase_id)

    if not request.user.is_staff:
        return redirect('trainee_dashboard')

    phase.delete()
    return redirect('manage_syllabus')


from django.shortcuts import render, get_object_or_404, redirect
from .models import Syllabus, Phase, Topic, TopicUnlock


def trainee_syllabus(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    user = request.user

    # 🔥 TOGGLE (TRAINER / STAFF ONLY)
    if request.method == "POST":

        if "toggle_phase" in request.POST:
            phase = get_object_or_404(Phase, id=request.POST.get("toggle_phase"))

            if user.role == "trainer" or user.is_staff:
                phase.allow_for_view = not phase.allow_for_view
                phase.save()

            return redirect(request.path)

        if "toggle_topic" in request.POST:
            topic = get_object_or_404(Topic, id=request.POST.get("toggle_topic"))

            if user.role == "trainer" or user.is_staff:
                topic.allow_for_view = not topic.allow_for_view
                topic.save()

            return redirect(request.path)

    # 🔒 SYLLABUS ACCESS
    if not syllabus.allow_for_trainee:
        return render(request, "syllabus/trainee_syllabus.html", {
            "syllabus": syllabus,
            "data": [],
            "allowed": False
        })

    # 🔒 CLASS FILTER (STUDENT ONLY - FIXED)
    if user.role == "student":
        student_class = str(getattr(user, "student_class", "")).strip()

        if str(syllabus.class_name).strip() != f"Class {student_class}":
            return render(request, "syllabus/trainee_syllabus.html", {
                "syllabus": syllabus,
                "data": [],
                "allowed": False
            })

    user_school = getattr(user, "school", None)

    # 🔥 IMPORTANT CHANGE
    # Trainer sees ALL phases
    # Student sees only active ones
    if user.role == "trainer" or user.is_staff:
        phases = Phase.objects.filter(
            syllabus=syllabus
        ).order_by("order")
    else:
        phases = Phase.objects.filter(
            syllabus=syllabus,
            allow_for_view=True
        ).order_by("order")

    data = []

    for phase in phases:

        # 🔥 Trainer sees all topics, student sees only visible
        if user.role == "trainer" or user.is_staff:
            topics = Topic.objects.filter(
                phase=phase
            ).order_by("order")
        else:
            topics = Topic.objects.filter(
                phase=phase,
                allow_for_view=True
            ).order_by("order")

        topic_data = []

        for topic in topics:

            unlocked = True

            # 🔓 STUDENT SCHOOL FILTER
            if user.role == "student":
                unlocked = False

                if user_school:
                    unlock = TopicUnlock.objects.filter(
                        school=user_school,
                        topic=topic,
                        is_unlocked=True
                    ).first()

                    unlocked = True if unlock else False

            # 🔥 TRAINER ALWAYS SEES
            if user.role == "trainer" or user.is_staff:
                topic_data.append({
                    "topic": topic,
                    "visible": topic.allow_for_view,
                    "unlocked": True
                })
            else:
                if unlocked:
                    topic_data.append({
                        "topic": topic,
                        "visible": True,
                        "unlocked": True
                    })

        # 🔥 FIX: ALWAYS SHOW PHASE FOR TRAINER
        if user.role == "trainer" or user.is_staff:
            data.append({
                "phase": phase,
                "topics": topic_data  # can be empty
            })
        else:
            # student only sees if content exists
            if topic_data:
                data.append({
                    "phase": phase,
                    "topics": topic_data
                })

    return render(request, "syllabus/trainee_syllabus.html", {
        "syllabus": syllabus,
        "data": data,
        "allowed": True
    })


# 🔥 TRAINEE DASHBOARD (FIXED CLASS MATCH)
def trainee_dashboard(request):
    user = request.user
    school = getattr(user, 'school', None)

    syllabus = None

    # 🎯 GET CLASS
    if user.role == "student":
        class_name = str(getattr(user, 'student_class', '')).strip()
    else:
        class_name = str(getattr(user, 'assigned_class', '')).strip()

    # 🔥 FIX: MATCH "Class X"
    if class_name:
        syllabus = Syllabus.objects.filter(
            class_name=f"Class {class_name}",
            allow_for_trainee=True
        ).first()

    # 🔥 FALLBACK
    if not syllabus:
        syllabus = Syllabus.objects.filter(
            allow_for_trainee=True
        ).first()

    return render(request, "dashboard/trainee_dashboard.html", {
        "syllabus": syllabus,
        "trainer": user,
        "school": school
    })
    


from apps.syllabus.models import Syllabus

def student_dashboard(request):
    user = request.user
    school = getattr(user, 'school', None)

    syllabus = None

    if user.role == "student":

        # 🎯 FIX CLASS FORMAT
        student_class = str(user.student_class).strip()

        syllabus = Syllabus.objects.filter(
            class_name__icontains=student_class,   # ✅ FIXED
            allow_for_trainee=True
        ).first()

    return render(request, "dashboard/student_dashboard.html", {
        "syllabus": syllabus,
        "student": user,
        "school": school
    })
    
    
def school_syllabus(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    user = request.user

    # 🔥 SCHOOL USER
    school = getattr(user, 'school', None)

    data = []

    # 🔥 ONLY ENABLED PHASES
    phases = Phase.objects.filter(
        syllabus=syllabus,
        allow_for_view=True
    ).order_by("order")

    for phase in phases:

        # 🔥 ONLY ENABLED TOPICS
        topics = Topic.objects.filter(
            phase=phase,
            allow_for_view=True
        ).order_by("order")

        topic_data = []

        for topic in topics:

            # 🔓 UNLOCK LOGIC
            unlocked = True

            if school:
                unlock = TopicUnlock.objects.filter(
                    school=school,
                    topic=topic
                ).first()

                if unlock:
                    unlocked = unlock.is_unlocked

            if not unlocked:
                continue

            topic_data.append({
                "topic": topic,
                "unlocked": True
            })

        # 🔥 ONLY SHOW PHASE IF HAS TOPICS
        if topic_data:
            data.append({
                "phase": phase,
                "topics": topic_data
            })

    return render(request, "syllabus/school_syllabus.html", {
        "syllabus": syllabus,
        "data": data
    })