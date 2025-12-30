from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task


class TaskModelTest(TestCase):
    """Tests for the Task model."""

    def test_create_task(self):
        """Test creating a task with default values."""
        task = Task.objects.create(title="Test Task")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.description, "")

    def test_create_task_with_all_fields(self):
        """Test creating a task with all fields specified."""
        task = Task.objects.create(
            title="Complete Task",
            description="This is a complete task",
            status="in_progress",
        )
        self.assertEqual(task.title, "Complete Task")
        self.assertEqual(task.description, "This is a complete task")
        self.assertEqual(task.status, "in_progress")

    def test_task_str_representation(self):
        """Test the string representation of a task."""
        task = Task.objects.create(title="String Test Task")
        self.assertEqual(str(task), "String Test Task")

    def test_mark_completed(self):
        """Test marking a task as completed."""
        task = Task.objects.create(title="Task to Complete")
        self.assertEqual(task.status, "pending")

        task.mark_completed()
        task.refresh_from_db()

        self.assertEqual(task.status, "completed")

    def test_task_ordering(self):
        """Test that tasks are ordered by created_at descending."""
        task1 = Task.objects.create(title="First Task")
        task2 = Task.objects.create(title="Second Task")
        task3 = Task.objects.create(title="Third Task")

        tasks = list(Task.objects.all())
        self.assertEqual(tasks[0], task3)
        self.assertEqual(tasks[1], task2)
        self.assertEqual(tasks[2], task1)

    def test_task_timestamps(self):
        """Test that created_at and updated_at are set automatically."""
        task = Task.objects.create(title="Timestamp Task")
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)


class TaskAPITest(APITestCase):
    """Tests for the Task API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.task1 = Task.objects.create(
            title="API Task 1", description="First API task", status="pending"
        )
        self.task2 = Task.objects.create(
            title="API Task 2", description="Second API task", status="in_progress"
        )
        self.task3 = Task.objects.create(
            title="API Task 3", description="Third API task", status="completed"
        )

    def test_list_tasks(self):
        """Test listing all tasks."""
        url = reverse("task-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_create_task(self):
        """Test creating a task via API."""
        url = reverse("task-list")
        data = {"title": "New API Task", "description": "Created via API"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 4)
        self.assertEqual(response.data["title"], "New API Task")
        self.assertEqual(response.data["status"], "pending")

    def test_retrieve_task(self):
        """Test retrieving a single task."""
        url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "API Task 1")

    def test_update_task(self):
        """Test updating a task via API."""
        url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        data = {"title": "Updated Task", "description": "Updated description"}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Updated Task")

    def test_partial_update_task(self):
        """Test partially updating a task via API."""
        url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        data = {"status": "in_progress"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, "in_progress")

    def test_delete_task(self):
        """Test deleting a task via API."""
        url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 2)

    def test_complete_action(self):
        """Test the complete action endpoint."""
        url = reverse("task-complete", kwargs={"pk": self.task1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, "completed")

    def test_pending_action(self):
        """Test the pending tasks filter endpoint."""
        url = reverse("task-pending")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "API Task 1")

    def test_stats_action(self):
        """Test the stats endpoint."""
        url = reverse("task-stats")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 3)
        self.assertEqual(response.data["pending"], 1)
        self.assertEqual(response.data["in_progress"], 1)
        self.assertEqual(response.data["completed"], 1)

    def test_create_task_without_title(self):
        """Test that creating a task without title fails."""
        url = reverse("task-list")
        data = {"description": "Task without title"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_nonexistent_task(self):
        """Test retrieving a task that doesn't exist."""
        url = reverse("task-detail", kwargs={"pk": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TaskSerializerTest(TestCase):
    """Tests for the Task serializer."""

    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        from .serializers import TaskSerializer

        task = Task.objects.create(title="Serializer Test")
        serializer = TaskSerializer(task)

        expected_fields = {
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serializer_read_only_fields(self):
        """Test that read-only fields cannot be set on creation."""
        from .serializers import TaskSerializer

        data = {
            "title": "Read Only Test",
            "id": 999,
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        task = serializer.save()
        self.assertNotEqual(task.id, 999)
