from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from studious_engine.users.api.views import UserViewSet
from experiences.api import (
    PowerViewSet, PlayerPowerViewSet,
    ExperienceViewSet, PlayerExperienceViewSet,
    ExperienceInstanceViewSet, ExperienceParticipationViewSet
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

# Register experiences app API endpoints
router.register("powers", PowerViewSet)
router.register("player-powers", PlayerPowerViewSet)
router.register("experiences", ExperienceViewSet)
router.register("player-experiences", PlayerExperienceViewSet)
router.register("experience-instances", ExperienceInstanceViewSet)
router.register("experience-participations", ExperienceParticipationViewSet)

app_name = "api"
urlpatterns = router.urls
