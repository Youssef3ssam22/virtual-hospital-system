"""Django admin configuration for Lab module."""
from django.contrib import admin
from apps.lab.infrastructure.orm_models import (
    LabOrder, Specimen, LabResult, CriticalValue, LabReport, AnalyzerQueue
)


@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    """Admin interface for LabOrder."""
    list_display = ('id', 'patient', 'encounter', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('id', 'patient__mrn', 'patient__full_name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'created_at'
    list_select_related = ('patient', 'encounter')


@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    """Admin interface for Specimen."""
    list_display = ('accession_number', 'order', 'patient', 'specimen_type', 'status', 'collection_time')
    list_filter = ('status', 'specimen_type', 'collection_time')
    search_fields = ('accession_number', 'order__id', 'patient__mrn', 'patient__full_name')
    ordering = ('-collection_time',)
    readonly_fields = ('id', 'received_time', 'created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'collection_time'
    list_select_related = ('order', 'patient', 'encounter')


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    """Admin interface for LabResult."""
    list_display = ('test_name', 'result_value', 'abnormal_flag', 'status', 'reported_at')
    list_filter = ('status', 'abnormal_flag', 'reported_at')
    search_fields = ('test_code', 'test_name')
    ordering = ('-reported_at',)
    readonly_fields = ('id', 'reported_at')
    list_per_page = 25
    list_select_related = ('order', 'specimen')
    date_hierarchy = 'reported_at'


@admin.register(CriticalValue)
class CriticalValueAdmin(admin.ModelAdmin):
    """Admin interface for CriticalValue."""
    list_display = ('test_name', 'critical_value', 'priority', 'status', 'patient_id')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('patient_id', 'test_name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'created_at'


@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    """Admin interface for LabReport."""
    list_display = ('report_number', 'patient', 'status', 'generated_at', 'critical_values_count')
    list_filter = ('status', 'generated_at')
    search_fields = ('report_number', 'order__id', 'patient__mrn', 'patient__full_name')
    ordering = ('-generated_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'generated_at'
    list_select_related = ('order', 'patient', 'encounter')


@admin.register(AnalyzerQueue)
class AnalyzerQueueAdmin(admin.ModelAdmin):
    """Admin interface for AnalyzerQueue."""
    list_display = ('analyzer_id', 'priority', 'status', 'position_in_queue', 'queued_at')
    list_filter = ('status', 'priority', 'analyzer_id')
    ordering = ('priority', 'position_in_queue')
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 25
    list_select_related = ('specimen',)
