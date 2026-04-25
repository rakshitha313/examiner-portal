
from django.contrib import admin
from .models import PublicExam, PublicQuestion, Candidate, ExamAttempt, CandidateAnswer

admin.site.register(PublicExam)
admin.site.register(PublicQuestion)
admin.site.register(Candidate)
admin.site.register(ExamAttempt)
admin.site.register(CandidateAnswer)
# Register your models here.
