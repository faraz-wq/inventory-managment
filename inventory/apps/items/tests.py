""" items/tests.py
Unit tests for Items API endpoints - FULLY CORRECTED
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.departments.models import Department
from apps.locations.models import District, Mandal, Village
from apps.catalogue.models import ItemInfo, ItemAttribute
from apps.items.models import Item, ItemAttributeValue
from apps.rbac.models import Role, Permission, RolePermission
from apps.users.models import UserRole

User = get_user_model()


class ItemAPITestCase(TestCase):
    """Test cases for Item API endpoints"""

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
            item_name="Test Item",
            item_code="TI001",
            category="Electronics",
            resource_type="Hardware",
            perishability="Non-Perishable"
        )

        # FIXED: Use 'item_info' instead of 'item'
        self.attribute_definition = ItemAttribute.objects.create(
            item_info=self.item_info,
            key="color",
            datatype="string"
        )

        # Create test user with permissions
        # CORRECT
        self.user = User.objects.create_user(
            email="user@test.com",
            password="user123",
            name="Test User",
            phone_no="+91-9876543210",
            dept=self.department,
            location=self.village
        )
        self.user.save()  # ← Force save to get .id

        # Create permissions and assign to user
        self.view_permission = Permission.objects.create(
            name="view_items",
            description="View Items"
        )
        self.create_permission = Permission.objects.create(
            name="create_items",
            description="Create Items"
        )
        self.update_permission = Permission.objects.create(
            name="update_items",
            description="Update Items"
        )
        self.delete_permission = Permission.objects.create(
            name="delete_items",
            description="Delete Items"
        )
        self.verify_permission = Permission.objects.create(
            name="verify_items",
            description="Verify Items"
        )

        # Create role with permissions
        self.role = Role.objects.create(
            name="Item Manager",
            description="Can manage items"
        )
        for permission in [
            self.view_permission, self.create_permission,
            self.update_permission, self.delete_permission,
            self.verify_permission
        ]:
            RolePermission.objects.create(role=self.role, permission=permission)

        # Assign role to user
        UserRole.objects.create(user=self.user, role=self.role)

        # Create test item
        self.item = Item.objects.create(
            iteminfo=self.item_info,
            dept=self.department,
            geocode=self.village,
            user=self.user,
            created_by=self.user,
            status="pending"
        )

        # Create test attribute value
        self.attribute_value = ItemAttributeValue.objects.create(
            item=self.item,
            item_attribute=self.attribute_definition,
            value="red"
        )

    def test_list_items(self):
        """Test listing all items"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_item(self):
        """Test retrieving a specific item"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/items/{self.item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.item.id)
        self.assertIn('attribute_values', response.data)

    def test_create_item(self):
        """Test creating a new item"""
        self.client.force_authenticate(user=self.user)
        data = {
            "iteminfo": self.item_info.id,
            "dept": self.department.id,
            "geocode": self.village.id,
            "user": self.user.staff_id,
            "status": "pending"
        }
        response = self.client.post('/api/items/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 2)

    def test_create_item_with_attributes(self):
        """Test creating an item with attribute values"""
        self.client.force_authenticate(user=self.user)
        data = {
            "iteminfo": self.item_info.id,
            "dept": self.department.id,
            "geocode": self.village.id,
            "user": self.user.staff_id,
            "status": "pending",
            "attribute_values": [
                {
                    "item_attribute": self.attribute_definition.id,
                    "value": "blue"
                }
            ]
        }
        response = self.client.post('/api/items/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 2)
        new_item = Item.objects.latest('id')
        self.assertEqual(new_item.attribute_values.count(), 1)

    def test_update_item(self):
        """Test updating an item"""
        self.client.force_authenticate(user=self.user)
        data = {"operational_notes": "Updated notes"}
        response = self.client.patch(f'/api/items/{self.item.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.operational_notes, "Updated notes")

    def test_delete_item(self):
        """Test deleting an item"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/items/{self.item.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Item.objects.count(), 0)

    def test_verify_item(self):
        """Test verifying an item"""
        self.client.force_authenticate(user=self.user)
        data = {
            "status": "verified",
            "operational_notes": "Item verified"
        }
        response = self.client.patch(f'/api/items/{self.item.id}/verify/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, "verified")
        self.assertEqual(self.item.verified_by, self.user)

    def test_list_item_attributes(self):
        """Test listing attributes for an item"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/items/{self.item.id}/attributes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['value'], 'red')

    def test_add_item_attribute(self):
        """Test adding an attribute to an item"""
        self.client.force_authenticate(user=self.user)

        # FIXED: Use 'item_info'
        new_attr_def = ItemAttribute.objects.create(
            item_info=self.item_info,
            key="size",
            datatype="string"
        )

        data = {
            "item_attribute": new_attr_def.id,
            "value": "large"
        }
        response = self.client.post(f'/api/items/{self.item.id}/attributes/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.item.attribute_values.count(), 2)

    def test_update_item_attribute(self):
        """Test updating an item attribute"""
        self.client.force_authenticate(user=self.user)
        data = {"value": "blue"}
        response = self.client.patch(
            f'/api/items/{self.item.id}/attributes/{self.attribute_value.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.attribute_value.refresh_from_db()
        self.assertEqual(self.attribute_value.value, "blue")

    def test_delete_item_attribute(self):
        """Test deleting an item attribute"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            f'/api/items/{self.item.id}/attributes/{self.attribute_value.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ItemAttributeValue.objects.count(), 0)

    def test_filter_items_by_status(self):
        """Test filtering items by status"""
        self.client.force_authenticate(user=self.user)
        Item.objects.create(
            iteminfo=self.item_info,
            dept=self.department,
            geocode=self.village,
            user=self.user,
            created_by=self.user,
            status="verified"
        )
        response = self.client.get('/api/items/?status=verified')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_items_by_department(self):
        """Test filtering items by department"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/items/?dept={self.department.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_search_items(self):
        """Test searching items"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/items/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_items_without_permission_denied(self):
        """Test that users without permissions cannot access items"""
        user_no_perms = User.objects.create_user(
            email="noperms@test.com",
            password="user123",
            name="No Perms User",
            phone_no="+91-9876543219",
            dept=self.department,
            location=self.village
        )
        self.client.force_authenticate(user=user_no_perms)
        response = self.client.get('/api/items/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_geolocation_validation(self):
        """Test that latitude and longitude must be provided together"""
        self.client.force_authenticate(user=self.user)
        data = {
            "iteminfo": self.item_info.id,
            "dept": self.department.id,
            "latitude": 12.34,
        }
        response = self.client.post('/api/items/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('latitude and longitude', str(response.data))

    def test_invalid_status_transition(self):
        """Test invalid status transitions in verification"""
        self.item.status = 'available'
        self.item.save()
        self.client.force_authenticate(user=self.user)
        data = {
            "status": "verified",
            "operational_notes": "Trying invalid transition"
        }
        response = self.client.patch(f'/api/items/{self.item.id}/verify/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)