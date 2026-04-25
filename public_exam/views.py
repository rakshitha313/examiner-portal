from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from examiner.models import Examiner
from .models import PublicExam, PublicQuestion, Candidate, ExamAttempt, CandidateAnswer
from .forms import PublicExamForm, PublicQuestionForm
from .forms import  UploadExcelForm
import openpyxl
from django.utils import timezone
from django.contrib import messages
def is_examiner(user):
    return user.groups.filter(name='EXAMINER').exists()


@login_required(login_url='/examiner/login/')
@user_passes_test(is_examiner, login_url='/examiner/login/')
def examiner_dashboard(request):
    examiner = Examiner.objects.get(user=request.user)
    exams = PublicExam.objects.filter(examiner=examiner)
    total_exams = exams.count()
    published_exams = exams.filter(is_published=True).count()

    return render(request, 'public_exam/dashboard.html', {
        'exams': exams,
        'total_exams': total_exams,
        'published_exams': published_exams,
    })


@login_required(login_url='/examiner/login/')
@user_passes_test(is_examiner, login_url='/examiner/login/')
def create_exam(request):
    examiner = Examiner.objects.get(user=request.user)

    if request.method == 'POST':
        form = PublicExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.examiner = examiner
            exam.save()
            return redirect('add-question', pk=exam.id)
    else:
        form = PublicExamForm()

    return render(request, 'public_exam/create_exam.html', {'form': form})


@login_required(login_url='/examiner/login/')
@user_passes_test(is_examiner, login_url='/examiner/login/')
def add_question(request, pk):
    examiner = Examiner.objects.get(user=request.user)
    exam = get_object_or_404(PublicExam, id=pk, examiner=examiner)

    question_form = PublicQuestionForm()
    excel_form = UploadExcelForm()

    if request.method == 'POST':

        # ================= MANUAL QUESTION ADD =================
        if 'manual_submit' in request.POST:
            question_form = PublicQuestionForm(request.POST)
            excel_form = UploadExcelForm()

            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.exam = exam
                question.save()

                actual_questions = PublicQuestion.objects.filter(exam=exam).count()
                actual_marks = PublicQuestion.objects.filter(exam=exam).aggregate(
                    total=Sum('marks')
                )['total'] or 0

                expected_q = exam.total_questions
                expected_m = exam.total_marks

                if actual_questions < expected_q or actual_marks < expected_m:
                    messages.warning(
                        request,
                        f"Question added. Missing: {expected_q - actual_questions} questions and {expected_m - actual_marks} marks."
                    )
                elif actual_questions > expected_q or actual_marks > expected_m:
                    messages.error(
                        request,
                        "Question added, but exam exceeded total questions or marks."
                    )
                else:
                    messages.success(request, "Question added successfully. Exam is complete.")

                return redirect('add-question', pk=exam.id)

        # ================= EXCEL QUESTION UPLOAD =================
        elif 'excel_submit' in request.POST:
            question_form = PublicQuestionForm()
            excel_form = UploadExcelForm(request.POST, request.FILES)

            if excel_form.is_valid():
                excel_file = request.FILES['file']

                try:
                    wb = openpyxl.load_workbook(excel_file)
                    sheet = wb.active

                    added_count = 0
                    skipped_count = 0
                    invalid_count = 0

                    for index, row in enumerate(sheet.iter_rows(values_only=True), start=1):

                        # skip header row
                        if index == 1:
                            continue

                        if not row:
                            skipped_count += 1
                            continue

                        row = list(row) + [None] * (8 - len(row))

                        question_text = str(row[0]).strip() if row[0] else ""
                        option1 = str(row[1]).strip() if row[1] else ""
                        option2 = str(row[2]).strip() if row[2] else ""
                        option3 = str(row[3]).strip() if row[3] else ""
                        option4 = str(row[4]).strip() if row[4] else ""
                        answer = str(row[5]).strip().lower() if row[5] else ""
                        marks = row[6] if row[6] is not None else 1
                        explanation = str(row[7]).strip() if row[7] else ""

                        if not question_text:
                            skipped_count += 1
                            continue

                        if answer not in ['option1', 'option2', 'option3', 'option4']:
                            invalid_count += 1
                            continue

                        try:
                            marks = int(marks)
                        except (TypeError, ValueError):
                            invalid_count += 1
                            continue

                        if PublicQuestion.objects.filter(
                            exam=exam,
                            question__iexact=question_text
                        ).exists():
                            skipped_count += 1
                            continue

                        PublicQuestion.objects.create(
                            exam=exam,
                            question=question_text,
                            option1=option1,
                            option2=option2,
                            option3=option3,
                            option4=option4,
                            answer=answer,
                            marks=marks,
                            explanation=explanation
                        )

                        added_count += 1

                    actual_questions = PublicQuestion.objects.filter(exam=exam).count()
                    actual_marks = PublicQuestion.objects.filter(exam=exam).aggregate(
                        total=Sum('marks')
                    )['total'] or 0

                    expected_q = exam.total_questions
                    expected_m = exam.total_marks

                    if actual_questions < expected_q or actual_marks < expected_m:
                        messages.warning(
                            request,
                            f"{added_count} questions uploaded. Missing: {expected_q - actual_questions} questions and {expected_m - actual_marks} marks."
                        )
                    elif actual_questions > expected_q or actual_marks > expected_m:
                        messages.error(
                            request,
                            f"{added_count} questions uploaded, but exam exceeded limit. Current: {actual_questions} questions and {actual_marks} marks."
                        )
                    else:
                        messages.success(
                            request,
                            f"{added_count} questions uploaded successfully. Exam is complete."
                        )

                    if skipped_count > 0:
                        messages.warning(request, f"{skipped_count} rows were skipped.")

                    if invalid_count > 0:
                        messages.error(request, f"{invalid_count} rows had invalid answer or marks.")

                    return redirect('add-question', pk=exam.id)

                except Exception as e:
                    messages.error(request, f"Excel upload failed: {e}")

    questions = PublicQuestion.objects.filter(exam=exam)

    actual_questions = questions.count()
    actual_marks = questions.aggregate(
    total=Sum('marks')
)['total'] or 0

    return render(request, 'public_exam/add_question.html', {
    'exam': exam,
    'questions': questions,
    'form': question_form,
    'excel_form': excel_form,
    'actual_questions': actual_questions,
    'actual_marks': actual_marks,
})

