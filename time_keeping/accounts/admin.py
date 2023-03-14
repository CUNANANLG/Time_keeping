from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rangefilter.filters import DateRangeFilter
from import_export.admin import ImportExportModelAdmin
from .resources import TimeRecordResource
from .models import User, TimeRecord


class EmployeeAdmin(UserAdmin, ImportExportModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active')
    list_per_page = 20

    def toggle_active(self, request, queryset):
        for user in queryset:
            user.is_active = not user.is_active
            user.save()

    toggle_active.short_description = 'Toggle active status'

    actions = [toggle_active]

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        elif obj and obj.is_superuser:
            return False
        else:
            return True

    def save_model(self, request, obj, form, change):
        obj.username = str(obj.id) + ' ' + obj.first_name + ' ' + obj.last_name
        obj.set_password(str(obj.id))
        super().save_model(request, obj, form, change)
    add_fieldsets = (
        (None, {
            'fields': ('id', 'first_name', 'last_name','password1', 'password2'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )

admin.site.register(User, EmployeeAdmin)


class TimeRecordAdmin(ImportExportModelAdmin):
    resource_class = TimeRecordResource
    list_filter = ('user', ('time_in', DateRangeFilter))
    list_display = ('user', 'time_in', 'time_out', 'total_time_display')
    ordering = ('-time_in',)
    list_per_page = 20

    def check_in_time(self, obj):
        return obj

    def check_out_time(self, obj):
        return obj.time_out.strftime("%H:%M") if obj.time_out else ""

    def total_time_display(self, obj):
        total_time = obj.total_time
        if total_time is None:
            return "-"
        total_seconds = int(total_time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    total_time_display.admin_order_field = 'total_time'


admin.site.register(TimeRecord, TimeRecordAdmin)
admin.site.site_header = "GoCloud Time Keeping Administrator"
