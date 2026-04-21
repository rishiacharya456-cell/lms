from django.urls import path
from .views import send_message_view
from .views import inbox_view
from .views import unread_count_api
from .views import register_device_view
from .views import save_device
from .views import latest_notification
from .views import send_message
from .views import chat_dashboard
urlpatterns = [
    path("send-message/", send_message_view, name="send_message"),
    path("inbox/", inbox_view, name="inbox"),
    path("unread-count/", unread_count_api, name="unread_count_api"),
    path("register-device/", register_device_view, name="register_device"),
    path("save-device/", save_device, name="save_device"),
    path("latest/", latest_notification, name="latest_notification"),
    path("send/", send_message, name="send_message"), 
    path("chat/", chat_dashboard, name="chat_dashboard"),
]