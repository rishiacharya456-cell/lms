from django.shortcuts import render, redirect
from apps.communications.services import send_message, get_user_notifications
from apps.communications.models import Message
from apps.schools.models import School, Section


# 📢 SEND MESSAGE VIEW (SUPER ADMIN)
def send_message_view(request):

    schools = School.objects.all()
    sections = Section.objects.all()

    # 🔥 Get sent messages for left panel (chat-style UI)
    messages = Message.objects.filter(sender=request.user).order_by("-created_at")

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        target_type = request.POST.get("target_type")
        school_id = request.POST.get("school")
        section_id = request.POST.get("section")
        priority = request.POST.get("priority", "normal")

        # 🔒 Basic validation
        if not title or not content:
            return redirect("send_message")

        # Safe fetching (no crash)
        school = School.objects.filter(id=school_id).first() if school_id else None
        section = Section.objects.filter(id=section_id).first() if section_id else None

        # 🚀 Send message
        send_message(
            sender=request.user,
            title=title,
            content=content,
            target_type=target_type,
            school=school,
            section=section,
            priority=priority
        )

        return redirect("send_message")

    return render(request, "communications/send_message.html", {
        "schools": schools,
        "sections": sections,
        "messages": messages   # 🔥 IMPORTANT
    })


# 📩 INBOX VIEW (ALL USERS)
def inbox_view(request):

    notifications = get_user_notifications(request.user)

    return render(request, "communications/inbox.html", {
        "notifications": notifications
    }) 
    
    
    
from django.http import JsonResponse
from apps.communications.services import get_unread_count

def unread_count_api(request):
    if request.user.is_authenticated:
        count = get_unread_count(request.user)
        return JsonResponse({"count": count})
    return JsonResponse({"count": 0})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from apps.communications.services import register_device


@csrf_exempt
def register_device_view(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)

        token = data.get("token")

        if token:
            register_device(request.user, token)
            return JsonResponse({"status": "saved"})

    return JsonResponse({"status": "failed"})


from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from apps.communications.services import register_device


@csrf_exempt  # for now (we can secure later)
def save_device(request):

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            token = data.get("token")
            device_type = data.get("device_type", "web")

            register_device(request.user, token, device_type)

            return JsonResponse({
                "status": "success",
                "message": "Device saved"
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return JsonResponse({"error": "Invalid request"})



from django.http import JsonResponse
from apps.communications.models import Notification

def latest_notification(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False})

    n = Notification.objects.filter(user=request.user).order_by("-created_at").first()

    if not n:
        return JsonResponse({"ok": False})

    return JsonResponse({
        "ok": True,
        "id": n.id,
        "title": n.title,
        "content": n.content,
    })
    
    
    
# apps/communications/views.py

from .models import Conversation, ChatMessage


def chat_view(request, convo_id):
    convo = Conversation.objects.get(id=convo_id)
    messages = convo.messages.order_by("created_at")

    return render(request, "communications/chat.html", {
        "conversation": convo,
        "messages": messages
    })


def send_chat_message(request):
    if request.method == "POST":
        convo_id = request.POST.get("conversation_id")
        content = request.POST.get("content")

        convo = Conversation.objects.get(id=convo_id)

        ChatMessage.objects.create(
            conversation=convo,
            sender=request.user,
            content=content
        )

        return redirect("chat_view", convo_id=convo.id)
    
    
    
def messaging_dashboard(request):
    conversations = Conversation.objects.all().order_by("-updated_at")

    selected_id = request.GET.get("convo")

    active_convo = None
    messages = []

    if selected_id:
        active_convo = Conversation.objects.get(id=selected_id)
        messages = active_convo.messages.order_by("created_at")

    return render(request, "communications/chat.html", {
        "conversations": conversations,
        "active_convo": active_convo,
        "messages": messages
    })
    
    
    
from django.shortcuts import redirect
from apps.communications.models import Conversation, ChatMessage
from apps.schools.models import School

def send_message(request):
    print("🔥 SEND MESSAGE VIEW HIT")

    if request.method == "POST":

        content = request.POST.get("content")
        school_id = request.POST.get("school")
        convo_id = request.POST.get("conversation_id")

        print("🔥 DEBUG:", content, school_id, convo_id)

        # 🔥 CASE 1: FIRST MESSAGE
        if school_id:
            school = School.objects.get(id=school_id)

            convo = Conversation.objects.filter(school=school).first()

            if not convo:
                convo = Conversation.objects.create(
                    school=school   # ✅ FIXED
                )
                print("✅ Conversation CREATED")

        # 🔥 CASE 2: EXISTING CHAT
        elif convo_id:
            convo = Conversation.objects.get(id=convo_id)

        else:
            print("❌ NO DATA")
            return redirect("/communications/chat/")

        # 🔥 SAVE MESSAGE
        ChatMessage.objects.create(
            conversation=convo,
            sender=request.user,
            content=content
        )

        print("✅ Message saved")

        return redirect(f"/communications/chat/?convo={convo.id}")
    
    
    
from django.shortcuts import render
from apps.communications.models import Conversation, ChatMessage
from apps.schools.models import School


from django.shortcuts import render
from apps.communications.models import Conversation, ChatMessage
from apps.schools.models import School

def chat_dashboard(request):
    from apps.communications.models import Conversation

    conversations = list(Conversation.objects.all().order_by("-id"))  # 🔥 FORCE EVALUATION

    print("🔥 COUNT:", len(conversations))  # DEBUG

    selected_id = request.GET.get("convo")

    active_convo = None
    messages = []

    if selected_id:
        active_convo = Conversation.objects.get(id=selected_id)
        messages = active_convo.messages.all().order_by("created_at")

    return render(request, "communications/chat.html", {
        "conversations": conversations,
        "active_convo": active_convo,
        "messages": messages,
        "schools": School.objects.all()
    })