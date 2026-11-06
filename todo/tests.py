from django.test import TestCase
from django.contrib.auth.models import User

from .models import Task


class TaskWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="StrongPass123!")
        self.other_user = User.objects.create_user(username="other", password="StrongPass123!")
        self.client.login(username="owner", password="StrongPass123!")

    def test_create_task_assigns_logged_in_user(self):
        response = self.client.post("/", {"title": "Write tests"}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task added successfully.")
        task = Task.objects.get(title="Write tests")
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.completed)

    def test_blank_task_is_not_created(self):
        response = self.client.post("/", {"title": "   "})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.exists())
        self.assertContains(response, "This field is required.")

    def test_search_and_status_filters(self):
        Task.objects.create(user=self.user, title="Write report")
        Task.objects.create(user=self.user, title="Ship release", completed=True)
        Task.objects.create(user=self.other_user, title="Private task")

        response = self.client.get("/", {"search": "write", "status": "pending"})

        self.assertContains(response, "Write report")
        self.assertNotContains(response, "Ship release")
        self.assertNotContains(response, "Private task")

        response = self.client.get("/", {"status": "completed"})

        self.assertContains(response, "Ship release")
        self.assertNotContains(response, "Write report")
        self.assertNotContains(response, "Private task")

    def test_dashboard_statistics_are_dynamic_and_user_scoped(self):
        Task.objects.create(user=self.user, title="Pending item")
        Task.objects.create(user=self.user, title="Finished item", completed=True)
        Task.objects.create(user=self.other_user, title="Another user's item")

        response = self.client.get("/")

        self.assertEqual(response.context["total_tasks"], 2)
        self.assertEqual(response.context["pending_tasks"], 1)
        self.assertEqual(response.context["completed_tasks"], 1)
        self.assertContains(response, "Pending item")
        self.assertContains(response, "Finished item")
        self.assertNotContains(response, "Another user&#x27;s item")

    def test_empty_dashboard_shows_add_task_action(self):
        response = self.client.get("/")

        self.assertContains(response, "No tasks yet. Start organizing your day!")
        self.assertContains(response, 'href="#add-task"')

    def test_update_task_validates_and_saves_form(self):
        task = Task.objects.create(user=self.user, title="Old title")

        response = self.client.post(
            f"/update/{task.pk}/",
            {"title": "New title", "completed": "on"},
        )

        self.assertRedirects(response, "/")
        task.refresh_from_db()
        self.assertEqual(task.title, "New title")
        self.assertTrue(task.completed)

    def test_task_cannot_be_viewed_or_updated_by_another_user(self):
        task = Task.objects.create(user=self.other_user, title="Private task")

        self.assertEqual(self.client.get(f"/update/{task.pk}/").status_code, 404)
        self.assertEqual(
            self.client.post(f"/update/{task.pk}/", {"title": "Changed"}).status_code,
            404,
        )

    def test_delete_requires_confirmation_and_post(self):
        task = Task.objects.create(user=self.user, title="Remove me")
        other_task = Task.objects.create(user=self.other_user, title="Private task")

        response = self.client.get(f"/delete/{task.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())
        self.assertContains(response, "Are you sure")
        self.assertEqual(self.client.post(f"/delete/{other_task.pk}/").status_code, 404)
        self.assertEqual(self.client.put(f"/delete/{task.pk}/").status_code, 405)

        response = self.client.post(f"/delete/{task.pk}/")

        self.assertRedirects(response, "/")
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_toggle_is_post_only_and_user_scoped(self):
        task = Task.objects.create(user=self.user, title="Toggle me")

        self.assertEqual(self.client.get(f"/toggle/{task.pk}/").status_code, 405)
        self.client.post(f"/toggle/{task.pk}/")
        task.refresh_from_db()
        self.assertTrue(task.completed)

        other_task = Task.objects.create(user=self.other_user, title="Private task")
        self.assertEqual(self.client.post(f"/toggle/{other_task.pk}/").status_code, 404)

    def test_logout_is_post_only(self):
        self.assertEqual(self.client.get("/logout/").status_code, 405)

        response = self.client.post("/logout/")

        self.assertRedirects(response, "/login/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class AuthenticationWorkflowTests(TestCase):
    def test_signup_validation_and_login(self):
        response = self.client.post(
            "/signup/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass123!",
                "password2": "DifferentPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

        response = self.client.post(
            "/signup/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, "/")
        user = User.objects.get(username="newuser")
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_login_rejects_invalid_password_and_accepts_valid_password(self):
        User.objects.create_user(username="member", password="StrongPass123!")

        response = self.client.post(
            "/login/",
            {"username": "member", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        response = self.client.post(
            "/login/",
            {"username": "member", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)
