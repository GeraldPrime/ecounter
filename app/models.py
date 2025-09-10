from django.db import models

# Create your models here.
# models.py
from django.db import models
import json



class PollingUnit(models.Model):
    sno = models.IntegerField()
    state = models.CharField(max_length=100)
    lga = models.CharField(max_length=100)
    ra = models.CharField(max_length=100)
    delim = models.CharField(max_length=200)
    register_voter_2023 = models.CharField(max_length=50)
    registered_voter_2024 = models.IntegerField()
    pvc_collected = models.IntegerField()
    balance_uncollected = models.IntegerField()
    pvc_45_percent = models.FloatField()
    
    # Original party columns (for reference only - not used in calculations)
    aa_original = models.FloatField(default=0)
    ad_original = models.FloatField(default=0)
    adc_original = models.FloatField(default=0)
    apc_original = models.FloatField(default=0)
    lp_original = models.FloatField(default=0)
    pdp_original = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sno']

    def __str__(self):
        return f"{self.state} - {self.lga} - {self.delim}"



class VoteAllocation(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Party allocation percentages (total should be 100)
    aa_percentage = models.FloatField(default=0, help_text="Percentage for AA party")
    ad_percentage = models.FloatField(default=0, help_text="Percentage for AD party")
    adc_percentage = models.FloatField(default=0, help_text="Percentage for ADC party")
    apc_percentage = models.FloatField(default=0, help_text="Percentage for APC party")
    lp_percentage = models.FloatField(default=0, help_text="Percentage for LP party")
    pdp_percentage = models.FloatField(default=0, help_text="Percentage for PDP party")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def total_percentage(self):
        return (self.aa_percentage + self.ad_percentage + self.adc_percentage + 
                self.apc_percentage + self.lp_percentage + self.pdp_percentage)
    
    def is_valid_allocation(self):
        return abs(self.total_percentage() - 100.0) < 0.01
    
    def get_party_allocations(self):
        return {
            'AA': self.aa_percentage,
            'AD': self.ad_percentage,
            'ADC': self.adc_percentage,
            'APC': self.apc_percentage,
            'LP': self.lp_percentage,
            'PDP': self.pdp_percentage,
        }

class AllocatedResult(models.Model):
    """Stores the calculated results for each polling unit based on allocation"""
    polling_unit = models.ForeignKey(PollingUnit, on_delete=models.CASCADE)
    vote_allocation = models.ForeignKey(VoteAllocation, on_delete=models.CASCADE)
    
    # Calculated votes for each party
    aa_votes = models.FloatField()
    ad_votes = models.FloatField()
    adc_votes = models.FloatField()
    apc_votes = models.FloatField()
    lp_votes = models.FloatField()
    pdp_votes = models.FloatField()
    total_votes = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['polling_unit', 'vote_allocation']

    def __str__(self):
        return f"{self.polling_unit.delim} - {self.vote_allocation.name}"