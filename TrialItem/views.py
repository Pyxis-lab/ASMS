import datetime
import re

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.http import urlencode
from django.utils.translation import gettext as _
from django.contrib import messages
from django.core.paginator import EmptyPage
from django.db.models import Q
from django.db import transaction

import openpyxl
from openpyxl.styles import PatternFill
from io import BytesIO
import logging

from .models import TrialItem

logger = logging.getLogger(__name__)


EXCEL_COLUMN_MAP = [
    ('client_name', '客户名称'),
    ('project_manager', '项目负责人'),
    ('project_site', '项目现场'),
    ('trial_start_date', '试用时间'),
    ('trial_period_days', '试用周期'),
    ('expiration_date', '到期时间'),
    ('trial_days', '已试用时间'),
    ('over_due_status', '是否超期'),
    ('closed', '是否完结'),
    ('resell', '是否转销售'),
    (None, ''),
    ('sales_amount', '销售金额'),
    ('return_date', '还回时间'),
    ('product_model', '产品名称'),
    ('quantity', '数量'),
    ('sn', 'SN'),
    ('pn', 'PN'),
    ('shipping_info', '收货信息'),
    ('contract_no', '合同号'),
    ('logistics_info', '物流信息'),
    ('outbound_shipment_number', '出库单号'),
    ('warehouse', '拿货仓库'),
    ('notes', '备注'),
]


def parse_boolean_value(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    str_value = str(value).strip()
    if str_value in ('是', 'Y', 'Yes', 'YES', 'true', 'True', 'TRUE', '1'):
        return True
    return False


def parse_datetime_value(value):
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, float):
        try:
            dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=value)
            return dt.date()
        except (OverflowError, ValueError):
            pass
    str_value = str(value).strip()
    datetime_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d-%m-%Y',
        '%m/%d/%Y',
    ]
    for fmt in datetime_formats:
        try:
            dt = datetime.datetime.strptime(str_value, fmt)
            return dt.date()
        except ValueError:
            continue
    return None


def validate_row(row_data, row_num):
    errors = []
    
    client_name = row_data.get('client_name')
    if client_name is None or (isinstance(client_name, str) and not client_name.strip()):
        errors.append(f"第{row_num}行: 客户名称不能为空")
    
    product_model = row_data.get('product_model')
    if product_model is None or (isinstance(product_model, str) and not product_model.strip()):
        errors.append(f"第{row_num}行: 产品名称不能为空")
    
    trial_start_date = row_data.get('trial_start_date')
    if trial_start_date is None or (isinstance(trial_start_date, str) and not trial_start_date.strip()):
        errors.append(f"第{row_num}行: 试用时间不能为空")
    elif parse_datetime_value(trial_start_date) is None:
        errors.append(f"第{row_num}行: 试用时间格式无法识别（{trial_start_date}）")
    
    trial_period = row_data.get('trial_period_days')
    if trial_period is not None:
        if isinstance(trial_period, str):
            trial_period = trial_period.strip()
        if trial_period:
            if not re.search(r'\d+', str(trial_period)):
                errors.append(f"第{row_num}行: 试用周期必须包含数字（如：7天、30、15天）")
    
    trial_days = row_data.get('trial_days')
    if trial_days is not None:
        if isinstance(trial_days, str):
            trial_days = trial_days.strip()
            if trial_days:
                try:
                    int(trial_days)
                except ValueError:
                    errors.append(f"第{row_num}行: 已试用时间必须是整数")
        elif not isinstance(trial_days, int):
            errors.append(f"第{row_num}行: 已试用时间必须是整数")
    
    return errors


class TrialItemListView(LoginRequiredMixin, ListView):
    model = TrialItem
    template_name = 'TrialItem/trialitem_list.html'
    context_object_name = 'items'
    paginate_by = 50
    login_url = '/login/'

    def paginate_queryset(self, queryset, page_size):
        """Override to handle invalid page numbers gracefully.
        Instead of raising Http404, redirect to the last valid page."""
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            # Non-integer page: redirect to page 1
            page_number = 1

        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except EmptyPage:
            # Invalid page number: redirect to last page
            page = paginator.page(paginator.num_pages)
            return (paginator, page, page.object_list, page.has_other_pages())

    def get_queryset(self):
        TrialItem.refresh_time_based_fields_daily()
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        over_due_status = self.request.GET.get('over_due_status', '')
        closed = self.request.GET.get('closed', '')
        resell = self.request.GET.get('resell', '')

        if search_query:
            queryset = queryset.filter(
                Q(client_name__icontains=search_query) |
                Q(project_manager__icontains=search_query) |
                Q(product_model__icontains=search_query) |
                Q(sn__icontains=search_query) |
                Q(pn__icontains=search_query) |
                Q(contract_no__icontains=search_query)
            )

        if over_due_status:
            queryset = queryset.filter(over_due_status=over_due_status)

        if closed != '':
            queryset = queryset.filter(closed=closed == 'True')

        if resell != '':
            queryset = queryset.filter(resell=resell == 'True')

        return queryset.order_by('-trial_start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_over_due'] = self.request.GET.get('over_due_status', '')
        context['selected_closed'] = self.request.GET.get('closed', '')
        context['selected_resell'] = self.request.GET.get('resell', '')

        # Build filter_params: preserves search/filter state across pagination
        # Format: "&search=foo&over_due_status=due&closed=True" (prefixed with &)
        params = {}
        for param in ['search', 'over_due_status', 'closed', 'resell']:
            value = self.request.GET.get(param, '')
            if value:
                params[param] = value
        context['filter_params'] = '&' + urlencode(params) if params else ''

        return context


