from django.contrib import admin
from .models import Location, Supplies, DisasterReport, SupplyRequest

class SuppliesInline(admin.StackedInline):
    model = Supplies
    can_delete = False
    extra = 0

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name',)
    inlines = [SuppliesInline]

@admin.register(Supplies)
class SuppliesAdmin(admin.ModelAdmin):
    list_display = ('location', 'food_packs', 'water_supply', 'medical_supply', 'last_updated')
    list_filter = ('location',)
    search_fields = ('location__name',)

@admin.register(DisasterReport)
class DisasterReportAdmin(admin.ModelAdmin):
    list_display = ('location', 'severity', 'reported_by', 'reported_date', 'is_active')
    list_filter = ('severity', 'is_active', 'reported_date')
    search_fields = ('location__name', 'description')
    actions = ['mark_as_resolved', 'mark_as_active']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_active=False)
    mark_as_resolved.short_description = "Mark selected reports as resolved"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_as_active.short_description = "Mark selected reports as active"

@admin.register(SupplyRequest)
class SupplyRequestAdmin(admin.ModelAdmin):
    list_display = ('location', 'requested_by', 'food_packs', 'water_supply', 'medical_supply', 'request_date', 'status')
    list_filter = ('location', 'status', 'request_date')
    search_fields = ('location__name', 'notes')
    actions = ['approve_requests', 'mark_as_delivered', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        queryset.update(status='approved')
    approve_requests.short_description = "Approve selected requests"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected requests as delivered"
    
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
    reject_requests.short_description = "Reject selected requests"
