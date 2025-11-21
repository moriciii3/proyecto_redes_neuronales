from django.db import models


class SampleStudent(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    source_row = models.PositiveIntegerField(help_text="Índice original dentro del dataset")

    estado_civil = models.FloatField()
    modo_aplicacion = models.FloatField()
    orden_aplicacion = models.FloatField()
    curso = models.FloatField()
    asistencia = models.FloatField()
    calificacion_previa = models.FloatField()
    nota_previa = models.FloatField()
    nacionalidad = models.FloatField()
    estudios_madre = models.FloatField()
    estudios_padre = models.FloatField()
    ocupacion_madre = models.FloatField()
    ocupacion_padre = models.FloatField()
    nota_admision = models.FloatField()
    desplazado = models.FloatField()
    nee = models.FloatField()
    deudor = models.FloatField()
    matricula_al_dia = models.FloatField()
    genero = models.FloatField()
    becado = models.FloatField()
    edad = models.FloatField()
    internacional = models.FloatField()
    cu1_creditos = models.FloatField()
    cu1_inscritas = models.FloatField()
    cu1_evaluaciones = models.FloatField()
    cu1_aprobadas = models.FloatField()
    cu1_nota = models.FloatField()
    cu1_sin_eval = models.FloatField()
    cu2_creditos = models.FloatField()
    cu2_inscritas = models.FloatField()
    cu2_evaluaciones = models.FloatField()
    cu2_aprobadas = models.FloatField()
    cu2_nota = models.FloatField()
    cu2_sin_eval = models.FloatField()
    tasa_desempleo = models.FloatField()
    inflacion = models.FloatField()
    pib = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.full_name} (fila {self.source_row})"
