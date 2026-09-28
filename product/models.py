from django.db import models
from django.utils.translation import gettext_lazy as _

class AfterSalesRecord(models.Model):
    """
    After‑Sales Record Model
    Optimized for bulk Excel import (10k+ rows)
    """

    # -------- Basic Info --------
    user_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("用户名称")
    )
    after_sales_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("售后类型")
    )
    no = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("NO.")
    )
    after_sales_no = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name=_("售后编号")
    )
    project_site = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("项目现场")
    )

    resolved = models.BooleanField(
        default=False,
        verbose_name=_("是否解决")
    )
    return_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("退货时间")
    )
    product_name_model = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("货物品名及型号")
    )
    original_ship_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("发货时间（原件）")
    )
    out_of_warranty = models.BooleanField(
        default=False,
        verbose_name=_("是否过保")
    )
    sn = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name=_("SN")
    )
    pn = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name=_("PN")
    )
    return_reason_description = models.TextField(
        blank=True,
        verbose_name=_("退货原因描述")
    )
    rca = models.TextField(
        blank=True,
        verbose_name=_("RCA")
    )
    
    
  
    after_sales_cost = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("售后成本")
    )
    charge_details = models.TextField(
        blank=True,
        verbose_name=_("收费明细")
    )
    ship_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("寄货时间")
    )
    customer_return_required = models.BooleanField(
        default=False,
        verbose_name=_("是否需客户寄回")
    )

    shipped_item_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("寄货品名")
    )
    r_sn = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("R_SN")
    )
    r_pn = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("R_PN")
    )
    equipment_no = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("设备编号")
    )
    outbound_order_no = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("出库单号")
    )
    shipping_info = models.TextField(
        blank=True,
        verbose_name=_("寄货信息")
    )
    tracking_no = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("运单号")
    )
    source_warehouse = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("拿货仓库")
    )

    # -------- Audit Fields --------
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("创建时间")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("更新时间")
    )

    class Meta:
        verbose_name = _("售后记录")
        verbose_name_plural = _("售后记录")
        ordering = ["-return_date"]
        indexes = [
            models.Index(fields=["after_sales_no"]),
            models.Index(fields=["sn"]),
            models.Index(fields=["pn"]),
            models.Index(fields=["return_date"]),
            models.Index(fields=["resolved"]),
        ]

    def __str__(self):
        return f"{self.after_sales_no} | {self.product_name_model}"

    def save(self, *args, **kwargs):
        """
        Optional hook for future business rules.
        Currently safe and bug‑free.
        """
        super().save(*args, **kwargs)
