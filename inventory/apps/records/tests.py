"""
records/tests.py
Unit tests for Borrow Records API endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta

from apps.departments.models import Department
from apps.locations.models import District, Mandal, Village
from apps.catalogue.models import ItemInfo
from apps.items.models import Item
from apps.records.models import BorrowRecord
from apps.rbac.models import Role, Permission, RolePermission
from apps.users.models import UserRole

User = get_user_model()


class BorrowRecordAPITestCase(TestCase):
    """Test cases for BorrowRecord API endpoints"""

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

        # Create test item info (catalogue)
        self.item_info = ItemInfo.objects.create(
            item_name="Test Laptop",
            item_code="TL001",
            category="Electronics",
            resource_type="Hardware",
            perishability="Non-Perishable"
        )

        # Create test user with permissions
        self.user = User.objects.create_user(
            email="user@test.com",
            password="user123",
            name="Test User",
            phone_no="+91-9876543210",
            dept=self.department,
            location=self.village
        )
        self.user.save()

        # Create test borrower user
        self.borrower_user = User.objects.create_user(
            email="borrower@test.com",
            password="borrower123",
            name="John Doe",
            phone_no="+91-9876543211",
            dept=self.department,
            location=self.village
        )
        self.borrower_user.save()

        # Create permissions
        self.view_permission = Permission.objects.create(
            name="view_borrow_records",
            description="View Borrow Records"
        )
        self.create_permission = Permission.objects.create(
            name="create_borrow_records",
            description="Create Borrow Records"
        )
        self.update_permission = Permission.objects.create(
            name="update_borrow_records",
            description="Update Borrow Records"
        )
        self.delete_permission = Permission.objects.create(
            name="delete_borrow_records",
            description="Delete Borrow Records"
        )

        # Create role with permissions
        self.role = Role.objects.create(
            name="Records Manager",
            description="Can manage borrow records"
        )
        for permission in [
            self.view_permission, self.create_permission,
            self.update_permission, self.delete_permission
        ]:
            RolePermission.objects.create(role=self.role, permission=permission)

        # Assign role to user
        UserRole.objects.create(user=self.user, role=self.role)

        # Create test items
        self.available_item = Item.objects.create(
            iteminfo=self.item_info,
            dept=self.department,
            geocode=self.village,
            user=self.user,
            created_by=self.user,
            status="available"
        )

        self.borrowed_item = Item.objects.create(
            iteminfo=self.item_info,
            dept=self.department,
            geocode=self.village,
            user=self.user,
            created_by=self.user,
            status="borrowed"
        )

        # Create test borrow record
        self.borrow_record = BorrowRecord.objects.create(
            item=self.borrowed_item,
            borrower=self.borrower_user,
            expected_return_date=date.today() + timedelta(days=7),
            borrow_notes="Test borrow",
            issued_by=self.user,
            status="borrowed"
        )

    def test_list_borrow_records(self):
        """Test listing all borrow records"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_borrow_record(self):
        """Test retrieving a specific borrow record"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/records/{self.borrow_record.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.borrow_record.id)
        self.assertEqual(response.data['borrower'], self.borrower_user.staff_id)
        self.assertEqual(response.data['borrower_name'], "John Doe")

    def test_create_borrow_record(self):
        """Test creating a new borrow record (issuing item)"""
        # Create another borrower user
        another_borrower = User.objects.create_user(
            email="jane@test.com",
            password="jane123",
            name="Jane Smith",
            phone_no="+91-9876543212",
            dept=self.department,
            location=self.village
        )

        self.client.force_authenticate(user=self.user)
        data = {
            "item": self.available_item.id,
            "borrower": another_borrower.staff_id,
            "expected_return_date": str(date.today() + timedelta(days=14)),
            "borrow_notes": "Borrowing for project work"
        }
        response = self.client.post('/api/records/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BorrowRecord.objects.count(), 2)

        # Verify item status was updated
        self.available_item.refresh_from_db()
        self.assertEqual(self.available_item.status, "borrowed")

    def test_create_borrow_record_validates_item_available(self):
        """Test that creating a borrow record fails if item is already borrowed"""
        self.client.force_authenticate(user=self.user)
        data = {
            "item": self.borrowed_item.id,
            "borrower": self.borrower_user.staff_id,
            "expected_return_date": str(date.today() + timedelta(days=14)),
        }
        response = self.client.post('/api/records/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already borrowed', str(response.data).lower())

    def test_create_borrow_record_validates_borrower_active(self):
        """Test that inactive borrowers cannot borrow items"""
        self.client.force_authenticate(user=self.user)

        # Create an inactive user
        inactive_user = User.objects.create_user(
            email="inactive@test.com",
            password="inactive123",
            name="Inactive User",
            phone_no="+91-9999999999",
            dept=self.department,
            location=self.village,
            active=False
        )

        data = {
            "item": self.available_item.id,
            "borrower": inactive_user.staff_id,
            "expected_return_date": str(date.today() + timedelta(days=14)),
        }
        response = self.client.post('/api/records/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('active', str(response.data).lower())

    def test_update_borrow_record(self):
        """Test updating a borrow record"""
        self.client.force_authenticate(user=self.user)
        data = {
            "borrow_notes": "Updated notes"
        }
        response = self.client.patch(f'/api/records/{self.borrow_record.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrow_record.refresh_from_db()
        self.assertEqual(self.borrow_record.borrow_notes, "Updated notes")

    def test_delete_borrow_record(self):
        """Test deleting a borrow record"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/records/{self.borrow_record.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BorrowRecord.objects.count(), 0)

    def test_return_item(self):
        """Test marking an item as returned"""
        self.client.force_authenticate(user=self.user)
        data = {
            "return_notes": "Item returned in good condition"
        }
        response = self.client.post(f'/api/records/{self.borrow_record.id}/return/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify borrow record was updated
        self.borrow_record.refresh_from_db()
        self.assertEqual(self.borrow_record.status, "returned")
        self.assertIsNotNone(self.borrow_record.actual_return_date)
        self.assertEqual(self.borrow_record.return_notes, "Item returned in good condition")
        self.assertEqual(self.borrow_record.received_by, self.user)

        # Verify item status was updated
        self.borrowed_item.refresh_from_db()
        self.assertEqual(self.borrowed_item.status, "available")

    def test_return_already_returned_item_fails(self):
        """Test that returning an already returned item fails"""
        self.borrow_record.status = 'returned'
        self.borrow_record.actual_return_date = timezone.now()
        self.borrow_record.save()

        self.client.force_authenticate(user=self.user)
        data = {"return_notes": "Trying to return again"}
        response = self.client.post(f'/api/records/{self.borrow_record.id}/return/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already been returned', str(response.data))

    def test_item_history(self):
        """Test getting borrow history for a specific item"""
        # Create another borrower user
        another_borrower = User.objects.create_user(
            email="another@test.com",
            password="another123",
            name="Another Borrower",
            phone_no="+91-9876543213",
            dept=self.department,
            location=self.village
        )

        # Create another borrow record for the same item
        self.borrowed_item.status = 'available'
        self.borrowed_item.save()

        BorrowRecord.objects.create(
            item=self.borrowed_item,
            borrower=another_borrower,
            issued_by=self.user,
            status="borrowed"
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/records/item/{self.borrowed_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_borrower_history(self):
        """Test getting borrow history for a specific borrower"""
        # Create another borrow record for the same borrower
        another_item = Item.objects.create(
            iteminfo=self.item_info,
            dept=self.department,
            geocode=self.village,
            user=self.user,
            created_by=self.user,
            status="available"
        )

        BorrowRecord.objects.create(
            item=another_item,
            borrower=self.borrower_user,  # Same borrower
            issued_by=self.user,
            status="borrowed"
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/records/borrower/{self.borrower_user.staff_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_status(self):
        """Test filtering borrow records by status"""
        # Create another borrower for the returned record
        returned_borrower = User.objects.create_user(
            email="returned@test.com",
            password="returned123",
            name="Returned Borrower",
            phone_no="+91-9876543214",
            dept=self.department,
            location=self.village
        )

        # Create a returned record
        returned_record = BorrowRecord.objects.create(
            item=self.available_item,
            borrower=returned_borrower,
            issued_by=self.user,
            status="returned",
            actual_return_date=timezone.now()
        )

        self.client.force_authenticate(user=self.user)

        # Filter for borrowed
        response = self.client.get('/api/records/?status=borrowed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Filter for returned
        response = self.client.get('/api/records/?status=returned')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_borrower_department(self):
        """Test filtering borrow records by borrower's department"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/records/?borrower__dept={self.department.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_search_by_borrower_name(self):
        """Test searching borrow records by borrower name"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/records/?search=John')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['borrower_name'], "John Doe")

    def test_search_by_email(self):
        """Test searching borrow records by borrower email"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/records/?search=borrower@test.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_search_by_phone(self):
        """Test searching borrow records by borrower phone number"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/records/?search=9876543211')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_without_permission_denied(self):
        """Test that users without permissions cannot access borrow records"""
        user_no_perms = User.objects.create_user(
            email="noperms@test.com",
            password="user123",
            name="No Perms User",
            phone_no="+91-9876543219",
            dept=self.department,
            location=self.village
        )
        self.client.force_authenticate(user=user_no_perms)
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access borrow records"""
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrow_record_sets_issued_by(self):
        """Test that creating a borrow record automatically sets issued_by"""
        # Create a new borrower user
        new_borrower = User.objects.create_user(
            email="autoissue@test.com",
            password="autoissue123",
            name="Auto Issue Test",
            phone_no="+91-9999999999",
            dept=self.department,
            location=self.village
        )

        self.client.force_authenticate(user=self.user)
        data = {
            "item": self.available_item.id,
            "borrower": new_borrower.staff_id,
        }
        response = self.client.post('/api/records/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        record = BorrowRecord.objects.get(borrower=new_borrower)
        self.assertEqual(record.issued_by, self.user)

    def test_ordering_by_borrow_date(self):
        """Test ordering borrow records by borrow date"""
        # Create a new borrower user
        new_borrower = User.objects.create_user(
            email="newborrower@test.com",
            password="newborrower123",
            name="New Borrower",
            phone_no="+91-8888888888",
            dept=self.department,
            location=self.village
        )

        self.client.force_authenticate(user=self.user)

        # Create another record (will have a later borrow_date)
        BorrowRecord.objects.create(
            item=self.available_item,
            borrower=new_borrower,
            issued_by=self.user,
            status="borrowed"
        )

        # Default ordering should be newest first
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertGreater(
            results[0]['borrow_date'],
            results[1]['borrow_date']
        )
