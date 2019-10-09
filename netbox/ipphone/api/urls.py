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

# Extensions
router.register(r'extension', views.ExtensionViewSet)
# router.register(r'dn', views.ExtensionViewSet)

# Lines
router.register(r'lines', views.LineViewSet)

app_name = 'ipphone-api'
urlpatterns = router.urls
