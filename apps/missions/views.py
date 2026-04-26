from django.shortcuts import render, get_object_or_404, redirect
from .models import Mission, MissionProgress
from django.utils import timezone
from .models import PlayerProfile

def xp_for_next_level(level):
    return level * (level + 1) * 25

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Mission, MissionProgress, PlayerProfile
from .utils import xp_for_next_level   


@login_required
def play_mission(request, mission_id):

    mission = get_object_or_404(Mission, id=mission_id)
    user = request.user

    # 🔥 GET OR CREATE PROGRESS
    progress, _ = MissionProgress.objects.get_or_create(
        user=user,
        mission=mission
    )

    # 🔥 PLAYER PROFILE (XP SYSTEM)
    player, _ = PlayerProfile.objects.get_or_create(user=user)

    message = None
    success = False
    leveled_up = False

    if request.method == "POST":

        user_input = request.POST.get("answer", "").strip()

        # 🔥 ALWAYS INCREASE ATTEMPTS
        progress.attempts += 1

        # 🔥 NORMALIZE INPUT (avoid spacing issues)
        clean_input = user_input.replace(" ", "")
        correct_answer = mission.correct_answer.replace(" ", "")

        if clean_input == correct_answer:

            success = True

            # ✅ ONLY FIRST TIME COMPLETION GIVES XP
            if not progress.completed:
                progress.completed = True
                progress.score = mission.xp
                progress.completed_at = timezone.now()

                # 🎯 ADD XP
                player.xp += mission.xp

                # 🔥 LEVEL UP LOOP (handles multiple jumps)
                while player.xp >= xp_for_next_level(player.level):
                    player.level += 1
                    leveled_up = True

                player.save()

            message = f"🎉 Correct! +{mission.xp} XP"

        else:
            message = "❌ Incorrect! Try again."

        progress.save()

    # 🔥 XP PROGRESS BAR CALCULATION
    current_level_xp = xp_for_next_level(player.level - 1) if player.level > 1 else 0
    next_level_xp = xp_for_next_level(player.level)

    if next_level_xp > current_level_xp:
        progress_percent = int(
            (player.xp - current_level_xp) /
            (next_level_xp - current_level_xp) * 100
        )
    else:
        progress_percent = 0

    return render(request, "missions/play.html", {
        "mission": mission,
        "progress": progress,
        "player": player,
        "message": message,
        "success": success,
        "leveled_up": leveled_up,
        "progress_percent": progress_percent,
        "next_level_xp": next_level_xp,
    })

from django.shortcuts import render, redirect
from .models import Mission
from apps.syllabus.models import Topic, Syllabus

from django.shortcuts import render, redirect
from .models import Mission
from apps.syllabus.models import Topic, Syllabus


def create_mission(request):
    if not request.user.is_staff:
        return redirect("trainee_dashboard")  # ✅ correct redirect

    # 🔥 GET SELECTED CLASS (e.g. "6")
    selected_class = request.GET.get("class")

    # 🔥 ALL CLASSES
    classes = Syllabus.objects.all().order_by("class_name")

    # 🔥 USE DIRECT VALUE (NO "Class ")
    class_filter = selected_class if selected_class else None

    # 🔥 FILTER TOPICS
    if class_filter:
        topics = Topic.objects.filter(
            phase__syllabus__class_name=class_filter
        ).select_related("phase__syllabus")
    else:
        topics = Topic.objects.all().select_related("phase__syllabus")

    # 🔥 CREATE MISSION
    if request.method == "POST":
        Mission.objects.create(
            topic_id=request.POST.get("topic"),
            title=request.POST.get("title"),
            story=request.POST.get("story"),
            mission_type=request.POST.get("mission_type"),
            starter_code=request.POST.get("starter_code"),
            correct_answer=request.POST.get("correct_answer"),
            xp=int(request.POST.get("xp") or 10),
            allow_for_trainee=True if request.POST.get("allow") else False,
            created_by=request.user
        )

        # ✅ KEEP FILTER AFTER SUBMIT
        if selected_class:
            return redirect(f"{request.path}?class={selected_class}")
        return redirect(request.path)

    # 🔥 FILTER MISSIONS
    missions = Mission.objects.select_related("topic", "topic__phase__syllabus")

    if class_filter:
        missions = missions.filter(
            topic__phase__syllabus__class_name=class_filter
        )

    missions = missions.order_by("-id")

    return render(request, "missions/create_mission.html", {
        "topics": topics,
        "missions": missions,
        "classes": classes,
        "selected_class": selected_class
    })
    
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Mission
@login_required
def trainee_missions(request):

    user = request.user

    if user.role != "trainer" and not user.is_staff:
        return redirect("trainee_dashboard")

    # 🔥 SAME FIELD HERE
    school = getattr(user, "assigned_school", None)

    missions = Mission.objects.filter(
        allow_for_trainee=True,
        is_active=True
    )

    data = []

    for m in missions:
        unlock = MissionUnlock.objects.filter(
            mission=m,
            school=school
        ).first()

        data.append({
            "mission": m,
            "unlocked": unlock.is_unlocked if unlock else False
        })

    return render(request, "missions/trainee_missions.html", {
        "data": data
    })
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect   
from .models import Mission, MissionUnlock

@login_required
def toggle_mission_unlock(request):

    if request.method == "POST":
        mission_id = request.POST.get("mission_id")

        mission = Mission.objects.get(id=mission_id)

        # 🔥 ALWAYS SAME FIELD
        school = getattr(request.user, "assigned_school", None)

        if not school:
            print("❌ NO SCHOOL FOUND")
            return redirect("trainee_missions")

        unlock, created = MissionUnlock.objects.get_or_create(
            mission=mission,
            school=school
        )

        unlock.is_unlocked = not unlock.is_unlocked
        unlock.save()

        print("✅ TOGGLED:", mission.id, unlock.is_unlocked)

    return redirect("trainee_missions")



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import get_user_model
from .models import Mission, MissionProgress

User = get_user_model()


@login_required
def school_missions(request):

    user = request.user
    school = getattr(user, "school", None)

    selected_class = request.GET.get("class")

    # 🔥 GET STUDENTS
    students = User.objects.filter(
        role="student",
        school=school
    )

    if selected_class:
        students = students.filter(student_class=selected_class)

    # 🔥 GET MISSIONS
    missions = Mission.objects.filter(
        allow_for_trainee=True,
        is_active=True
    )

    data = []

    for m in missions:
        student_data = []

        for s in students:
            progress = MissionProgress.objects.filter(
                user=s,
                mission=m
            ).first()

            student_data.append({
                "student": s,
                "completed": progress.completed if progress else False,
                "score": progress.score if progress else 0,
                "attempts": progress.attempts if progress else 0
            })

        data.append({
            "mission": m,
            "students": student_data
        })

    return render(request, "missions/school_missions.html", {
        "data": data,
        "selected_class": selected_class
    })

