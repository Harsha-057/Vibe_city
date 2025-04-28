from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Keybind
from django.db.models import Q

# Create your views here.

@login_required
def keybinds_view(request):
    # Get all active keybinds
    keybinds = Keybind.objects.filter(is_active=True)
    
    # Get search query if any
    search_query = request.GET.get('search', '')
    if search_query:
        keybinds = keybinds.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(key__icontains=search_query) |
            Q(command__icontains=search_query)
        )
    
    # Get category filter if any
    category_filter = request.GET.get('category', '')
    if category_filter:
        keybinds = keybinds.filter(category=category_filter)
    
    # Get all unique categories for the filter dropdown
    categories = Keybind.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    
    # Group keybinds by category
    keybinds_by_category = {}
    for keybind in keybinds:
        if keybind.category not in keybinds_by_category:
            keybinds_by_category[keybind.category] = []
        keybinds_by_category[keybind.category].append(keybind)
    
    context = {
        'keybinds_by_category': keybinds_by_category,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    
    return render(request, 'keybinds/keybinds.html', context)
