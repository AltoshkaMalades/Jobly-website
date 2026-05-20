from django.shortcuts import render, get_object_or_404

from .models import Course, Lesson


def course_list(request):
    courses = Course.objects.prefetch_related('lessons').all()
    return render(request, 'learning/course_list.html', {'courses': courses})


def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('course'), pk=pk)
    return render(request, 'learning/lesson_detail.html', {'lesson': lesson})
