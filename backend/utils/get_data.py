from datetime import datetime

from django.db import connections


def obtener_citas(carnet, fecha=None):
    with connections["crit"].cursor() as cursor:
        # Primero buscamos el paciente por el carnet
        cursor.execute(
            """
            SELECT NB_PACIENTE, NB_PATERNO, NO_CARNET
            FROM SCRITS2.C_PACIENTE
            WHERE NO_CARNET = %s
            """,
            [carnet],
        )
        paciente_row = cursor.fetchone()

        if not paciente_row:
            return {"error": "paciente_no_encontrado"}

        paciente = {
            "nombre": f"{paciente_row[0]} {paciente_row[1]}",
            "no_carnet": paciente_row[2],
        }

        # Luego buscamos las citas (si existen)
        query = """
                SELECT cs.NB_SERVICIO,
                       kc.FE_CITA,
                       CONCAT(cu.NB_USUARIO, ' ', cu.NB_PATERNO) AS nombre_colaborador
                FROM SCRITS2.C_PACIENTE cp
                         INNER JOIN SCRITS2.K_PACIENTE_CITA kpc ON cp.FL_PACIENTE = kpc.FL_PACIENTE
                         INNER JOIN SCRITS2.K_CITA kc ON kpc.FL_CITA = kc.FL_CITA
                         INNER JOIN SCRITS2.C_SERVICIO cs ON kc.FL_SERVICIO = cs.FL_SERVICIO
                         INNER JOIN SCRITS2.C_USUARIO cu ON kc.FL_USUARIO = cu.FL_USUARIO
                WHERE cp.NO_CARNET = %s \
                """
        params = [carnet]

        if fecha:
            query += " AND CAST(kc.FE_CITA AS DATE) = %s"
            params.append(fecha)

        query += " ORDER BY kc.FE_CITA DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        citas = [
            {
                "nb_servicio": row[0],
                "fe_cita": row[1],
                "nombre_colaborador": row[2],
            }
            for row in rows
        ]

        return {
            "paciente": paciente,
            "citas": citas,
        }


def formatear_citas(paciente, citas):
    if not paciente:
        return None

    paciente_fmt = {
        "Nombre": paciente.get("nombre", ""),
        "Carnet": paciente.get("no_carnet", ""),
    }

    def fmt(fecha):
        return (
            fecha.strftime("%d/%m/%Y %H:%M")
            if isinstance(fecha, datetime)
            else str(fecha)
        )

    citas_fmt = tuple(
        (c["nb_servicio"], fmt(c["fe_cita"]), c["nombre_colaborador"]) for c in citas
    )

    return paciente_fmt, citas_fmt
