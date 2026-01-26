from django.contrib import admin
from .models import (
    Company, Team, TeamMembership,
    CorporateTrack, CorporateMission, TeamTrackAssignment,
    TeamGoal
)

admin.site.register(Company)
admin.site.register(Team)
admin.site.register(TeamMembership)
admin.site.register(CorporateTrack)
admin.site.register(CorporateMission)
admin.site.register(TeamTrackAssignment)
admin.site.register(TeamGoal)

