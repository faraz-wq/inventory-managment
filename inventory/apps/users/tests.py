"""
Unit tests for Users API endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.departments.models import Department
from apps.locations.models import District, Mandal, Village
from apps.rbac.models import Role, Permission
from apps.users.models import UserRole

User = get_user_model()


class UserAPITestCase(TestCase):
    """Test cases for User API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create test department
        self.department = Department.objects.create(
            org_name="Test Department",
            org_shortname="TD",
            org_code="TD001",
            org_type="Government",
            contact_person_name="Test Contact"
        )

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

        # Create test role and permission
        self.permission = Permission.objects.create(
            name="test_permission",
            description="Test Permission"
        )
        self.role = Role.objects.create(
            name="Test Role",
            description="Test Role Description"
        )

    def test_user_registration_requires_admin(self):
        """Test that only admins can create users"""
        self.client.force_authenticate(user=self.regular_user)

        data = {
            "email": "newuser@test.com",
            "password": "newpass123",
            "name": "New User",
            "phone_no": "+91-9876543212",
            "dept": self.department.id,
            "location": self.village.id
        }

        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_user(self):
        """Test that admins can create users"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            "email": "newuser@test.com",
            "password": "newpass123",
            "name": "New User",
            "phone_no": "+91-9876543212",
            "dept": self.department.id,
            "location": self.village.id
        }

        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_get_current_user_profile(self):
        """Test getting current user's profile"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.regular_user.email)

    def test_update_current_user_profile(self):
        """Test updating current user's profile"""
        self.client.force_authenticate(user=self.regular_user)

        data = {"name": "Updated Name"}
        response = self.client.patch('/api/users/me/update/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.name, "Updated Name")

    def test_change_password(self):
        """Test changing password"""
        self.client.force_authenticate(user=self.regular_user)

        data = {
            "old_password": "user123",
            "new_password": "newpassword123"
        }

        response = self.client.post('/api/users/me/change-password/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify new password works
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password("newpassword123"))

    def test_change_password_with_wrong_old_password(self):
        """Test changing password with incorrect old password"""
        self.client.force_authenticate(user=self.regular_user)

        data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword123"
        }

        response = self.client.post('/api/users/me/change-password/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_user_roles(self):
        """Test listing roles for a user"""
        self.client.force_authenticate(user=self.admin_user)

        # Assign role to user
        UserRole.objects.create(user=self.regular_user, role=self.role)

        response = self.client.get(f'/api/users/{self.regular_user.staff_id}/roles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_assign_role_to_user(self):
        """Test assigning a role to a user"""
        self.client.force_authenticate(user=self.admin_user)

        data = {"role_id": self.role.id}
        response = self.client.post(
            f'/api/users/{self.regular_user.staff_id}/assign-role/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserRole.objects.filter(
                user=self.regular_user,
                role=self.role
            ).exists()
        )

    def test_remove_role_from_user(self):
        """Test removing a role from a user"""
        self.client.force_authenticate(user=self.admin_user)

        # First assign the role
        UserRole.objects.create(user=self.regular_user, role=self.role)

        response = self.client.delete(
            f'/api/users/{self.regular_user.staff_id}/remove-role/{self.role.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            UserRole.objects.filter(
                user=self.regular_user,
                role=self.role
            ).exists()
        )

    def test_list_users_requires_admin(self):
        """Test that only admins can list all users"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_users(self):
        """Test that admins can list all users"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_user_can_retrieve_own_profile(self):
        """Test that users can retrieve their own profile"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(f'/api/users/{self.regular_user.staff_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_jwt_token_obtain(self):
        """Test obtaining JWT token"""
        data = {
            "email": "user@test.com",
            "password": "user123"
        }

        response = self.client.post('/api/auth/token/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_token_refresh(self):
        """Test refreshing JWT token"""
        # First obtain token
        data = {
            "email": "user@test.com",
            "password": "user123"
        }

        token_response = self.client.post('/api/auth/token/', data)
        refresh_token = token_response.data['refresh']

        # Now refresh
        refresh_data = {"refresh": refresh_token}
        response = self.client.post('/api/auth/token/refresh/', refresh_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_public_registration(self):
        """Test that anonymous users can register via the public register endpoint"""
        # Ensure user does not already exist
        self.assertFalse(User.objects.filter(email='public@test.com').exists())

        data = {
            "name": "Public User",
            "email": "public@test.com",
            "password": "publicpass123",
            "phone_no": "+91-9000000000",
            "dept": self.department.id,
            "location": self.village.id
        }

        response = self.client.post('/api/auth/register/', data)
        # Depending on implementation this may return 201 or 200; expect created
        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))

        # Verify user created
        self.assertTrue(User.objects.filter(email='public@test.com').exists())

        # Verify the new user can obtain JWT tokens
        login_data = {"email": "public@test.com", "password": "publicpass123"}
        token_response = self.client.post('/api/auth/token/', login_data)
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', token_response.data)
        self.assertIn('refresh', token_response.data)

    def test_verify_accept_and_reject(self):
        """Test that a user with verify permission can accept and reject another user"""
        # Create permission and role for verifier
        verify_perm = Permission.objects.create(name='verify_users', description='Can verify users')
        verifier_role = Role.objects.create(name='District Verifier', description='Verifier role')
        # Assign permission to role
        from apps.rbac.models import RolePermission
        RolePermission.objects.create(role=verifier_role, permission=verify_perm)

        # Create a verifier user
        verifier = User.objects.create_user(
            email='verifier@test.com',
            password='verifier123',
            name='Verifier User',
            phone_no='+91-9000000001',
            dept=self.department,
            location=self.village
        )
        # Assign role to verifier
        UserRole.objects.create(user=verifier, role=verifier_role)

        # Create a target user with pending status
        target = User.objects.create_user(
            email='target@test.com',
            password='target123',
            name='Target User',
            phone_no='+91-9000000002',
            dept=self.department,
            location=self.village,
            verified_status='pending'
        )

        # Authenticate as verifier
        self.client.force_authenticate(user=verifier)

        # Accept action
        accept_data = {'action': 'accept', 'remarks': 'All good'}
        accept_resp = self.client.post(f'/api/users/{target.staff_id}/verify/', accept_data)
        self.assertEqual(accept_resp.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertEqual(target.verified_status, 'verified')

        # Set back to pending to test reject
        target.verified_status = 'pending'
        target.save()

        # Reject action
        reject_data = {'action': 'reject', 'remarks': 'Missing documents'}
        reject_resp = self.client.post(f'/api/users/{target.staff_id}/verify/', reject_data)
        self.assertEqual(reject_resp.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertEqual(target.verified_status, 'rejected')


class UserDistrictDepartmentFilteringTestCase(TestCase):
    """Test cases for district and department based filtering of users"""

    def setUp(self):
        """Set up test data for filtering tests"""
        self.client = APIClient()

        # Create two districts
        self.district1 = District.objects.create(
            district_name="District 1",
            district_code_ap="D01"
        )
        self.district2 = District.objects.create(
            district_name="District 2",
            district_code_ap="D02"
        )

        # Create mandals for each district
        self.mandal1 = Mandal.objects.create(
            mandal_name="Mandal 1",
            mandal_code_ap="M01",
            district=self.district1
        )
        self.mandal2 = Mandal.objects.create(
            mandal_name="Mandal 2",
            mandal_code_ap="M02",
            district=self.district2
        )

        # Create villages for each mandal
        self.village1 = Village.objects.create(
            village_name="Village 1",
            village_code_ap="V01",
            district=self.district1,
            mandal=self.mandal1
        )
        self.village2 = Village.objects.create(
            village_name="Village 2",
            village_code_ap="V02",
            district=self.district2,
            mandal=self.mandal2
        )

        # Create two departments
        self.dept1 = Department.objects.create(
            org_name="Department 1",
            org_shortname="D1",
            org_code="D001",
            org_type="Government",
            contact_person_name="Contact 1"
        )
        self.dept2 = Department.objects.create(
            org_name="Department 2",
            org_shortname="D2",
            org_code="D002",
            org_type="Government",
            contact_person_name="Contact 2"
        )

        # Create permissions
        self.view_users_permission = Permission.objects.create(
            name="view_users",
            description="View Users"
        )

        # Create roles
        self.district_verifier_role = Role.objects.create(
            name="District Verifier",
            description="Can verify users in their district"
        )
        self.data_entry_role = Role.objects.create(
            name="Data Entry Operator",
            description="Can enter data in their district"
        )
        self.dept_admin_role = Role.objects.create(
            name="Department Admin",
            description="Can manage users in their department"
        )

        # Assign view permission to all roles
        from apps.rbac.models import RolePermission
        for role in [self.district_verifier_role, self.data_entry_role, self.dept_admin_role]:
            RolePermission.objects.create(role=role, permission=self.view_users_permission)

        # Create District Verifier in district 1
        self.district_verifier1 = User.objects.create_user(
            email="verifier1@test.com",
            password="pass123",
            name="Verifier 1",
            dept=self.dept1,
            location=self.village1
        )
        UserRole.objects.create(user=self.district_verifier1, role=self.district_verifier_role)

        # Create Data Entry Operator in district 2
        self.data_entry2 = User.objects.create_user(
            email="dataentry2@test.com",
            password="pass123",
            name="Data Entry 2",
            dept=self.dept1,
            location=self.village2
        )
        UserRole.objects.create(user=self.data_entry2, role=self.data_entry_role)

        # Create Department Admin in dept 1
        self.dept_admin1 = User.objects.create_user(
            email="deptadmin1@test.com",
            password="pass123",
            name="Dept Admin 1",
            dept=self.dept1,
            location=self.village1
        )
        UserRole.objects.create(user=self.dept_admin1, role=self.dept_admin_role)

        # Create Department Admin in dept 2
        self.dept_admin2 = User.objects.create_user(
            email="deptadmin2@test.com",
            password="pass123",
            name="Dept Admin 2",
            dept=self.dept2,
            location=self.village1
        )
        UserRole.objects.create(user=self.dept_admin2, role=self.dept_admin_role)

        # Create superuser
        self.superuser = User.objects.create_superuser(
            email="super@test.com",
            password="pass123",
            name="Super User",
            dept=self.dept1,
            location=self.village1
        )

        # Create regular users in different districts and departments
        self.user_d1_dept1 = User.objects.create_user(
            email="user_d1_dept1@test.com",
            password="pass123",
            name="User D1 Dept1",
            dept=self.dept1,
            location=self.village1
        )
        self.user_d1_dept2 = User.objects.create_user(
            email="user_d1_dept2@test.com",
            password="pass123",
            name="User D1 Dept2",
            dept=self.dept2,
            location=self.village1
        )
        self.user_d2_dept1 = User.objects.create_user(
            email="user_d2_dept1@test.com",
            password="pass123",
            name="User D2 Dept1",
            dept=self.dept1,
            location=self.village2
        )
        self.user_d2_dept2 = User.objects.create_user(
            email="user_d2_dept2@test.com",
            password="pass123",
            name="User D2 Dept2",
            dept=self.dept2,
            location=self.village2
        )

    def test_district_verifier_sees_only_own_district_users(self):
        """District Verifier should only see users in their district"""
        self.client.force_authenticate(user=self.district_verifier1)
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get all user emails from response
        user_emails = [user['email'] for user in response.data['results']]

        # Should see users in district 1 (regardless of department)
        # This includes the district verifier themselves, dept admin 1, dept admin 2, and user_d1_dept1/2
        self.assertIn(self.user_d1_dept1.email, user_emails)
        self.assertIn(self.user_d1_dept2.email, user_emails)
        self.assertIn(self.district_verifier1.email, user_emails)

        # Should NOT see users in district 2
        self.assertNotIn(self.user_d2_dept1.email, user_emails)
        self.assertNotIn(self.user_d2_dept2.email, user_emails)
        self.assertNotIn(self.data_entry2.email, user_emails)

    def test_data_entry_operator_sees_only_own_district_users(self):
        """Data Entry Operator should only see users in their district"""
        self.client.force_authenticate(user=self.data_entry2)
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_emails = [user['email'] for user in response.data['results']]

        # Should see users in district 2 (regardless of department)
        self.assertIn(self.user_d2_dept1.email, user_emails)
        self.assertIn(self.user_d2_dept2.email, user_emails)
        self.assertIn(self.data_entry2.email, user_emails)

        # Should NOT see users in district 1
        self.assertNotIn(self.user_d1_dept1.email, user_emails)
        self.assertNotIn(self.user_d1_dept2.email, user_emails)
        self.assertNotIn(self.district_verifier1.email, user_emails)

    def test_department_admin_sees_only_own_department_users(self):
        """Department Admin should only see users in their department"""
        self.client.force_authenticate(user=self.dept_admin1)
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_emails = [user['email'] for user in response.data['results']]

        # Should see users in dept 1 (regardless of district)
        self.assertIn(self.user_d1_dept1.email, user_emails)
        self.assertIn(self.user_d2_dept1.email, user_emails)
        self.assertIn(self.dept_admin1.email, user_emails)

        # Should NOT see users in dept 2
        self.assertNotIn(self.user_d1_dept2.email, user_emails)
        self.assertNotIn(self.user_d2_dept2.email, user_emails)
        self.assertNotIn(self.dept_admin2.email, user_emails)

    def test_different_dept_admin_sees_different_users(self):
        """Different Department Admins see different sets of users"""
        self.client.force_authenticate(user=self.dept_admin2)
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_emails = [user['email'] for user in response.data['results']]

        # Should see users in dept 2 (regardless of district)
        self.assertIn(self.user_d1_dept2.email, user_emails)
        self.assertIn(self.user_d2_dept2.email, user_emails)
        self.assertIn(self.dept_admin2.email, user_emails)

        # Should NOT see users in dept 1
        self.assertNotIn(self.user_d1_dept1.email, user_emails)
        self.assertNotIn(self.user_d2_dept1.email, user_emails)
        self.assertNotIn(self.dept_admin1.email, user_emails)

    def test_superuser_sees_all_users(self):
        """Superuser should see all users regardless of district or department"""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should see all users created in setUp (9 total: 4 regular users +
        # 2 admins + 1 verifier + 1 data entry + 1 superuser)
        self.assertGreaterEqual(len(response.data['results']), 9)

    def test_district_verifier_cannot_access_other_district_user(self):
        """District Verifier cannot retrieve user from another district"""
        self.client.force_authenticate(user=self.district_verifier1)
        # Try to access user in district 2
        response = self.client.get(f'/api/users/{self.user_d2_dept1.staff_id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_dept_admin_cannot_access_other_dept_user(self):
        """Department Admin cannot retrieve user from another department"""
        self.client.force_authenticate(user=self.dept_admin1)
        # Try to access user in dept 2
        response = self.client.get(f'/api/users/{self.user_d1_dept2.staff_id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_without_location_sees_no_users(self):
        """District Verifier without location sees no users"""
        # Create user with no location
        user_no_location = User.objects.create_user(
            email="nolocation@test.com",
            password="pass123",
            name="No Location User",
            dept=self.dept1,
            location=None
        )
        UserRole.objects.create(user=user_no_location, role=self.district_verifier_role)

        self.client.force_authenticate(user=user_no_location)
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_user_without_department_sees_no_users(self):
        """Department Admin without department sees no users"""
        # Create user with no department
        user_no_dept = User.objects.create_user(
            email="nodept@test.com",
            password="pass123",
            name="No Dept User",
            dept=None,
            location=self.village1
        )
        UserRole.objects.create(user=user_no_dept, role=self.dept_admin_role)

        self.client.force_authenticate(user=user_no_dept)
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_district_filtering_with_search(self):
        """District filtering should work with search queries"""
        self.client.force_authenticate(user=self.district_verifier1)
        # Search for users in district 1
        response = self.client.get('/api/users/?search=D1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_emails = [user['email'] for user in response.data['results']]

        # Should find users with "D1" in their name who are in district 1
        self.assertIn(self.user_d1_dept1.email, user_emails)
        self.assertIn(self.user_d1_dept2.email, user_emails)

        # Should NOT find users from district 2 even if they match search
        self.assertNotIn(self.user_d2_dept1.email, user_emails)

    def test_department_filtering_with_location_filter(self):
        """Department filtering should work with location filters"""
        self.client.force_authenticate(user=self.dept_admin1)
        # Filter by village in district 1
        response = self.client.get(f'/api/users/?location={self.village1.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_emails = [user['email'] for user in response.data['results']]

        # Should only see users in dept 1 who are also in village 1
        self.assertIn(self.user_d1_dept1.email, user_emails)

        # Should NOT see users in dept 2 even if they're in village 1
        self.assertNotIn(self.user_d1_dept2.email, user_emails)

        # Should NOT see users in dept 1 but different village
        self.assertNotIn(self.user_d2_dept1.email, user_emails)
