from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .metrics import REQUEST_COUNT, REQUEST_DURATION_SECONDS, REQUEST_EXCEPTIONS


@csrf_exempt
@require_GET
def metrics_view(request):
    data = generate_latest()
    return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)
