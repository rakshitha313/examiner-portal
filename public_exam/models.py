from django.db import models
from examiner.models import Examiner
import uuid


class PublicExam(models.Model):
    examiner = models.ForeignKey(Examiner, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    duration = models.PositiveIntegerField(default=30)

    total_questions = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    is_published = models.BooleanField(default=False)
    exam_code = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.exam_code:
            self.exam_code = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PublicQuestion(models.Model):
    exam = models.ForeignKey(PublicExam, on_delete=models.CASCADE)
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    answer = models.CharField(max_length=20)
    marks = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.question[:50]


class Candidate(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} - {self.email}"


class ExamAttempt(models.Model):
    exam = models.ForeignKey(PublicExam, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    entered_name = models.CharField(max_length=150, blank=True, null=True)
    entered_email = models.EmailField(blank=True, null=True)
    entered_phone = models.CharField(max_length=15, blank=True, null=True)

    score = models.PositiveIntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entered_name} - {self.exam.title}"


class CandidateAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(PublicQuestion, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=20, blank=True, null=True)