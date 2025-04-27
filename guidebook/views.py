from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import GuidebookEntry

# Create your views here.

class GuidebookListView(ListView):
    model = GuidebookEntry
    template_name = 'guidebook/list.html'
    context_object_name = 'entries'
    
    def get_queryset(self):
        return GuidebookEntry.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group entries by category
        entries_by_category = {}
        for entry in context['entries']:
            if entry.category not in entries_by_category:
                entries_by_category[entry.category] = []
            entries_by_category[entry.category].append(entry)
        context['entries_by_category'] = entries_by_category
        return context

class GuidebookDetailView(DetailView):
    model = GuidebookEntry
    template_name = 'guidebook/detail.html'
    context_object_name = 'entry'
