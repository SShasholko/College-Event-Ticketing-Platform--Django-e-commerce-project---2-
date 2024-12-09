from . import views
from django.shortcuts import render


def custom_404(request, exception):
    """Renders a custom 404 error page using '404.html' template with a 404 status code."""
    return render(request, '404.html', status=404)