from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import TrialItem


@admin.register(TrialItem)
class TrialItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for TrialItem model.
    
    This admin class provides comprehensive management capabilities for trial items,
    with organized sections, intuitive list display, powerful search and filtering,
    and proper handling of auto-calculated fields.
    """

    # ===============================
    # List View Configuration
    # ===============================
    
    # Display fields in the list view
    list_display = (
        'client_name',
        'project_manager',
        'product_model',
        'sn',
        'trial_start_date',
        'expiration_date',
        'over_due_display',
        'trial_days',
        'closed',
        'resell',
    )

    # Fields that can be edited directly in the list view
    list_editable = (
        'closed',
        'resell',
    )

    # Search functionality
    search_fields = (
        'client_name',
        'project_manager',
        'project_site',
        'product_model',
        'sn',
        'pn',
        'contract_no',
        'logistics_info',
        'warehouse',
    )

    # Filter options in the sidebar
    list_filter = (
        'over_due_status',
        'closed',
        'resell',
        'warehouse',
    )

    # Date-based navigation
    date_hierarchy = 'trial_start_date'

    # Default ordering
    ordering = ('-trial_start_date',)

    # Number of records per page
    list_per_page = 50

    # ===============================
    # Form Configuration
    # ===============================

    # Fields that are read-only (auto-calculated in save())
    readonly_fields = (
        'expiration_date',
        'trial_days',
        'over_due_status',
        'days_after_return',
    )

    # Fieldsets for organized edit form
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'client_name',
                'project_manager',
                'project_site',
            )
        }),
        (_('试用周期'), {
            'description': _('试用开始日期和周期将自动计算到期日期'),
            'fields': (
                'trial_start_date',
                'trial_period_days',
                ('expiration_date', 'trial_days'),
            )
        }),
        (_('Status Information'), {
            'fields': (
                'over_due_status',
                'closed',
                'resell',
            )
        }),
        (_('Financial & Return'), {     
            'fields': (
                'sales_amount',
                'return_date',
                'days_after_return',
            )
        }),
        (_('Product Information'), {
            'fields': (
                'product_model',
                'quantity',
                'sn',
                'pn',
            )
        }),
        (_('发货与文档'), {
            'fields': (
                'shipping_info',
                'contract_no',
                'logistics_info',
                'outbound_shipment_number',
                'warehouse',
            )
        }),
        (_('备注'), {
            'fields': (
                'notes',
            ),
            'classes': ('collapse',),
        }),
    )

    # ===============================
    # Custom Actions
    # ===============================

    actions = ['mark_as_closed', 'mark_as_resell']

    @admin.action(description=_('批量标记为完结'))
    def mark_as_closed(self, request, queryset):
        """
        Bulk mark selected trial items as closed.
        """
        queryset.update(closed=True)
        self.message_user(
            request,
            _('成功将 %(count)s 条记录标记为完结') % {
                'count': queryset.count()
            }
        )

    @admin.action(description=_('批量标记为转销售'))
    def mark_as_resell(self, request, queryset):
        """
        Bulk mark selected trial items as resell (will auto-close).
        """
        queryset.update(resell=True, closed=True)
        self.message_user(
            request,
            _('成功将 %(count)s 条记录标记为转销售') % {
                'count': queryset.count()
            }
        )

    # ===============================
    # Custom Display Methods
    # ===============================

    @admin.display(description=_('超期状态'), ordering='over_due_status')
    def over_due_display(self, obj):
        """
        Display the over due status with color coding.
        """
        status_map = {
            'not_due': (_('未到期'), 'bg-green-100 text-green-800'),
            'due': (_('到期'), 'bg-yellow-100 text-yellow-800'),
            'over_due': (_('超期'), 'bg-red-100 text-red-800'),
        }
        label, css_class = status_map.get(obj.over_due_status, (_('未知'), 'bg-gray-100 text-gray-800'))
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            css_class,
            label
        )