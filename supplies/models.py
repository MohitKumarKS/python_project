from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from djongo import models as djongo_models
from bson.objectid import ObjectId

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'locations'

class Supplies(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    food_packs = models.IntegerField(default=0)
    water_supply = models.IntegerField(default=0)
    medical_supply = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Supplies at {self.location.name}"
    
    def is_low_on_supplies(self):
        """Check if any supplies are running low (less than 10)"""
        return self.food_packs < 10 or self.water_supply < 10 or self.medical_supply < 10
    
    class Meta:
        db_table = 'supplies'

class DisasterReport(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Report at {self.location.name} - {self.get_severity_display()}"
    
    class Meta:
        db_table = 'disaster_reports'

class SupplyRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
    ]
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    food_packs = models.IntegerField(default=0)
    water_supply = models.IntegerField(default=0)
    medical_supply = models.IntegerField(default=0)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Supply Request for {self.location.name} - {self.status}"
    
    class Meta:
        db_table = 'supply_requests'
