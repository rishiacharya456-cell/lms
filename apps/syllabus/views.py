from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Syllabus, Phase, Topic, TopicUnlock, Progress


# 🎓 STUDENT SYLLABUS VIEW
def student_syllabus(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    phases = Phase.objects.filter(syllabus=syllabus).order_by('order')

    user = request.user

    # ⚠️ assuming user has school relation
    school = getattr(user, 'school', None)

    data = []

    for phase in phases:
        topics = Topic.objects.filter(phase=phase).order_by('order')

        topic_data = []
        completed_count = 0

        for topic in topics:
            # 🔓 check unlock status (school-based)
            unlocked = False
            if school:
                unlock = TopicUnlock.objects.filter(
                    school=school,
                    topic=topic,
                    is_unlocked=True
                ).first()
                unlocked = True if unlock else False

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
                "unlocked": unlocked,
                "completed": is_completed
            })

        data.append({
            "phase": phase,
            "topics": topic_data,
            "completed": completed_count,
            "total": topics.count()
        })

    return render(request, "syllabus/student_syllabus.html", {
        "syllabus": syllabus,
        "data": data
    })


# 🔓 UNLOCK TOPIC (TRAINER / ADMIN)
def unlock_topic(request, topic_id):
    user = request.user

    if not user.is_staff:
        return JsonResponse({"error": "Not allowed"}, status=403)

    school = getattr(user, 'school', None)

    if not school:
        return JsonResponse({"error": "No school assigned"}, status=400)

    topic = get_object_or_404(Topic, id=topic_id)

    unlock, created = TopicUnlock.objects.get_or_create(
        school=school,
        topic=topic
    )

    unlock.is_unlocked = True
    unlock.save()

    return JsonResponse({"success": True})


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


# 👑 SUPER ADMIN PANEL
@staff_member_required
def manage_syllabus(request):
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


# ➕ ADD PHASE
@staff_member_required
def add_phase(request):
    if request.method == "POST":
        syllabus_id = request.POST.get("syllabus_id")
        title = request.POST.get("title")

        syllabus = get_object_or_404(Syllabus, id=syllabus_id)

        Phase.objects.create(
            syllabus=syllabus,
            title=title
        )

    return redirect('manage_syllabus')


# ➕ ADD TOPIC
@staff_member_required
def add_topic(request):
    if request.method == "POST":
        phase_id = request.POST.get("phase_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        file = request.FILES.get("file")
        image = request.FILES.get("image")

        phase = Phase.objects.get(id=phase_id)

        Topic.objects.create(
            phase=phase,
            title=title,
            description=description,
            file=file,
            image=image
        )

    return redirect('manage_syllabus')



from apps.schools.models import School
from .models import TopicUnlock


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

        # Update unlock status
        for topic in topics:
            unlock, _ = TopicUnlock.objects.get_or_create(
                school=selected_school,
                topic=topic
            )

            unlock.is_unlocked = str(topic.id) in selected_topics
            unlock.save()

        # refresh unlocked ids
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



def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    topic.delete()
    return redirect('manage_syllabus')



def delete_phase(request, phase_id):
    phase = get_object_or_404(Phase, id=phase_id)
    phase.delete()
    return redirect('manage_syllabus')