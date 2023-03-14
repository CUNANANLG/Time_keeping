from import_export import fields, resources
from datetime import timedelta

from .models import TimeRecord


class TimeRecordResource(resources.ModelResource):
    total_hours = fields.Field()

    class Meta:
        model = TimeRecord
        fields = ('id', 'user', 'time_in', 'time_out', 'total_hours')

    def dehydrate_user(self, time_record):
        return time_record.user.get_full_name()

    def dehydrate_total_hours(self, time_record):
        if time_record.time_in and time_record.time_out:
            total_time = time_record.time_out - time_record.time_in
            hours = int(total_time.total_seconds() // 3600)
            minutes = int((total_time.total_seconds() % 3600) // 60)
            return f"{hours:02d}:{minutes:02d}"
        else:
            return ""

    def after_export(self, queryset, data, *args, **kwargs):    
        total_seconds = sum((tr.time_out - tr.time_in).total_seconds() for tr in queryset if tr.time_in and tr.time_out)
        total_hours = str(timedelta(seconds=total_seconds))
        data.append(['', '', '', 'Total hours:', total_hours])
        return data

