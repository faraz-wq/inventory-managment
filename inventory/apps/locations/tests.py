"""
Unit tests for Locations API endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.departments.models import Department
from apps.locations.models import District, Mandal, Village

User = get_user_model()


class LocationAPITestCase(TestCase):
    """Test cases for Location (District, Mandal, Village) API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create test locations
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

    # District Tests
    def test_list_districts(self):
        """Test listing all districts"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/locations/districts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_district(self):
        """Test retrieving a specific district"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/locations/districts/{self.district.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['district_name'], self.district.district_name)

    def test_create_district(self):
        """Test creating a new district"""
        self.client.force_authenticate(user=self.user)

        data = {
            "district_name": "New District",
            "district_code_ap": "ND01"
        }

        response = self.client.post('/api/locations/districts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(District.objects.count(), 2)

    def test_update_district(self):
        """Test updating a district"""
        self.client.force_authenticate(user=self.user)

        data = {"district_name": "Updated District"}
        response = self.client.patch(
            f'/api/locations/districts/{self.district.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.district.refresh_from_db()
        self.assertEqual(self.district.district_name, "Updated District")

    def test_delete_district(self):
        """Test deleting a district"""
        self.client.force_authenticate(user=self.user)

        # Create a new district to delete (can't delete one with references)
        new_district = District.objects.create(
            district_name="Delete District",
            district_code_ap="DD01"
        )

        response = self.client.delete(f'/api/locations/districts/{new_district.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_districts(self):
        """Test searching districts"""
        self.client.force_authenticate(user=self.user)

        District.objects.create(
            district_name="Search District",
            district_code_ap="SD01"
        )

        response = self.client.get('/api/locations/districts/?search=Search')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # Mandal Tests
    def test_list_mandals(self):
        """Test listing all mandals"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/locations/mandals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_mandal(self):
        """Test retrieving a specific mandal"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/locations/mandals/{self.mandal.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mandal_name'], self.mandal.mandal_name)

    def test_create_mandal(self):
        """Test creating a new mandal"""
        self.client.force_authenticate(user=self.user)

        data = {
            "mandal_name": "New Mandal",
            "mandal_code_ap": "NM01",
            "district": self.district.id
        }

        response = self.client.post('/api/locations/mandals/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Mandal.objects.count(), 2)

    def test_update_mandal(self):
        """Test updating a mandal"""
        self.client.force_authenticate(user=self.user)

        data = {"mandal_name": "Updated Mandal"}
        response = self.client.patch(
            f'/api/locations/mandals/{self.mandal.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mandal.refresh_from_db()
        self.assertEqual(self.mandal.mandal_name, "Updated Mandal")

    def test_filter_mandals_by_district(self):
        """Test filtering mandals by district"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/locations/mandals/?district={self.district.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    # Village Tests
    def test_list_villages(self):
        """Test listing all villages"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/locations/villages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_village(self):
        """Test retrieving a specific village"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/locations/villages/{self.village.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['village_name'], self.village.village_name)

    def test_create_village(self):
        """Test creating a new village"""
        self.client.force_authenticate(user=self.user)

        data = {
            "village_name": "New Village",
            "village_code_ap": "NV01",
            "district": self.district.id,
            "mandal": self.mandal.id
        }

        response = self.client.post('/api/locations/villages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Village.objects.count(), 2)

    def test_update_village(self):
        """Test updating a village"""
        self.client.force_authenticate(user=self.user)

        data = {"village_name": "Updated Village"}
        response = self.client.patch(
            f'/api/locations/villages/{self.village.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.village.refresh_from_db()
        self.assertEqual(self.village.village_name, "Updated Village")

    def test_filter_villages_by_district(self):
        """Test filtering villages by district"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/locations/villages/?district={self.district.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_filter_villages_by_mandal(self):
        """Test filtering villages by mandal"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/locations/villages/?mandal={self.mandal.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_search_villages(self):
        """Test searching villages"""
        self.client.force_authenticate(user=self.user)

        Village.objects.create(
            village_name="Search Village",
            village_code_ap="SV01",
            district=self.district,
            mandal=self.mandal
        )

        response = self.client.get('/api/locations/villages/?search=Search')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access locations"""
        response = self.client.get('/api/locations/districts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
