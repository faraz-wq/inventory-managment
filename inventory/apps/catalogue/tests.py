"""
Unit tests for Catalogue API endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.departments.models import Department
from apps.locations.models import District, Mandal, Village
from apps.catalogue.models import ItemInfo

User = get_user_model()


class CatalogueAPITestCase(TestCase):
    """Test cases for Catalogue (ItemInfo) API endpoints"""

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

        # Create test user
        self.user = User.objects.create_user(
            email="user@test.com",
            password="user123",
            name="Test User",
            phone_no="+91-9876543210",
            dept=self.department,
            location=self.village
        )

        # Create test item info
        self.item_info = ItemInfo.objects.create(
            item_name="Test Item",
            item_code="TI001",
            category="Electronics",
            resource_type="Hardware",
            perishability="Non-Perishable"
        )

    def test_list_item_info(self):
        """Test listing all item info (catalogue)"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/catalogue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_item_info(self):
        """Test retrieving a specific item info"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/catalogue/{self.item_info.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_name'], self.item_info.item_name)

    def test_create_item_info(self):
        """Test creating a new item info"""
        self.client.force_authenticate(user=self.user)

        data = {
            "item_name": "New Item",
            "item_code": "NI001",
            "category": "Furniture",
            "resource_type": "Asset",
            "perishability": "Non-Perishable"
        }

        response = self.client.post('/api/catalogue/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ItemInfo.objects.count(), 2)

    def test_update_item_info(self):
        """Test updating an item info"""
        self.client.force_authenticate(user=self.user)

        data = {"item_name": "Updated Item"}
        response = self.client.patch(
            f'/api/catalogue/{self.item_info.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item_info.refresh_from_db()
        self.assertEqual(self.item_info.item_name, "Updated Item")

    def test_delete_item_info(self):
        """Test deleting an item info"""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f'/api/catalogue/{self.item_info.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ItemInfo.objects.count(), 0)

    def test_filter_by_category(self):
        """Test filtering item info by category"""
        self.client.force_authenticate(user=self.user)

        # Create item with different category
        ItemInfo.objects.create(
            item_name="Furniture Item",
            item_code="FI001",
            category="Furniture",
            resource_type="Asset",
            perishability="Non-Perishable"
        )

        response = self.client.get('/api/catalogue/?category=Furniture')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_resource_type(self):
        """Test filtering item info by resource type"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/catalogue/?resource_type=Hardware')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_filter_by_perishability(self):
        """Test filtering item info by perishability"""
        self.client.force_authenticate(user=self.user)

        # Create perishable item
        ItemInfo.objects.create(
            item_name="Perishable Item",
            item_code="PI001",
            category="Food",
            resource_type="Consumable",
            perishability="Perishable"
        )

        response = self.client.get('/api/catalogue/?perishability=Perishable')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_item_info(self):
        """Test searching item info"""
        self.client.force_authenticate(user=self.user)

        ItemInfo.objects.create(
            item_name="Computer Hardware",
            item_code="CH001",
            category="Electronics",
            resource_type="Hardware",
            perishability="Non-Perishable"
        )

        response = self.client.get('/api/catalogue/?search=Computer')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_active_status(self):
        """Test filtering item info by active status"""
        self.client.force_authenticate(user=self.user)

        # Create inactive item
        ItemInfo.objects.create(
            item_name="Inactive Item",
            item_code="II001",
            category="Other",
            resource_type="Other",
            perishability="Non-Perishable",
            active=False
        )

        response = self.client.get('/api/catalogue/?active=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_ordering_by_name(self):
        """Test ordering item info by name"""
        self.client.force_authenticate(user=self.user)

        # Create additional items
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['item_name'], "Alpha Item")

    def test_create_item_info_with_all_fields(self):
        """Test creating item info with all fields"""
        self.client.force_authenticate(user=self.user)

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

        response = self.client.post('/api/catalogue/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tags'], "office, equipment, furniture")

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access catalogue"""
        response = self.client.get('/api/catalogue/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
