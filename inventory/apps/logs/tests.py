"""
Unit tests for Logs API endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.departments.models import Department
from apps.locations.models import District, Mandal, Village
from apps.logs.models import Log

User = get_user_model()


class LogAPITestCase(TestCase):
    """Test cases for Log API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create test location
        self.district = District.objects.create(
            district_name="Test District",
            district_code_ap="TD01"
        )
        self.mandal = Mandal.objects.create(
            mandal_name="Test Mandal",
            mandal_code_ap="TM01",
            district=self.district
        )
        self.village = Village.objects.create(
            village_name="Test Village",
            village_code_ap="TV01",
            district=self.district,
            mandal=self.mandal
        )

        # Create test department
        self.department = Department.objects.create(
            org_name="Test Department",
            org_shortname="TD",
            org_code="TD001",
            org_type="Government",
            contact_person_name="Test Contact"
        )

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="admin123",
            name="Admin User",
            phone_no="+91-9876543210",
            dept=self.department,
            location=self.village
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            email="user@test.com",
            password="user123",
            name="Regular User",
            phone_no="+91-9876543211",
            dept=self.department,
            location=self.village
        )

        # Create test logs
        self.log1 = Log.objects.create(
            user=self.regular_user,
            subject_type="Item",
            subject_id=1,
            action="create",
            status="success"
        )

        self.log2 = Log.objects.create(
            user=self.admin_user,
            subject_type="User",
            subject_id=2,
            action="update",
            status="success"
        )

    def test_list_logs_as_regular_user(self):
        """Test that regular users can only see their own logs"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get('/api/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Regular user should only see their own log
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['user'],
            self.regular_user.staff_id
        )

    def test_list_logs_as_admin(self):
        """Test that admins can see all logs"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin should see all logs
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_retrieve_log(self):
        """Test retrieving a specific log"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(f'/api/logs/{self.log1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.log1.id)

    def test_filter_logs_by_user(self):
        """Test filtering logs by user"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(
            f'/api/logs/?user={self.regular_user.staff_id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_logs_by_subject_type(self):
        """Test filtering logs by subject type"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/logs/?subject_type=Item')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_logs_by_action(self):
        """Test filtering logs by action"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/logs/?action=create')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_logs_by_status(self):
        """Test filtering logs by status"""
        self.client.force_authenticate(user=self.admin_user)

        # Create a failed log
        Log.objects.create(
            user=self.regular_user,
            subject_type="Item",
            subject_id=3,
            action="delete",
            status="failed"
        )

        response = self.client.get('/api/logs/?status=failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_logs(self):
        """Test searching logs"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/logs/?search=Item')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_ordering_logs_by_created_at(self):
        """Test ordering logs by created_at"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/logs/?ordering=-created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return logs in descending order
        results = response.data['results']
        if len(results) >= 2:
            self.assertGreaterEqual(
                results[0]['created_at'],
                results[1]['created_at']
            )

    def test_logs_are_readonly(self):
        """Test that logs cannot be created, updated, or deleted via API"""
        self.client.force_authenticate(user=self.admin_user)

        # Try to create
        data = {
            "user": self.regular_user.staff_id,
            "subject_type": "Test",
            "subject_id": 1,
            "action": "test",
            "status": "success"
        }
        response = self.client.post('/api/logs/', data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try to update
        data = {"status": "failed"}
        response = self.client.patch(f'/api/logs/{self.log1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try to delete
        response = self.client.delete(f'/api/logs/{self.log1.id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_log_contains_user_details(self):
        """Test that log response includes user details"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(f'/api/logs/{self.log1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('user_email', response.data)
        self.assertEqual(response.data['user_email'], self.regular_user.email)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access logs"""
        response = self.client.get('/api/logs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_see_other_user_logs(self):
        """Test that regular users cannot see other users' logs"""
        self.client.force_authenticate(user=self.regular_user)

        # Try to access admin's log
        response = self.client.get(f'/api/logs/{self.log2.id}/')
        # This should return 404 because the queryset is filtered
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_see_all_logs(self):
        """Test that admin can see logs from all users"""
        self.client.force_authenticate(user=self.admin_user)

        # Admin should be able to see regular user's log
        response = self.client.get(f'/api/logs/{self.log1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin should be able to see their own log
        response = self.client.get(f'/api/logs/{self.log2.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
