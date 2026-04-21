from django.contrib import admin
from .models import Syllabus, Phase, Topic, TopicUnlock

admin.site.register(Syllabus)
admin.site.register(Phase)
admin.site.register(Topic)
admin.site.register(TopicUnlock)