from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.departments.models import Department
from apps.locations.models import District, Mandal, Village
from apps.catalogue.models import ItemInfo, ItemAttribute
from apps.rbac.models import Role, Permission, RolePermission
from apps.users.models import UserRole

User = get_user_model()

class CatalogueAPITestCase(TestCase):
    """Test cases for Catalogue (ItemInfo) API endpoints"""

    def setUp(self):
        """Set up test data according to ItemInfo and ItemAttribute schemas"""
        self.client = APIClient()

        # Create test location (required for User model)
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

        # Create test department (required for User model)
        self.department = Department.objects.create(
            org_name="Test Department",
            org_shortname="TD",
            org_code="TD001",
            org_type="Government",
            contact_person_name="Test Contact"
        )

        # Create test user
        self.user = User.objects.create_user(
            email="user@test.com",
            password="user123",
            name="Test User",
            phone_no="+91-9876543210",
            dept=self.department,
            location=self.village
        )
        self.user.save()

        # Create permissions for catalogue with names matching has_permission identifiers
        self.view_permission = Permission.objects.create(
            name="view_catalogue",
            description="View Catalogue Items"
        )
        self.create_permission = Permission.objects.create(
            name="create_catalogue",
            description="Create Catalogue Items"
        )
        self.update_permission = Permission.objects.create(
            name="update_catalogue",
            description="Update Catalogue Items"
        )
        self.delete_permission = Permission.objects.create(
            name="delete_catalogue",
            description="Delete Catalogue Items"
        )

        # Create role with permissions
        self.role = Role.objects.create(
            name="Catalogue Manager",
            description="Can manage catalogue items"
        )
        for permission in [
            self.view_permission,
            self.create_permission,
            self.update_permission,
            self.delete_permission
        ]:
            RolePermission.objects.create(role=self.role, permission=permission)

        # Assign role to user
        UserRole.objects.create(user=self.user, role=self.role)

        # Create test item_info (aligned with ItemInfo model, no department)
        self.item_info = ItemInfo.objects.create(
            item_name="Test Item",
            item_code="TI001",
            category="Electronics",
            resource_type="Hardware",
            perishability="Non-Perishable",
            unit="Piece",
            tags="test, item",
            activity_name="Testing"
        )

        # Create test item_attribute
        self.item_attribute = ItemAttribute.objects.create(
            item_info=self.item_info,
            key="ram",
            datatype="string"
        )

        # Authenticate client
        self.client.force_authenticate(user=self.user)

    def test_list_item_info(self):
        """Test listing all item_info (catalogue)"""
        response = self.client.get('/api/catalogue/')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_item_info(self):
        """Test retrieving a specific item_info"""
        print(f"Item ID: {self.item_info.id}")  # Debug
        print(f"Item exists: {ItemInfo.objects.filter(id=self.item_info.id).exists()}")  # Debug
        response = self.client.get(f'/api/catalogue/{self.item_info.id}/')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_name'], self.item_info.item_name)

    def test_create_item_info(self):
        """Test creating a new item_info"""
        data = {
            "item_name": "New Item",
            "item_code": "NI001",
            "category": "Furniture",
            "resource_type": "Asset",
            "perishability": "Non-Perishable"
        }
        response = self.client.post('/api/catalogue/', data, format='json')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ItemInfo.objects.count(), 2)

    def test_update_item_info(self):
        """Test updating an item_info"""
        data = {"item_name": "Updated Item"}
        response = self.client.patch(f'/api/catalogue/{self.item_info.id}/', data, format='json')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item_info.refresh_from_db()
        self.assertEqual(self.item_info.item_name, "Updated Item")

    def test_delete_item_info(self):
        """Test deleting an item_info"""
        response = self.client.delete(f'/api/catalogue/{self.item_info.id}/')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ItemInfo.objects.count(), 0)

    def test_filter_by_category(self):
        """Test filtering item_info by category"""
        ItemInfo.objects.create(
            item_name="Furniture Item",
            item_code="FI001",
            category="Furniture",
            resource_type="Asset",
            perishability="Non-Perishable"
        )
        response = self.client.get('/api/catalogue/?category=Furniture')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_resource_type(self):
        """Test filtering item_info by resource type"""
        response = self.client.get('/api/catalogue/?resource_type=Hardware')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_filter_by_perishability(self):
        """Test filtering item_info by perishability"""
        ItemInfo.objects.create(
            item_name="Perishable Item",
            item_code="PI001",
            category="Food",
            resource_type="Consumable",
            perishability="Perishable"
        )
        response = self.client.get('/api/catalogue/?perishability=Perishable')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_item_info(self):
        """Test searching item_info"""
        ItemInfo.objects.create(
            item_name="Computer Hardware",
            item_code="CH001",
            category="Electronics",
            resource_type="Hardware",
            perishability="Non-Perishable"
        )
        response = self.client.get('/api/catalogue/?search=Computer')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_active_status(self):
        """Test filtering item_info by active status"""
        ItemInfo.objects.create(
            item_name="Inactive Item",
            item_code="II001",
            category="Other",
            resource_type="Other",
            perishability="Non-Perishable",
            active=False
        )
        response = self.client.get('/api/catalogue/?active=false')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_ordering_by_name(self):
        """Test ordering item_info by name"""
        ItemInfo.objects.create(
            item_name="Alpha Item",
            item_code="AI001",
            category="Other",
            resource_type="Other",
            perishability="Non-Perishable"
        )
        ItemInfo.objects.create(
            item_name="Beta Item",
            item_code="BI001",
            category="Other",
            resource_type="Other",
            perishability="Non-Perishable"
        )
        response = self.client.get('/api/catalogue/?ordering=item_name')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['item_name'], "Alpha Item")

    def test_create_item_info_with_all_fields(self):
        """Test creating item_info with all fields"""
        data = {
            "item_name": "Complete Item",
            "item_code": "CI001",
            "category": "Office",
            "resource_type": "Equipment",
            "perishability": "Non-Perishable",
            "tags": "office, equipment, furniture",
            "activity_name": "Office Setup",
            "active": True
        }
        response = self.client.post('/api/catalogue/', data, format='json')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tags'], "office, equipment, furniture")

    def test_filter_attributes_by_datatype(self):
        """Test filtering attributes by datatype"""
        ItemAttribute.objects.create(
            item_info=self.item_info,
            key="quantity",
            datatype="number"
        )
        response = self.client.get('/api/catalogue/attributes/?datatype=number')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_attributes_by_item(self):
        """Test filtering attributes by item_info"""
        another_item = ItemInfo.objects.create(
            item_name="Another Item",
            item_code="AI001",
            category="Furniture"
        )
        ItemAttribute.objects.create(
            item_info=another_item,
            key="color",
            datatype="string"
        )
        response = self.client.get(f'/api/catalogue/attributes/?item_id={another_item.id}')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_attributes(self):
        """Test searching attributes"""
        response = self.client.get('/api/catalogue/attributes/?search=ram')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_item_attribute_duplicate_key(self):
        """Test cannot create duplicate attribute key for same item_info"""
        data = {
            "item_info": self.item_info.id,
            "key": "ram",  # Same key as existing
            "datatype": "string"
        }
        response = self.client.post('/api/catalogue/attributes/', data, format='json')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_info_duplicate_code(self):
        """Test cannot create item_info with duplicate item_code"""
        data = {
            "item_name": "Duplicate Item",
            "item_code": "TI001",  # Same code as existing
            "category": "Other"
        }
        response = self.client.post('/api/catalogue/', data, format='json')
        print(response.content)  # Debug
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access catalogue"""
        self.client.logout()  # Ensure unauthenticated
        response = self.client.get('/api/catalogue/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get('/api/catalogue/attributes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)