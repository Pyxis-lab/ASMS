from django.contrib import admin
from .models import AfterSalesRecord


@admin.register(AfterSalesRecord)
class AfterSalesRecordAdmin(admin.ModelAdmin):
    """
    Admin configuration for AfterSalesRecord model.
    Optimized for efficient management of bulk imported records.
    """

    # Display fields in the list view
    list_display = (
        'after_sales_no',
        'user_name',
        'product_name_model',
        'after_sales_type',
        'resolved',
        'out_of_warranty',
        'return_date',
        'created_at',
    )

    # Fields that can be searched
    search_fields = (
        'after_sales_no',
        'user_name',
        'product_name_model',
        'sn',
        'pn',
        'project_site',
        'tracking_no',
    )

    # Filter options in the sidebar
    list_filter = (
        'resolved',
        'out_of_warranty',
        'after_sales_type',
        'customer_return_required',
    )

    # Fields that are read-only in the edit form
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Default ordering
    ordering = ('-return_date',)

    # Number of records per page
    list_per_page = 50

    # Fieldsets for better organization in the edit form
    fieldsets = (
        ('基本信息', {
            'fields': (
                'after_sales_no',
                'no',
                'user_name',
                'after_sales_type',
                'project_site',
            )
        }),
        ('产品信息', {
            'fields': (
                'product_name_model',
                'sn',
                'pn',
                'equipment_no',
            )
        }),
        ('售后状态', {
            'fields': (
                'resolved',
                'out_of_warranty',
                'customer_return_required',
            )
        }),
        ('时间信息', {
            'fields': (
                'return_date',
                'original_ship_date',
                'ship_date',
            )
        }),
        ('退货与RCA', {
            'fields': (
                'return_reason_description',
                'rca',
            )
        }),
        ('寄货信息', {
            'fields': (
                'shipped_item_name',
                'r_sn',
                'r_pn',
                'shipping_info',
                'tracking_no',
                'source_warehouse',
                'outbound_order_no',
            )
        }),
        ('费用信息', {
            'fields': (
                'after_sales_cost',
                'charge_details',
            )
        }),
        ('审计信息', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )