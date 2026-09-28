import re
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TrialItem(models.Model):
    # ===============================
    # Basic Information
    # ===============================
    client_name = models.CharField(
        max_length=255,
        verbose_name=_("客户名称")
    )
    project_manager = models.CharField(
        max_length=100,
        verbose_name=_("项目负责人")
    )
    project_site = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("项目现场")
    )

    # ===============================
    # Trial Time Related
    # ===============================
    # REQUIRED: trial_start_date and trial_period_days are mandatory
    trial_start_date = models.DateField(
        verbose_name=_("试用时间（开始）")
    )
    trial_period_days = models.CharField(
        max_length=10,
        default='30',
        verbose_name=_("试用周期（天）")
    )
    expiration_date = models.DateField(
        verbose_name=_("到期时间"),
        blank=True,
        null=True
    )

    # Trial Days（Excel 中的 G 列）
    # Can be negative (days remaining before expiration) or positive (days past expiration)
    trial_days = models.IntegerField(
        default=0,
        verbose_name=_("已试用时间")
    )

    # ===============================
    # OVER DUE（Excel 公式）
    # =IF(G3>30,"超期",IF(G3>0,"到期","未到期"))
    # ===============================
    OVER_DUE_CHOICES = [
        ('not_due', _('未到期')),
        ('due', _('到期')),
        ('over_due', _('超期')),
    ]

    over_due_status = models.CharField(
        max_length=20,
        choices=OVER_DUE_CHOICES,
        default='not_due',
        verbose_name=_("是否超期")
    )

    # ===============================
    # Status Fields
    # ===============================
    closed = models.BooleanField(
        default=False,
        verbose_name=_("是否完结")
    )
    resell = models.BooleanField(
        default=False,
        verbose_name=_("是否转销售")
    )

    # ===============================
    # Financial & Return Time
    # ===============================
    sales_amount = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name=_("销售金额")
    )

    # Excel F 列：Return Date
    return_date = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("还回时间")
    )

    # Excel Days After Return Logic
    # =IF(ISBLANK(F3),"NA",TODAY()-F3)
    days_after_return = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("归还后天数")
    )

    # ===============================
    # Product Information
    # OPTIONAL: All fields can be left empty
    # ===============================
    product_model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("产品名称")
    )
    quantity = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("数量")
    )
    sn = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("SN")
    )
    pn = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("PN")
    )

    # ===============================
    # Shipping & Document Information
    # OPTIONAL: All fields can be left empty
    # ===============================
    shipping_info = models.TextField(
        blank=True,
        verbose_name=_("收货信息")
    )
    contract_no = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("合同号")
    )
    logistics_info = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("物流信息")
    )
    outbound_shipment_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("出库单号")
    )
    warehouse = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("拿货仓库")
    )

    notes = models.TextField(
        blank=True,
        verbose_name=_("备注")
    )

    class Meta:
        verbose_name = _("试用项目")
        verbose_name_plural = _("试用项目表")

    def __str__(self):
        return f"{self.client_name} - {self.product_model}"

    # ===============================
    # Data Processing Helpers
    # ===============================
    def get_trial_period_days_int(self):
        """
        Extract numeric value from trial_period_days input.
        Handles formats like "7天", "30天", "15", "7 天", etc.
        Returns the extracted integer or default 30 on invalid input.
        """
        if not self.trial_period_days:
            return 30
        
        # Extract digits using regex
        match = re.search(r'\d+', str(self.trial_period_days))
        if match:
            try:
                return int(match.group())
            except ValueError:
                return 30
        
        # No digits found, return default
        return 30

    def clean(self):
        """
        Validate trial_period_days contains at least one digit.
        """
        if self.trial_period_days and not re.search(r'\d+', str(self.trial_period_days)):
            raise ValidationError({
                'trial_period_days': _('试用周期必须包含数字（如：7天、30、15天）')
            })

    # ===============================
    # Excel OVER DUE Logic
    # =IF(G3>30,"超期",IF(G3>0,"到期","未到期"))
    # ===============================
    def update_over_due_status(self):
        if self.trial_days > 30:
            self.over_due_status = 'over_due'
        elif self.trial_days > 0:
            self.over_due_status = 'due'
        else:
            # trial_days <= 0 means before expiration (not due yet)
            self.over_due_status = 'not_due'

    # ===============================
    # Excel Days After Return Logic
    # =IF(ISBLANK(expiration_date),"NA",TODAY()-F3)
    # ===============================
    def update_days_after_return(self):
        today = timezone.localdate()

        if self.expiration_date:
            delta = (today - self.expiration_date).days
            self.days_after_return = delta if delta >= 0 else 0
        else:
            self.days_after_return = None

    # ===============================
    # Core Save Logic
    # ===============================
    def recalculate(self, skip_auto_calc=False):
        today = timezone.localdate()

        # 1️⃣ Expiry Date = Trial Start Date + Trial Period Days
        if self.trial_start_date and self.trial_period_days:
            period_days = self.get_trial_period_days_int()
            self.expiration_date = (
                self.trial_start_date
                + timedelta(days=period_days)
            )

        # 2️⃣ Trial Days Used Time
        # Negative value means days remaining before expiration
        # Positive value means days past expiration
        if not skip_auto_calc and self.expiration_date:
            days = (today - self.expiration_date).days
            self.trial_days = days

        # 3️⃣ Excel OVER DUE Logic
        self.update_over_due_status()

        # 4️⃣ Excel Days After Return Logic
        self.update_days_after_return()

        # 5️⃣ Resell → Auto Close Trial
        if self.resell:
            self.closed = True

    def save(self, *args, skip_auto_calc=False, **kwargs):
        self.recalculate(skip_auto_calc=skip_auto_calc)
        super().save(*args, **kwargs)

    # Date-dependent fields (like Excel's TODAY()) go stale once a day passes
    # without the row being saved, so they are refreshed in bulk.
    TIME_BASED_FIELDS = ['expiration_date', 'trial_days', 'over_due_status', 'days_after_return', 'closed']

    @classmethod
    def refresh_time_based_fields(cls):
        stale = []
        for item in cls.objects.all():
            before = [getattr(item, f) for f in cls.TIME_BASED_FIELDS]
            item.recalculate()
            if [getattr(item, f) for f in cls.TIME_BASED_FIELDS] != before:
                stale.append(item)
        if stale:
            cls.objects.bulk_update(stale, cls.TIME_BASED_FIELDS, batch_size=500)
        return len(stale)

    @classmethod
    def refresh_time_based_fields_daily(cls):
        """Run refresh_time_based_fields() at most once per day per process."""
        from django.core.cache import cache
        if cache.add(f'trialitem-refreshed-{timezone.localdate()}', True, 60 * 60 * 24):
            cls.refresh_time_based_fields()

    # ===============================
    # For Admin / Templates / API Display
    # ===============================
    @property
    def over_due_display(self):
        """Excel OVER DUE Status Text"""
        return dict(self.OVER_DUE_CHOICES).get(self.over_due_status, "")

    @property
    def days_after_return_display(self):
        """Excel Days After Return Text or Number"""
        return (
            "NA"
            if self.days_after_return is None
            else str(self.days_after_return)
        )