import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.models import SampleStudent


FIELDS_MAP = {
    "Marital status": "estado_civil",
    "Application mode": "modo_aplicacion",
    "Application order": "orden_aplicacion",
    "Course": "curso",
    "Daytime/evening attendance": "asistencia",
    "Previous qualification": "calificacion_previa",
    "Previous qualification (grade)": "nota_previa",
    "Nacionality": "nacionalidad",
    "Mother's qualification": "estudios_madre",
    "Father's qualification": "estudios_padre",
    "Mother's occupation": "ocupacion_madre",
    "Father's occupation": "ocupacion_padre",
    "Admission grade": "nota_admision",
    "Displaced": "desplazado",
    "Educational special needs": "nee",
    "Debtor": "deudor",
    "Tuition fees up to date": "matricula_al_dia",
    "Gender": "genero",
    "Scholarship holder": "becado",
    "Age at enrollment": "edad",
    "International": "internacional",
    "Curricular units 1st sem (credited)": "cu1_creditos",
    "Curricular units 1st sem (enrolled)": "cu1_inscritas",
    "Curricular units 1st sem (evaluations)": "cu1_evaluaciones",
    "Curricular units 1st sem (approved)": "cu1_aprobadas",
    "Curricular units 1st sem (grade)": "cu1_nota",
    "Curricular units 1st sem (without evaluations)": "cu1_sin_eval",
    "Curricular units 2nd sem (credited)": "cu2_creditos",
    "Curricular units 2nd sem (enrolled)": "cu2_inscritas",
    "Curricular units 2nd sem (evaluations)": "cu2_evaluaciones",
    "Curricular units 2nd sem (approved)": "cu2_aprobadas",
    "Curricular units 2nd sem (grade)": "cu2_nota",
    "Curricular units 2nd sem (without evaluations)": "cu2_sin_eval",
    "Unemployment rate": "tasa_desempleo",
    "Inflation rate": "inflacion",
    "GDP": "pib",
}

TARGET_FIELD = "Target"
EXPECTED_TARGET = "Enrolled"
MAX_STUDENTS = 20


class Command(BaseCommand):
    help = "Carga 20 estudiantes con Target=Enrolled desde dataset/data.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Elimina los registros existentes antes de cargar los estudiantes demo.",
        )

    def handle(self, *args, **options):
        if not options["force"] and SampleStudent.objects.count() >= MAX_STUDENTS:
            self.stdout.write(
                self.style.WARNING(
                    "Ya existen estudiantes de muestra. Usa --force para regenerarlos."
                )
            )
            return

        if options["force"]:
            deleted, _ = SampleStudent.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Se eliminaron {deleted} registros."))

        dataset_path = Path(settings.BASE_DIR).parent / "dataset" / "data.csv"
        if not dataset_path.exists():
            raise CommandError(
                f"No se encontró el archivo dataset en {dataset_path}"
            )

        students_to_create = []
        with dataset_path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=";")
            cleaned_fieldnames = [name.strip() for name in reader.fieldnames or []]
            reader.fieldnames = cleaned_fieldnames

            for row_index, raw_row in enumerate(reader, start=1):
                row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in raw_row.items()}

                if row.get(TARGET_FIELD) != EXPECTED_TARGET:
                    continue

                mapped_data = {
                    "full_name": f"Estudiante Enrolled {len(students_to_create) + 1}",
                    "email": f"estudiante{len(students_to_create) + 1}@demo.edu",
                    "source_row": row_index,
                }

                for source_field, model_field in FIELDS_MAP.items():
                    value = row.get(source_field, "") or "0"
                    try:
                        mapped_data[model_field] = float(value.replace(",", "."))
                    except ValueError:
                        mapped_data[model_field] = 0.0

                students_to_create.append(SampleStudent(**mapped_data))

                if len(students_to_create) == MAX_STUDENTS:
                    break

        if len(students_to_create) < MAX_STUDENTS:
            raise CommandError(
                f"Solo se encontraron {len(students_to_create)} estudiantes con Target={EXPECTED_TARGET}."
            )

        SampleStudent.objects.bulk_create(students_to_create)
        self.stdout.write(
            self.style.SUCCESS(
                f"Se cargaron {len(students_to_create)} estudiantes de muestra."
            )
        )

