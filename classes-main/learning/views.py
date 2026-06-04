from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from .models import Course, Lesson

# Cache configuration
COURSE_LIST_CACHE_TTL = 60 * 15  # 15 minutes
LESSON_DETAIL_CACHE_TTL = 60 * 30  # 30 minutes


def course_list(request):
    """
    Кэшированный список всех курсов.
    TTL: 15 минут
    """
    cache_key = 'learning:course_list_all'
    cached_courses = cache.get(cache_key)
    
    if cached_courses is not None:
        return render(request, 'learning/course_list.html', {'courses': cached_courses})
    
    # If not in cache, fetch from database
    courses = list(Course.objects.prefetch_related('lessons').all())
    
    # Store in cache
    cache.set(cache_key, courses, COURSE_LIST_CACHE_TTL)
    
    return render(request, 'learning/course_list.html', {'courses': courses})


def lesson_detail(request, pk):
    """
    Кэшированная детальная страница урока.
    TTL: 30 минут
    """
    cache_key = f'learning:lesson_detail:{pk}'
    cached_lesson = cache.get(cache_key)
    
    if cached_lesson is not None:
        return render(request, 'learning/lesson_detail.html', {'lesson': cached_lesson})
    
    lesson = get_object_or_404(Lesson.objects.select_related('course'), pk=pk)
    
    # Store in cache
    cache.set(cache_key, lesson, LESSON_DETAIL_CACHE_TTL)
    
    return render(request, 'learning/lesson_detail.html', {'lesson': lesson})
