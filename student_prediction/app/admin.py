from django.contrib import admin

from .models import SampleStudent


@admin.register(SampleStudent)
class SampleStudentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "curso", "prob_dropout_proxy", "created_at")
    search_fields = ("full_name", "email")
    list_filter = ("curso",)

    def prob_dropout_proxy(self, obj):
        return f"{obj.cu1_aprobadas}/{obj.cu1_inscritas}"

    prob_dropout_proxy.short_description = "CU1 aprobadas/inscritas"
