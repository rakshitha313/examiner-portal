from django import forms
from django.utils import timezone
from .models import PublicExam, PublicQuestion

class PublicExamForm(forms.ModelForm):
    class Meta:
        model = PublicExam
        fields = [
            'title', 'description', 'duration',
            'total_questions', 'total_marks',
            'start_time', 'end_time'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']

        if self.instance and self.instance.pk:
            if self.instance.start_time:
                self.initial['start_time'] = timezone.localtime(self.instance.start_time).strftime('%Y-%m-%dT%H:%M')
            if self.instance.end_time:
                self.initial['end_time'] = timezone.localtime(self.instance.end_time).strftime('%Y-%m-%dT%H:%M')


class PublicQuestionForm(forms.ModelForm):
    ANSWER_CHOICES = [
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
        ('option3', 'Option 3'),
        ('option4', 'Option 4'),
    ]

    answer = forms.ChoiceField(choices=ANSWER_CHOICES)

    class Meta:
        model = PublicQuestion
        fields = ['question', 'option1', 'option2', 'option3', 'option4', 'answer', 'marks', 'explanation']


class UploadExcelForm(forms.Form):
    file = forms.FileField()