class TrialItemDetailView(LoginRequiredMixin, DetailView):
    model = TrialItem
    template_name = 'TrialItem/trialitem_detail.html'
    context_object_name = 'item'
    login_url = '/login/'

    def get_object(self, queryset=None):
        TrialItem.refresh_time_based_fields_daily()
        return super().get_object(queryset)


class TrialItemProgressView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, pk):
        TrialItem.refresh_time_based_fields_daily()
        item = get_object_or_404(TrialItem, pk=pk)
        return JsonResponse({
            'trial_days': item.trial_days,
            'total_days': item.get_trial_period_days_int(),
            'over_due_status': item.over_due_status,
        })


class TrialItemCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TrialItem
    template_name = 'TrialItem/trialitem_form.html'
    context_object_name = 'item'
    permission_required = 'TrialItem.add_trialitem'
    login_url = '/login/'

    fields = [
        'client_name', 'project_manager', 'project_site',
        'trial_start_date', 'trial_period_days',
        'product_model', 'quantity', 'sn', 'pn',
        'shipping_info', 'contract_no', 'logistics_info',
        'outbound_shipment_number', 'warehouse',
        'sales_amount', 'return_date',
        'closed', 'resell',
        'notes',
    ]

    success_url = reverse_lazy('TrialItem:trialitem_list')

    def form_valid(self, form):
        messages.success(self.request, _('试用项目创建成功'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('表单验证失败，请检查输入'))
        return super().form_invalid(form)


class TrialItemUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TrialItem
    template_name = 'TrialItem/trialitem_form.html'
    context_object_name = 'item'
    permission_required = 'TrialItem.change_trialitem'
    login_url = '/login/'

    fields = [
        'client_name', 'project_manager', 'project_site',
        'trial_start_date', 'trial_period_days',
        'product_model', 'quantity', 'sn', 'pn',
        'shipping_info', 'contract_no', 'logistics_info',
        'outbound_shipment_number', 'warehouse',
        'sales_amount', 'return_date',
        'closed', 'resell',
        'notes',
    ]

    success_url = reverse_lazy('TrialItem:trialitem_list')

    def form_valid(self, form):
        messages.success(self.request, _('试用项目更新成功'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('表单验证失败，请检查输入'))
        return super().form_invalid(form)


class TrialItemDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TrialItem
    template_name = 'TrialItem/trialitem_confirm_delete.html'
    permission_required = 'TrialItem.delete_trialitem'
    login_url = '/login/'
    success_url = reverse_lazy('TrialItem:trialitem_list')

    def form_valid(self, form):
        messages.success(self.request, _('试用项目删除成功'))
        return super().form_valid(form)


class TrialItemImportView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'TrialItem/trialitem_import.html'
    login_url = '/login/'
    permission_required = 'TrialItem.add_trialitem'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.POST.get('action') == 'confirm':
            return self.process_import(request)

        if 'excel_file' not in request.FILES:
            return render(request, self.template_name, {
                'error_message': _('请选择要上传的Excel文件')
            })

        excel_file = request.FILES['excel_file']
        if not excel_file.name.endswith('.xlsx'):
            return render(request, self.template_name, {
                'error_message': _('只支持.xlsx格式的Excel文件')
            })

        update_existing = request.POST.get('update_existing') == 'on'

        try:
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            ws = wb.active

            preview_data = []
            error_list = []

            for row_num in range(3, ws.max_row + 1):
                row_data = {}
                has_data = False
                for col_idx, (field_name, _header) in enumerate(EXCEL_COLUMN_MAP):
                    if field_name is None:
                        continue
                    cell_value = ws.cell(row=row_num, column=col_idx + 1).value
                    if cell_value is not None:
                        if isinstance(cell_value, str) and cell_value.startswith('='):
                            continue
                        if isinstance(cell_value, str):
                            row_data[field_name] = cell_value.strip()
                        elif field_name in ('trial_start_date', 'expiration_date', 'return_date', 'trial_days', 'closed', 'resell'):
                            row_data[field_name] = cell_value
                        elif isinstance(cell_value, float) and cell_value.is_integer():
                            row_data[field_name] = str(int(cell_value))
                        else:
                            row_data[field_name] = str(cell_value)
                        has_data = True
                
                if not has_data:
                    continue

                row_errors = validate_row(row_data, row_num)
                if row_errors:
                    error_list.append({'row': row_num, 'message': row_errors[0]})
                    continue

                if 'closed' in row_data:
                    row_data['closed'] = parse_boolean_value(row_data['closed'])
                if 'resell' in row_data:
                    row_data['resell'] = parse_boolean_value(row_data['resell'])

                datetime_fields = ['trial_start_date', 'expiration_date', 'return_date']
                for field in datetime_fields:
                    if field in row_data:
                        parsed = parse_datetime_value(row_data[field])
                        # return_date is free text: keep the original if it isn't a date
                        if parsed is None and field == 'return_date':
                            parsed = str(row_data[field])
                        row_data[field] = parsed

                if 'trial_days' in row_data:
                    trial_days_value = row_data['trial_days']
                    if isinstance(trial_days_value, str):
                        trial_days_value = trial_days_value.strip()
                        if trial_days_value:
                            try:
                                row_data['trial_days'] = int(trial_days_value)
                            except ValueError:
                                error_list.append({'row': row_num, 'message': f"第{row_num}行: 已试用时间必须是整数"})
                                continue
                        else:
                            row_data['trial_days'] = 0
                    elif not isinstance(trial_days_value, int):
                        try:
                            row_data['trial_days'] = int(trial_days_value)
                        except (ValueError, TypeError):
                            error_list.append({'row': row_num, 'message': f"第{row_num}行: 已试用时间必须是整数"})
                            continue
                else:
                    row_data['trial_days'] = 0

                action_type = 'create'
                original_data = None
                if update_existing and 'contract_no' in row_data and row_data['contract_no']:
                    try:
                        existing_items = TrialItem.objects.filter(contract_no=row_data['contract_no'])
                        if existing_items.count() == 1:
                            existing_item = existing_items.first()
                            action_type = 'update'
                            original_data = {}
                            for field_name, _label in EXCEL_COLUMN_MAP:
                                if field_name and hasattr(existing_item, field_name):
                                    value = getattr(existing_item, field_name)
                                    if value is not None:
                                        original_data[field_name] = str(value)
                        elif existing_items.count() > 1:
                            error_list.append({
                                'row': row_num,
                                'message': f"第{row_num}行: 发现多条合同号为 '{row_data['contract_no']}' 的记录，无法确定更新哪一条"
                            })
                            continue
                        else:
                            action_type = 'create'
                    except Exception as e:
                        logger.error(f'查询合同号失败: {row_data['contract_no']}, 错误: {str(e)}')
                        action_type = 'create'

                changed_fields = {}
                if action_type == 'update' and original_data:
                    for field_name, new_value in row_data.items():
                        if field_name in original_data and str(new_value) != original_data[field_name]:
                            changed_fields[field_name] = {
                                'original': original_data[field_name],
                                'new': new_value,
                            }

                preview_data.append({
                    'row_num': row_num,
                    'action': action_type,
                    'data': row_data,
                    'changed_fields': changed_fields,
                })

            create_count = sum(1 for p in preview_data if p['action'] == 'create')
            update_count = sum(1 for p in preview_data if p['action'] == 'update')

            for item in preview_data:
                for field in ['trial_start_date', 'expiration_date', 'return_date']:
                    if isinstance(item['data'].get(field), datetime.date):
                        item['data'][field] = item['data'][field].strftime('%Y-%m-%d')

            request.session['import_preview'] = {
                'preview_data': preview_data,
                'update_existing': update_existing,
                'file_name': excel_file.name,
            }

            return render(request, self.template_name, {
                'preview_mode': True,
                'preview_data': preview_data,
                'create_count': create_count,
                'update_count': update_count,
                'error_count': len(error_list),
                'file_name': excel_file.name,
                'errors': error_list,
            })

        except Exception as e:
            logger.error(f'Excel导入失败: {str(e)}', exc_info=True)
            return render(request, self.template_name, {
                'error_message': f'{_('导入失败：')}{str(e)}'
            })

    def process_import(self, request):
        import_preview = request.session.get('import_preview')
        if not import_preview:
            return render(request, self.template_name, {
                'error_message': _('请先上传文件并预览')
            })

        preview_data = import_preview['preview_data']
        update_existing = import_preview.get('update_existing', True)

        success_count = 0
        updated_count = 0
        failed_count = 0
        error_list = []
        change_summary = []

        batch_size = 100
        records_to_create = []
        records_to_update = []

        try:
            for item in preview_data:
                row_data = item['data']
                row_num = item['row_num']

                for field in ['trial_start_date', 'expiration_date', 'return_date']:
                    if field in row_data and row_data[field]:
                        try:
                            row_data[field] = datetime.datetime.strptime(row_data[field], '%Y-%m-%d').date()
                        except ValueError:
                            if field != 'return_date':
                                row_data[field] = None

                try:
                    if item['action'] == 'update':
                        existing_items = TrialItem.objects.filter(contract_no=row_data['contract_no'])
                        if existing_items.count() == 1:
                            existing_item = existing_items.first()
                            for key, value in row_data.items():
                                setattr(existing_item, key, value)
                            existing_item.save(skip_auto_calc=True)
                            updated_count += 1
                            change_summary.append({
                                'action': 'update',
                                'client_name': row_data.get('client_name', ''),
                                'field_count': len(item.get('changed_fields', {}))
                            })
                        elif existing_items.count() > 1:
                            error_list.append({
                                'row': row_num,
                                'message': f"发现多条合同号为 '{row_data['contract_no']}' 的记录，无法确定更新哪一条"
                            })
                            failed_count += 1
                        else:
                            new_item = TrialItem(**row_data)
                            new_item.save(skip_auto_calc=True)
                            success_count += 1
                            change_summary.append({
                                'action': 'create',
                                'client_name': row_data.get('client_name', ''),
                                'field_count': 0
                            })
                    else:
                        new_item = TrialItem(**row_data)
                        new_item.save(skip_auto_calc=True)
                        success_count += 1
                        change_summary.append({
                            'action': 'create',
                            'client_name': row_data.get('client_name', ''),
                            'field_count': 0
                        })

                except Exception as e:
                    error_list.append({'row': row_num, 'message': str(e)})
                    failed_count += 1

            import_result = {
                'total': len(preview_data),
                'success': success_count,
                'updated': updated_count,
                'failed': failed_count,
                'errors': error_list,
                'summary': change_summary,
            }

            if failed_count == 0:
                messages.success(request, _(f'成功导入 {success_count} 条记录，更新 {updated_count} 条记录'))
            else:
                messages.warning(request, _(f'导入完成：成功 {success_count} 条，更新 {updated_count} 条，失败 {failed_count} 条'))

            del request.session['import_preview']

            return render(request, self.template_name, {'import_result': import_result})

        except Exception as e:
            logger.error(f'Excel导入失败: {str(e)}', exc_info=True)
            del request.session['import_preview']
            return render(request, self.template_name, {
                'error_message': f'{_('导入失败：')}{str(e)}'
            })


class TrialItemExportView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = 'TrialItem.view_trialitem'

    def get(self, request, *args, **kwargs):
        try:
            TrialItem.refresh_time_based_fields_daily()
            records = TrialItem.objects.all().order_by('-trial_start_date')

            output = BytesIO()
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = '试用项目'

            header_row = []
            for _field, label in EXCEL_COLUMN_MAP:
                header_row.append(label if label else '')
            ws.append(header_row)

            # Define cell fill patterns for over_due_status column
            green_fill = PatternFill(start_color='008000', end_color='008000', fill_type='solid')
            yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
            red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')

            # Find the column index of over_due_status (1-indexed)
            over_due_col_idx = None
            for idx, (field_name, _label) in enumerate(EXCEL_COLUMN_MAP, 1):
                if field_name == 'over_due_status':
                    over_due_col_idx = idx
                    break

            for record in records:
                row_data = []
                for field_name, _label in EXCEL_COLUMN_MAP:
                    if field_name is None:
                        row_data.append('')
                    else:
                        value = getattr(record, field_name, '')
                        if isinstance(value, bool):
                            row_data.append('是' if value else '否')
                        elif field_name == 'over_due_status':
                            row_data.append(str(record.over_due_display))
                        elif value is None:
                            row_data.append('')
                        else:
                            row_data.append(str(value))
                ws.append(row_data)

                # Apply conditional formatting only to the over_due_status column
                if over_due_col_idx:
                    row_num = ws.max_row
                    status_display = str(record.over_due_display)
                    if status_display == '未到期':
                        ws.cell(row=row_num, column=over_due_col_idx).fill = green_fill
                    elif status_display == '到期':
                        ws.cell(row=row_num, column=over_due_col_idx).fill = yellow_fill
                    elif status_display == '超期':
                        ws.cell(row=row_num, column=over_due_col_idx).fill = red_fill

            for col in ws.columns:
                max_length = 0
                for cell in col:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[col[0].column_letter].width = adjusted_width

            wb.save(output)
            output.seek(0)

            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=试用项目.xlsx'
            return response

        except Exception as e:
            logger.error(f'Excel导出失败: {str(e)}', exc_info=True)
            messages.error(request, f'{_('导出失败：')}{str(e)}')
            return HttpResponseBadRequest(f'{_('导出失败：')}{str(e)}')