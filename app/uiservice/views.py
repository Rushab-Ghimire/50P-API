"""
Core views for app.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def business(request):
    import json
    with open('./uiservice/ui/business/form.json', 'r') as f:
        o = json.load(f)
    return Response(o)
