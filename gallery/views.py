from django.shortcuts import render
from .models import GalleryImage

def gallery_view(request):
    # Get all active gallery images
    images = GalleryImage.objects.filter(is_active=True)
    
    # Get category filter if any
    category = request.GET.get('category', 'all')
    if category != 'all':
        images = images.filter(category=category)
    
    # Use model choices for categories
    categories = GalleryImage.CATEGORY_CHOICES
    
    # Group images by category
    images_by_category = {}
    for image in images:
        if image.category not in images_by_category:
            images_by_category[image.category] = []
        images_by_category[image.category].append(image)
    
    context = {
        'images': images,
        'images_by_category': images_by_category,
        'categories': categories,  # Now a list of (value, display) tuples
        'current_category': category,
    }
    
    return render(request, 'gallery/gallery.html', context) 