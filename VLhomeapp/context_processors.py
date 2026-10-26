from .models import Restaurant


def restaurant(request):
    return {"restaurant": Restaurant.objects.first()}