from django.db.models import Sum

@login_required(login_url='/examiner/login/')
@user_passes_test(is_examiner, login_url='/examiner/login/')
def publish_exam(request, pk):
    examiner = Examiner.objects.get(user=request.user)
    exam = get_object_or_404(PublicExam, id=pk, examiner=examiner)

    actual_questions = PublicQuestion.objects.filter(exam=exam).count()
    actual_marks = PublicQuestion.objects.filter(exam=exam).aggregate(
        total=Sum('marks')
    )['total'] or 0

    if actual_questions != exam.total_questions or actual_marks != exam.total_marks:
        messages.error(request, "❌ Cannot publish! Exam is incomplete")
        return redirect('add-question', pk=exam.id)

    exam.is_published = True
    exam.save()

    exam_link = request.build_absolute_uri(
        reverse('public-exam-entry', kwargs={'exam_code': exam.exam_code})
    )

    return render(request, 'public_exam/publish_success.html', {
        'exam': exam,
        'exam_link': exam_link
    })


def public_exam_entry_view(request, exam_code):
    exam = get_object_or_404(PublicExam, exam_code=exam_code, is_published=True)

    now = timezone.localtime()

    # before exam start
    if now < exam.start_time:
        return render(request, 'public_exam/exam_not_available.html', {
            'exam': exam,
            'message': 'This exam has not started yet.'
        })

    # after exam end
    if now > exam.end_time:
        return render(request, 'public_exam/exam_not_available.html', {
            'exam': exam,
            'message': 'This exam time is over. You cannot attend this exam now.'
        })

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        email_exists = ExamAttempt.objects.filter(
            exam=exam,
            entered_email=email
        ).exists()

        phone_exists = ExamAttempt.objects.filter(
            exam=exam,
            entered_phone=phone
        ).exists()

        if email_exists or phone_exists:
            return render(request, 'public_exam/already_attempted.html', {
                'exam': exam,
                'message': 'This email ID or phone number already exists for this exam.'
            })

        candidate = Candidate.objects.create(
            name=name,
            email=email,
            phone=phone
        )

        attempt = ExamAttempt.objects.create(
            exam=exam,
            candidate=candidate,
            entered_name=name,
            entered_email=email,
            entered_phone=phone
        )

        request.session['attempt_id'] = attempt.id
        return redirect('public-exam-start', exam_code=exam.exam_code)

    return render(request, 'public_exam/public_exam_entry.html', {
        'exam': exam
    })

