from django.urls import path

from . import views

urlpatterns = [
    path("", views.student_demo, name="student-demo"),
    path("students/<int:pk>/predict/", views.predict_student, name="predict-student"),
]