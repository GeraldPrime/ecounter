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
    nrm_original = models.FloatField(default=0)
    nnpp_original = models.FloatField(default=0)
    prp_original = models.FloatField(default=0)
    sdp_original = models.FloatField(default=0)
    ypp_original = models.FloatField(default=0)
    yp_original = models.FloatField(default=0)
    zlp_original = models.FloatField(default=0)
    a_original = models.FloatField(default=0)
    aac_original = models.FloatField(default=0)
    adp_original = models.FloatField(default=0)
    apm_original = models.FloatField(default=0)
    apga_original = models.FloatField(default=0)
    app_original = models.FloatField(default=0)
    bp_original = models.FloatField(default=0)

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
    nrm_percentage = models.FloatField(default=0, help_text="Percentage for NRM party")
    nnpp_percentage = models.FloatField(default=0, help_text="Percentage for NNPP party")
    prp_percentage = models.FloatField(default=0, help_text="Percentage for PRP party")
    sdp_percentage = models.FloatField(default=0, help_text="Percentage for SDP party")
    ypp_percentage = models.FloatField(default=0, help_text="Percentage for YPP party")
    yp_percentage = models.FloatField(default=0, help_text="Percentage for YP party")
    zlp_percentage = models.FloatField(default=0, help_text="Percentage for ZLP party")
    a_percentage = models.FloatField(default=0, help_text="Percentage for Accord party")
    aac_percentage = models.FloatField(default=0, help_text="Percentage for AAC party")
    adp_percentage = models.FloatField(default=0, help_text="Percentage for ADP party")
    apm_percentage = models.FloatField(default=0, help_text="Percentage for APM party")
    apga_percentage = models.FloatField(default=0, help_text="Percentage for APGA party")
    app_percentage = models.FloatField(default=0, help_text="Percentage for APP party")
    bp_percentage = models.FloatField(default=0, help_text="Percentage for BP party")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def total_percentage(self):
        return (self.aa_percentage + self.ad_percentage + self.adc_percentage + 
                self.apc_percentage + self.lp_percentage + self.pdp_percentage +
                self.nrm_percentage + self.nnpp_percentage + self.prp_percentage +
                self.sdp_percentage + self.ypp_percentage + self.yp_percentage +
                self.zlp_percentage + self.a_percentage + self.aac_percentage +
                self.adp_percentage + self.apm_percentage + self.apga_percentage + 
                self.app_percentage + self.bp_percentage)
    
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
            'NRM': self.nrm_percentage,
            'NNPP': self.nnpp_percentage,
            'PRP': self.prp_percentage,
            'SDP': self.sdp_percentage,
            'YPP': self.ypp_percentage,
            'YP': self.yp_percentage,
            'ZLP': self.zlp_percentage,
            'A': self.a_percentage,
            'AAC': self.aac_percentage,
            'ADP': self.adp_percentage,
            'APM': self.apm_percentage,
            'APGA': self.apga_percentage,
            'APP': self.app_percentage,
            'BP': self.bp_percentage,
        }

class AllocatedResult(models.Model):
    """Stores the calculated results for each polling unit based on allocation"""
    polling_unit = models.ForeignKey(PollingUnit, on_delete=models.CASCADE)
    vote_allocation = models.ForeignKey(VoteAllocation, on_delete=models.CASCADE)
    
    # Calculated votes for each party
    aa_votes = models.FloatField(default=0)
    ad_votes = models.FloatField(default=0)
    adc_votes = models.FloatField(default=0)
    apc_votes = models.FloatField(default=0)
    lp_votes = models.FloatField(default=0)
    pdp_votes = models.FloatField(default=0)
    nrm_votes = models.FloatField(default=0)
    nnpp_votes = models.FloatField(default=0)
    prp_votes = models.FloatField(default=0)
    sdp_votes = models.FloatField(default=0)
    ypp_votes = models.FloatField(default=0)
    yp_votes = models.FloatField(default=0)
    zlp_votes = models.FloatField(default=0)
    a_votes = models.FloatField(default=0)
    aac_votes = models.FloatField(default=0)
    adp_votes = models.FloatField(default=0)
    apm_votes = models.FloatField(default=0)
    apga_votes = models.FloatField(default=0)
    app_votes = models.FloatField(default=0)
    bp_votes = models.FloatField(default=0)
    total_votes = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['polling_unit', 'vote_allocation']

    def __str__(self):
        return f"{self.polling_unit.delim} - {self.vote_allocation.name}"