def public_exam_start_view(request, exam_code):
    exam = get_object_or_404(PublicExam, exam_code=exam_code, is_published=True)

    now = timezone.now()

    if now < exam.start_time:
        return render(request, 'public_exam/exam_not_available.html', {
            'exam': exam,
            'message': 'This exam has not started yet.'
        })

    if now > exam.end_time:
        return render(request, 'public_exam/exam_not_available.html', {
            'exam': exam,
            'message': 'This exam time is over. You cannot attend this exam now.'
        })

    attempt_id = request.session.get('attempt_id')
    if not attempt_id:
        return redirect('public-exam-entry', exam_code=exam_code)

    attempt = get_object_or_404(ExamAttempt, id=attempt_id, exam=exam)
    questions = PublicQuestion.objects.filter(exam=exam)

    return render(request, 'public_exam/public_exam_start.html', {
        'exam': exam,
        'attempt': attempt,
        'questions': questions
    })
def submit_public_exam(request, exam_code):
    if request.method != 'POST':
        return redirect('public-exam-entry', exam_code=exam_code)

    exam = get_object_or_404(PublicExam, exam_code=exam_code, is_published=True)
    attempt_id = request.session.get('attempt_id')
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, exam=exam)

    if attempt.is_submitted:
        return redirect('public-exam-result', exam_code=exam.exam_code)

    questions = PublicQuestion.objects.filter(exam=exam)
    score = 0

    for q in questions:
        selected = request.POST.get(str(q.id))
        print("QUESTION:", q.question)
        print("SELECTED:", selected)
        print("CORRECT:", q.answer)

        CandidateAnswer.objects.create(
            attempt=attempt,
            question=q,
            selected_answer=selected
        )

        if selected == q.answer:
            score += q.marks

    attempt.score = score
    attempt.is_submitted = True
    attempt.save()

    return redirect('public-exam-result', exam_code=exam.exam_code)

def public_exam_result_view(request, exam_code):
    exam = get_object_or_404(PublicExam, exam_code=exam_code, is_published=True)
    attempt_id = request.session.get('attempt_id')
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, exam=exam)

    print("RESULT VIEW HIT")
    print("EXAM:", exam.title)
    print("ATTEMPT ID:", attempt_id)
    print("SCORE:", attempt.score)

    return render(request, 'public_exam/result.html', {
        'exam': exam,
        'attempt': attempt
    })
from .models import ExamAttempt

@login_required(login_url='/examiner/login/')
@user_passes_test(is_examiner, login_url='/examiner/login/')
def examiner_results_view(request):
    examiner = request.user.examiner

    attempts = ExamAttempt.objects.filter(
        exam__examiner=examiner,
        is_submitted=True
    ).order_by('-submitted_at')

    return render(request, 'public_exam/examiner_results.html', {
        'attempts': attempts
    })
@login_required(login_url='/examiner/login/')
@user_passes_test(is_examiner, login_url='/examiner/login/')
def edit_exam(request, pk):
    examiner = Examiner.objects.get(user=request.user)
    exam = get_object_or_404(PublicExam, id=pk, examiner=examiner)

    if request.method == 'POST':
        form = PublicExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('examiner-dashboard')
    else:
        form = PublicExamForm(instance=exam)

    return render(request, 'public_exam/edit_exam.html', {
        'form': form,
        'exam': exam
    })
@login_required(login_url='/examiner/login/')
@user_passes_test(is_examiner, login_url='/examiner/login/')
def delete_exam(request, pk):
    examiner = Examiner.objects.get(user=request.user)
    exam = get_object_or_404(PublicExam, id=pk, examiner=examiner)

    if request.method == "POST":
        exam.delete()
        return redirect('examiner-dashboard')

    return redirect('examiner-dashboard')
@login_required(login_url='/examiner/login/')
@user_passes_test(is_examiner, login_url='/examiner/login/')
def delete_question(request, pk):
    question = get_object_or_404(PublicQuestion, id=pk)

    exam_id = question.exam.id
    question.delete()

    return redirect('add-question', pk=exam_id)
@login_required(login_url='/examiner/login/')
@user_passes_test(is_examiner, login_url='/examiner/login/')
def edit_question(request, pk):
    question = get_object_or_404(PublicQuestion, id=pk)

    if request.method == 'POST':
        form = PublicQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('add-question', pk=question.exam.id)
    else:
        form = PublicQuestionForm(instance=question)

    return render(request, 'public_exam/edit_question.html', {
        'form': form,
        'question': question
    })