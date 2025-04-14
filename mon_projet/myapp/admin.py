from django.contrib import admin
from .models import Ticket, Review, UserFollows, BlockRelation

admin.site.register(Ticket)
admin.site.register(Review)
admin.site.register(UserFollows)
@admin.register(BlockRelation)
class BlockRelationAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked')
