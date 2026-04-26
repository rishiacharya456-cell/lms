# apps/communications/services.py

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
import logging

from firebase_admin import messaging

from .models import Message, Notification, Device

logger = logging.getLogger(__name__)
User = get_user_model()


# 🎯 TARGET USERS
def get_target_users(target_type, school=None, section=None, class_name=None):

    qs = User.objects.filter(is_active=True)

    if target_type == "all_students":
        return qs.filter(role="student")

    elif target_type == "all_trainees":
        return qs.filter(role="trainee")

    elif target_type == "all_schools":
        return qs.filter(role="school_admin")

    elif target_type == "school_students" and school:
        return qs.filter(role="student", school=school)

    elif target_type == "class_students" and school and class_name:
        q = Q(role="student", school=school, student_class=class_name)
        if section:
            q &= Q(section=section)
        return qs.filter(q)

    return User.objects.none()


# 🔔 PUSH (chunked)
def send_push_to_users(users, title, body):

    # stream tokens instead of loading all at once
    tokens_qs = Device.objects.filter(
        user__in=users,
        is_active=True
    ).values_list("device_token", flat=True)

    tokens = list(tokens_qs)

    if not tokens:
        logger.warning("No device tokens found")
        return

    CHUNK = 500  # FCM limit

    success_total = 0
    fail_total = 0

    for i in range(0, len(tokens), CHUNK):
        batch = tokens[i:i+CHUNK]

        message = messaging.MulticastMessage(
            tokens=batch,
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

        success_total += response.success_count
        fail_total += response.failure_count

        # remove bad tokens
        for idx, resp in enumerate(response.responses):
            if not resp.success:
                bad = batch[idx]
                Device.objects.filter(device_token=bad).delete()

    logger.info(f"Push sent → success={success_total}, failed={fail_total}")


# 🚀 MAIN SEND
@transaction.atomic
def send_message(
    sender,
    title,
    content,
    target_type,
    school=None,
    section=None,
    class_name=None,
    priority="normal"
):

    # basic validation (don’t overdo it, just guard obvious cases)
    if target_type == "school_students" and not school:
        raise ValueError("school is required for school_students")

    if target_type == "class_students" and (not school or not class_name):
        raise ValueError("school + class_name required for class_students")

    # 1️⃣ Save message
    message = Message.objects.create(
        sender=sender,
        title=title,
        content=content,
        target_type=target_type,
        school=school,
        section=section,
        priority=priority
    )

    logger.info(f"Message created: {title}")

    # 2️⃣ Fetch users
    users = get_target_users(
        target_type,
        school=school,
        section=section,
        class_name=class_name
    )

    if not users.exists():
        logger.warning("No users found for target")
        return message

    # 3️⃣ Bulk notifications (iterator to reduce memory)
    now = timezone.now()

    notifications = (
        Notification(
            user=user,
            message=message,
            title=title,
            content=content,
            type="message",
            created_at=now
        )
        for user in users.iterator(chunk_size=1000)
    )

    Notification.objects.bulk_create(notifications, batch_size=1000)

    logger.info("Notifications created")

    # 4️⃣ Push
    try:
        send_push_to_users(users, title, content)
    except Exception as e:
        logger.error(f"Push error: {str(e)}")

    return message


# 🔵 MARK READ
def mark_notification_as_read(notification_id, user):

    updated = Notification.objects.filter(
        id=notification_id,
        user=user,
        is_read=False
    ).update(is_read=True)

    return bool(updated)


# 📩 LIST
def get_user_notifications(user):
    return Notification.objects.filter(user=user).order_by("-created_at")


# 🔴 COUNT
def get_unread_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()


# 📱 DEVICE REGISTER
def register_device(user, token, device_type="web"):

    if not token:
        return

    Device.objects.update_or_create(
        device_token=token,   # important: unique token
        defaults={
            "user": user,
            "device_type": device_type,
            "is_active": True
        }
    )