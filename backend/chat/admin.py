from django.contrib import admin
from chat.models import Thread, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    fields = ['sender', 'text', 'is_read', 'created']
    readonly_fields = ['created', ]


class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_participants', 'created', 'updated']
    list_display_links = ['id', 'get_participants']
    search_fields = ['participants__username', ]
    inlines = [MessageInline]

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'


class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'sender', 'thread', 'is_read', 'created']
    list_display_links = ['id', 'text']
    search_fields = ['sender__username', 'thread__id', 'text']
    list_filter = ['is_read', 'created']


admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message, MessageAdmin)
