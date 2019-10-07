from rest_framework import routers

from . import views


class IPPHONERootView(routers.APIRootView):
    """
    IPPHONE API root view
    """
    def get_view_name(self):
        return 'IPPHONE'


router = routers.DefaultRouter()
router.APIRootView = IPPHONERootView

# Field choices
router.register(r'_choices', views.IPPHONEFieldChoicesViewSet, basename='field-choice')

# Partitions
router.register(r'partitions', views.PartitionViewSet)

# IP addresses
router.register(r'dn', views.ExtensionViewSet)

app_name = 'ipphone-api'
urlpatterns = router.urls
