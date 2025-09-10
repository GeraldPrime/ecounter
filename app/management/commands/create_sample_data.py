from django.core.management.base import BaseCommand
from models import PollingUnit, VoteAllocation
import random

class Command(BaseCommand):
    help = 'Create sample polling units and allocations for testing'
    
    def handle(self, *args, **options):
        # Create sample polling units
        states = ['ANAMBRA', 'LAGOS', 'KANO', 'RIVERS']
        lgas = ['AGUATA', 'IKEJA', 'NASSARAWA', 'PORT HARCOURT']
        
        for i in range(1, 51):  # Create 50 sample units
            PollingUnit.objects.create(
                sno=i,
                state=random.choice(states),
                lga=random.choice(lgas),
                ra=f"RA_{i}",
                delim=f"Polling Unit {i}",
                register_voter_2023=f"04-01-01-{i:03d}",
                registered_voter_2024=random.randint(200, 1000),
                pvc_collected=random.randint(150, 900),
                balance_uncollected=random.randint(10, 100),
                pvc_45_percent=random.uniform(90, 450)
            )
        
        # Create sample allocations
        sample_allocations = [
            {
                'name': 'APC Majority',
                'apc_percentage': 60.0,
                'lp_percentage': 25.0,
                'pdp_percentage': 15.0
            },
            {
                'name': 'Even Distribution',
                'apc_percentage': 33.33,
                'lp_percentage': 33.33,
                'pdp_percentage': 33.34
            },
            {
                'name': 'LP Focus',
                'apc_percentage': 20.0,
                'lp_percentage': 50.0,
                'pdp_percentage': 30.0
            }
        ]
        
        for allocation_data in sample_allocations:
            VoteAllocation.objects.create(**allocation_data)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data')
        )