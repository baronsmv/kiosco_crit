from datetime import datetime

from django.db import connections


def obtener_citas(carnet):
    with connections["crit"].cursor() as cursor:
        cursor.execute(
            """
            SELECT cs.NB_SERVICIO,
                   cp.NO_CARNET,
                   kc.FE_CITA,
                   CONCAT(cp.NB_PACIENTE, ' ', cp.NB_PATERNO) AS nombre_paciente,
                   CONCAT(cu.NB_USUARIO, ' ', cu.NB_PATERNO)  AS nombre_colaborador
            FROM SCRITS2.C_PACIENTE cp
                     INNER JOIN SCRITS2.K_PACIENTE_CITA kpc ON cp.FL_PACIENTE = kpc.FL_PACIENTE
                     INNER JOIN SCRITS2.K_CITA kc ON kpc.FL_CITA = kc.FL_CITA
                     INNER JOIN SCRITS2.C_SERVICIO cs ON kc.FL_SERVICIO = cs.FL_SERVICIO
                     INNER JOIN SCRITS2.C_USUARIO cu ON kc.FL_USUARIO = cu.FL_USUARIO
            WHERE cp.NO_CARNET = %s
            ORDER BY kc.FE_CITA DESC
            """,
            [carnet],
        )
        rows = cursor.fetchall()

    if not rows:
        return

    # Datos del paciente (tomados de la primera fila)
    paciente = {
        "no_carnet": rows[0][1],
        "nombre": rows[0][3],
    }

    # Citas
    citas = [
        {
            "nb_servicio": row[0],
            "fe_cita": row[2],
            "nombre_colaborador": row[4],
        }
        for row in rows
    ]

    return paciente, citas


def formatear_citas(paciente, citas):
    if not paciente:
        return None

    # Formatear fecha a string legible, ej: "09/12/2010 08:55"
    def formatear_fecha(fecha):
        if isinstance(fecha, datetime):
            return fecha.strftime("%d/%m/%Y %H:%M")
        return str(fecha)

    paciente_formateado = {
        "Nombre": paciente.get("nombre", ""),
        "Carnet": paciente.get("no_carnet", ""),
    }

    citas_formateadas = tuple(
        (
            cita.get("nb_servicio", ""),
            formatear_fecha(cita.get("fe_cita")),
            cita.get("nombre_colaborador", ""),
        )
        for cita in citas
    )

    return paciente_formateado, citas_formateadas
