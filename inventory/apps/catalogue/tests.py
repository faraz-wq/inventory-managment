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
    def setUp(self):
        self.client = APIClient()

        # Location & Department
        self.district = District.objects.create(district_name="TD", district_code_ap="TD01")
        self.mandal = Mandal.objects.create(mandal_name="TM", mandal_code_ap="TM01", district=self.district)
        self.village = Village.objects.create(village_name="TV", village_code_ap="TV01", district=self.district, mandal=self.mandal)
        self.department = Department.objects.create(org_name="TD", org_shortname="TD", org_code="TD001", org_type="Government")

        # User
        self.user = User.objects.create_user(
            email="user@test.com", password="user123", name="Test User",
            phone_no="+91-9876543210", dept=self.department, location=self.village
        )

        # Permissions & Role
        perms = ["view_catalogue", "create_catalogue", "update_catalogue", "delete_catalogue"]
        permissions = {name: Permission.objects.create(name=name) for name in perms}
        self.role = Role.objects.create(name="Catalogue Manager")
        for perm in permissions.values():
            RolePermission.objects.create(role=self.role, permission=perm)
        UserRole.objects.create(user=self.user, role=self.role)

        # ItemInfo
        self.item_info = ItemInfo.objects.create(
            item_code="TI001", item_name="Test Item", category="Electronics",
            resource_type="Hardware", perishability="Non-Perishable", unit="Piece",
            tags="test,item", activity_name="Testing"
        )

        # ItemAttribute
        self.item_attribute = ItemAttribute.objects.create(
            item_info=self.item_info, key="ram", datatype="string"
        )

        self.client.force_authenticate(user=self.user)

    # -------------------------------------------------
    # ItemInfo CRUD
    # -------------------------------------------------
    def test_list_item_info(self):
        response = self.client.get('/api/catalogue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_item_info_with_attributes(self):
        response = self.client.get(f'/api/catalogue/{self.item_info.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_name'], "Test Item")
        self.assertIn('attributes', response.data)
        self.assertEqual(len(response.data['attributes']), 1)
        self.assertEqual(response.data['attributes'][0]['key'], "ram")

    def test_create_item_info(self):
        data = {
            "item_code": "NI001", "item_name": "New Item", "category": "Furniture",
            "resource_type": "Asset", "perishability": "Non-Perishable"
        }
        response = self.client.post('/api/catalogue/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ItemInfo.objects.count(), 2)

    def test_update_item_info(self):
        response = self.client.patch(
            f'/api/catalogue/{self.item_info.id}/',
            {"item_name": "Updated Item"}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item_info.refresh_from_db()
        self.assertEqual(self.item_info.item_name, "Updated Item")

    def test_delete_item_info(self):
        response = self.client.delete(f'/api/catalogue/{self.item_info.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ItemInfo.objects.filter(id=self.item_info.id).exists())

    # -------------------------------------------------
    # Filtering / Search / Validation
    # -------------------------------------------------
    def test_filter_by_category(self):
        ItemInfo.objects.create(item_code="F001", item_name="Chair", category="Furniture")
        response = self.client.get('/api/catalogue/?category=Furniture')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_item_info(self):
        response = self.client.get('/api/catalogue/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_duplicate_item_code_fails(self):
        data = {"item_code": "TI001", "item_name": "Duplicate"}
        response = self.client.post('/api/catalogue/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------
    # Attribute actions (GET/POST on /attributes/, PATCH/DELETE on /attributes/<id>/)
    # -------------------------------------------------
    def test_list_attributes_via_action(self):
        url = f'/api/catalogue/{self.item_info.id}/attributes/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)               # ← NOT paginated
        self.assertEqual(response.data[0]['key'], "ram")

    def test_create_item_attribute_via_action(self):
        payload = {"item_info": self.item_info.id, "key": "cpu", "datatype": "string"}
        url = f'/api/catalogue/{self.item_info.id}/attributes/'
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['key'], "cpu")

    def test_update_attribute_via_action(self):
        payload = {"key": "memory"}
        url = f'/api/catalogue/{self.item_info.id}/attributes/{self.item_attribute.id}/'
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item_attribute.refresh_from_db()
        self.assertEqual(self.item_attribute.key, "memory")

    def test_delete_attribute_via_action(self):
        url = f'/api/catalogue/{self.item_info.id}/attributes/{self.item_attribute.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ItemAttribute.objects.filter(id=self.item_attribute.id).exists())

    def test_duplicate_attribute_key_fails(self):
        data = {"item_info": self.item_info.id, "key": "ram", "datatype": "string"}
        response = self.client.post(
            f'/api/catalogue/{self.item_info.id}/attributes/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------
    # Permissions
    # -------------------------------------------------
    def test_unauthenticated_access_denied(self):
        self.client.logout()
        response = self.client.get('/api/catalogue/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)