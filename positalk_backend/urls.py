from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cabinet/', include("cabinet.urls")),
    path('wellness/', include("wellness.urls")),
    path('store/', include("psy_store.urls")),
    path('sales/', include("sales.urls")),
    path('session/', include("session.urls")),
    path('tinymce/', include('tinymce.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]+ debug_toolbar_urls()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)