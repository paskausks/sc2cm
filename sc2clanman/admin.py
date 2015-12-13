#!/bin/env python3

from django.contrib import admin
from . modeladmins import clanmember, synclog
from . import models


# Register your models here.
admin.site.register(models.ClanMember, clanmember.ClanMemberAdmin)
admin.site.register(models.SyncLog, synclog.SyncLogAdmin)
admin.site.register(models.PracticeEvent)
admin.site.register(models.PracticeAttendant)
