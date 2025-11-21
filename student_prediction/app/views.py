from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

import torch

from .data_pipeline import get_artifacts, transform_feature_row
from .ml_model_loader import load_model
from .models import SampleStudent

model = load_model()
artifacts = get_artifacts()
class_names = artifacts["class_names"]


def student_demo(request):
    students = SampleStudent.objects.all()[:20]
    return render(
        request,
        "student_demo.html",
        {
            "students": students,
        },
    )


def _binary_pair(value: float):
    normalized = 1.0 if float(value) >= 1 else 0.0
    return normalized, 1.0 - normalized


def _student_feature_row(student: SampleStudent) -> dict:
    tuition_one, tuition_zero = _binary_pair(student.matricula_al_dia)
    scholarship_one, scholarship_zero = _binary_pair(student.becado)
    debtor_one, debtor_zero = _binary_pair(student.deudor)
    gender_one, gender_zero = _binary_pair(student.genero)

    return {
        "curricular_units_2nd_sem_approved": float(student.cu2_aprobadas),
        "curricular_units_1st_sem_approved": float(student.cu1_aprobadas),
        "curricular_units_2nd_sem_grade": float(student.cu2_nota),
        "curricular_units_1st_sem_grade": float(student.cu1_nota),
        "tuition_fees_up_to_date_1": tuition_one,
        "scholarship_holder_1": scholarship_one,
        "debtor_0": debtor_zero,
        "gender_0": gender_zero,
        "curricular_units_2nd_sem_enrolled": float(student.cu2_inscritas),
        "curricular_units_1st_sem_enrolled": float(student.cu1_inscritas),
        "tuition_fees_up_to_date_0": tuition_zero,
        "age_at_enrollment": float(student.edad),
        "application_mode": float(student.modo_aplicacion),
        "scholarship_holder_0": scholarship_zero,
        "debtor_1": debtor_one,
        "gender_1": gender_one,
    }


@require_POST
def predict_student(request, pk):
    student = get_object_or_404(SampleStudent, pk=pk)
    feature_row = _student_feature_row(student)
    model_input = transform_feature_row(feature_row)
    input_tensor = torch.from_numpy(model_input)

    with torch.no_grad():
        logits = model(input_tensor)
        probabilities = torch.softmax(logits, dim=1).squeeze(0)
        pred_idx = torch.argmax(probabilities).item()

    prediction = class_names[pred_idx]

    return JsonResponse(
        {
            "student": student.full_name,
            "prediction": prediction,
            "probability_graduate": round(float(probabilities[1]), 4),
            "probability_dropout": round(float(probabilities[0]), 4),
        }
    )
