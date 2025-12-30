from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task CRUD operations."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark a task as completed."""
        task = self.get_object()
        task.mark_completed()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get all pending tasks."""
        pending_tasks = self.queryset.filter(status="pending")
        serializer = self.get_serializer(pending_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get task statistics."""
        total = self.queryset.count()
        pending = self.queryset.filter(status="pending").count()
        in_progress = self.queryset.filter(status="in_progress").count()
        completed = self.queryset.filter(status="completed").count()

        return Response(
            {
                "total": total,
                "pending": pending,
                "in_progress": in_progress,
                "completed": completed,
            }
        )
