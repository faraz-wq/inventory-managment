"""
Unit tests for RBAC API endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.departments.models import Department
from apps.locations.models import District, Mandal, Village
from apps.rbac.models import Role, Permission, RolePermission

User = get_user_model()


class RBACAPITestCase(TestCase):
    """Test cases for RBAC (Role and Permission) API endpoints"""

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

        # Create test permission and role
        self.permission = Permission.objects.create(
            name="test_permission",
            description="Test Permission"
        )
        self.role = Role.objects.create(
            name="Test Role",
            description="Test Role Description"
        )

    def test_list_roles_requires_admin(self):
        """Test that only admins can list roles"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get('/api/rbac/roles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_roles(self):
        """Test that admins can list roles"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/rbac/roles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_create_role(self):
        """Test creating a new role"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            "name": "New Role",
            "description": "New Role Description"
        }

        response = self.client.post('/api/rbac/roles/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Role.objects.count(), 2)

    def test_update_role(self):
        """Test updating a role"""
        self.client.force_authenticate(user=self.admin_user)

        data = {"description": "Updated Description"}
        response = self.client.patch(f'/api/rbac/roles/{self.role.id}/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.role.refresh_from_db()
        self.assertEqual(self.role.description, "Updated Description")

    def test_delete_role(self):
        """Test deleting a role"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(f'/api/rbac/roles/{self.role.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Role.objects.count(), 0)

    def test_assign_permission_to_role(self):
        """Test assigning a permission to a role"""
        self.client.force_authenticate(user=self.admin_user)

        data = {"permission_id": self.permission.id}
        response = self.client.post(
            f'/api/rbac/roles/{self.role.id}/assign-permission/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            RolePermission.objects.filter(
                role=self.role,
                permission=self.permission
            ).exists()
        )

    def test_remove_permission_from_role(self):
        """Test removing a permission from a role"""
        self.client.force_authenticate(user=self.admin_user)

        # First assign the permission
        RolePermission.objects.create(
            role=self.role,
            permission=self.permission
        )

        response = self.client.delete(
            f'/api/rbac/roles/{self.role.id}/remove-permission/{self.permission.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            RolePermission.objects.filter(
                role=self.role,
                permission=self.permission
            ).exists()
        )

    def test_list_role_permissions(self):
        """Test listing permissions for a role"""
        self.client.force_authenticate(user=self.admin_user)

        # Assign permission to role
        RolePermission.objects.create(
            role=self.role,
            permission=self.permission
        )

        response = self.client.get(
            f'/api/rbac/roles/{self.role.id}/permissions/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_permissions(self):
        """Test listing all permissions"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/rbac/permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_create_permission(self):
        """Test creating a new permission"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            "name": "new_permission",
            "description": "New Permission Description"
        }

        response = self.client.post('/api/rbac/permissions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Permission.objects.count(), 2)

    def test_update_permission(self):
        """Test updating a permission"""
        self.client.force_authenticate(user=self.admin_user)

        data = {"description": "Updated Permission Description"}
        response = self.client.patch(
            f'/api/rbac/permissions/{self.permission.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.permission.refresh_from_db()
        self.assertEqual(
            self.permission.description,
            "Updated Permission Description"
        )

    def test_delete_permission(self):
        """Test deleting a permission"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(
            f'/api/rbac/permissions/{self.permission.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Permission.objects.count(), 0)

    def test_search_roles(self):
        """Test searching roles"""
        self.client.force_authenticate(user=self.admin_user)

        Role.objects.create(name="Admin Role", description="Admin Description")

        response = self.client.get('/api/rbac/roles/?search=Admin')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_permissions(self):
        """Test searching permissions"""
        self.client.force_authenticate(user=self.admin_user)

        Permission.objects.create(
            name="admin_permission",
            description="Admin Permission"
        )

        response = self.client.get('/api/rbac/permissions/?search=admin')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
