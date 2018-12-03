from datetime import datetime

from django.core.exceptions import ValidationError
from django.forms import ModelForm

from portfolio.models import Trade


# create ModelForm class for Trade model, this will use all the same fields and field criteria
class TradeInputForm(ModelForm):
    class Meta:
        model = Trade
        fields = '__all__'
        # override field data
        labels = {'timestamp': 'Time Stamp'}

    # custom validation of timestamp
    def clean_timestamp(self):
        data = self.cleaned_data['timestamp']
        if data > datetime.date.today():
            raise ValidationError('Time stamp is in the future')
