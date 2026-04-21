from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .models import Message, Notification, Device

User = get_user_model()


# 🔥 GET TARGET USERS
def get_target_users(target_type, school=None, section=None):

    if target_type == "all_students":
        return User.objects.filter(role="student", is_active=True)

    elif target_type == "all_trainees":
        return User.objects.filter(role="trainee", is_active=True)

    elif target_type == "all_schools":
        return User.objects.filter(role="school_admin", is_active=True)

    elif target_type == "school_students" and school:
        return User.objects.filter(
            role="student",
            school=school,
            is_active=True
        )

    elif target_type == "section_students" and school and section:
        return User.objects.filter(
            role="student",
            school=school,
            section=section,
            is_active=True
        )

    return User.objects.none()
from firebase_admin import messaging
from firebase_admin import messaging
from firebase_admin import messaging

def send_push_to_users(users, title, body):

    devices = Device.objects.filter(user__in=users, is_active=True)

    tokens = list(devices.values_list("device_token", flat=True))

    if not tokens:
        print("⚠️ No device tokens found")
        return

    message = messaging.MulticastMessage(
        tokens=tokens,
        notification=messaging.Notification(
            title=title,
            body=body[:120],
        ),
        data={
            "title": title,
            "body": body[:120],
        }
    )

    response = messaging.send_each_for_multicast(message)

    print(f"✅ Success: {response.success_count}")
    print(f"❌ Failed: {response.failure_count}")

    # 🔥 REMOVE INVALID TOKENS
    for idx, resp in enumerate(response.responses):
        if not resp.success:
            bad_token = tokens[idx]
            print("❌ Removing bad token:", bad_token)

            Device.objects.filter(device_token=bad_token).delete()





@transaction.atomic
def send_message(
    sender,
    title,
    content,
    target_type,
    school=None,
    section=None,
    priority="normal"
):

    # 1️⃣ Save Message
    message = Message.objects.create(
        sender=sender,
        title=title,
        content=content,
        target_type=target_type,
        school=school,
        section=section,
        priority=priority
    )

    print(f"📩 Message created: {title}")

    # 2️⃣ Get Target Users
    users = get_target_users(target_type, school, section)

    if not users.exists():
        print("⚠️ No users found for this target")
        return message

    print(f"👥 Target users count: {users.count()}")

    # 3️⃣ Bulk Notification Creation
    now = timezone.now()

    notifications = [
        Notification(
            user=user,
            message=message,
            title=title,
            content=content,
            type="message",
            created_at=now
        )
        for user in users
    ]

    Notification.objects.bulk_create(notifications, batch_size=1000)

    print(f"📦 Notifications created: {len(notifications)}")

    # 4️⃣ Push Notification (SAFE CALL)
    try:
        send_push_to_users(users, title, content)
        print("🔔 Push notification triggered")
    except Exception as e:
        print("❌ Push error:", str(e))

    return message


# 🔵 MARK AS READ
def mark_notification_as_read(notification_id, user):

    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=user
        )

        if not notification.is_read:
            notification.is_read = True
            notification.save()

        return True

    except Notification.DoesNotExist:
        return False


# 📩 GET ALL NOTIFICATIONS
def get_user_notifications(user):
    return Notification.objects.filter(user=user).order_by("-created_at")


# 🔴 UNREAD COUNT
def get_unread_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()


# 📱 REGISTER DEVICE TOKEN
def register_device(user, token, device_type="web"):

    if not token:
        return

    Device.objects.update_or_create(
        user=user,
        device_token=token,
        defaults={
            "device_type": device_type,
            "is_active": True
        }
    )