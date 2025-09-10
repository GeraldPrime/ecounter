# management/commands/import_excel.py
from django.core.management.base import BaseCommand
from django.conf import settings
import pandas as pd
import os
from models import PollingUnit

class Command(BaseCommand):
    help = 'Import polling units from Excel file'
    
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file')
    
    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        try:
            df = pd.read_excel(file_path)
            
            # Clear existing data
            PollingUnit.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing polling units'))
            
            # Import data
            for _, row in df.iterrows():
                PollingUnit.objects.create(
                    sno=row.get('S/NO', 0),
                    state=str(row.get('STATE', '')),
                    lga=str(row.get('LGA', '')),
                    ra=str(row.get('RA', '')),
                    delim=str(row.get('DELIM', '')),
                    register_voter_2023=str(row.get('REGISTER VOTER AS AT 2023', '')),
                    registered_voter_2024=int(row.get('REGISTERED VOTER AS AT 2024', 0)),
                    pvc_collected=int(row.get('NO OF PVC COLLECTED ', 0)),
                    balance_uncollected=int(row.get('BALANCE OF UNCOLECTED PVCs', 0)),
                    pvc_45_percent=float(row.get('45% PVC COLLECTION', 0)),
                    aa_original=float(row.get('AA', 0)),
                    ad_original=float(row.get('AD', 0)),
                    adc_original=float(row.get('ADC', 0)),
                    apc_original=float(row.get('APC', 0)),
                    lp_original=float(row.get('LP', 0)),
                    pdp_original=float(row.get('PDP', 0)),
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {len(df)} polling units')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))