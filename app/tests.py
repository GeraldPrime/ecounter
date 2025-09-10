from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from .models import PollingUnit, VoteAllocation, AllocatedResult
import tempfile
import pandas as pd

class VoteAllocationTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.polling_unit = PollingUnit.objects.create(
            sno=1,
            state="ANAMBRA",
            lga="AGUATA",
            ra="ACHINA I",
            delim="TEST POLLING UNIT",
            register_voter_2023="04-01-01-001",
            registered_voter_2024=500,
            pvc_collected=450,
            balance_uncollected=50,
            pvc_45_percent=225.0
        )
        
        self.allocation = VoteAllocation.objects.create(
            name="Test Allocation",
            description="Test allocation for unit testing",
            apc_percentage=60.0,
            lp_percentage=30.0,
            pdp_percentage=10.0
        )
    
    def test_polling_unit_creation(self):
        """Test polling unit model"""
        self.assertEqual(self.polling_unit.state, "ANAMBRA")
        self.assertEqual(self.polling_unit.pvc_45_percent, 225.0)
    
    def test_allocation_validation(self):
        """Test allocation percentage validation"""
        self.assertTrue(self.allocation.is_valid_allocation())
        self.assertEqual(self.allocation.total_percentage(), 100.0)
    
    def test_dashboard_view(self):
        """Test dashboard view"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vote Allocation Dashboard")
    
    def test_create_allocation_view(self):
        """Test create allocation view"""
        response = self.client.get(reverse('create_allocation'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'name': 'New Test Allocation',
            'description': 'Test description',
            'apc_percentage': 50.0,
            'lp_percentage': 40.0,
            'pdp_percentage': 10.0
        }
        response = self.client.post(reverse('create_allocation'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
