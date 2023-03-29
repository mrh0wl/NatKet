from django.db.models.fields import DateTimeField
from django.utils import timezone


class UCDateTimeField(DateTimeField):
    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            value = timezone.now()
            setattr(model_instance, self.attname, value)
            return value
        else:
            value = getattr(model_instance, self.attname)
            if not isinstance(value, timezone.datetime):
                # assume that the value is a timestamp if it is not a datetime
                value = timezone.make_aware(timezone.datetime.fromtimestamp(
                    int(value))) if value is not None else value

                # an exception might be better than an assumption
                setattr(model_instance, self.attname, value)
            return super(UCDateTimeField, self).pre_save(model_instance, add)
