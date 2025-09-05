from typing import Optional, Dict


def existe(query: str, id: str, cursor) -> Optional[Dict[str, str]]:
    cursor.execute(query, (id,))
    row = cursor.fetchone()
    return {"nombre": " ".join(row), "id": id} if row else None


def paciente(carnet: str, cursor) -> Optional[Dict[str, str]]:
    return existe(
        query="""
              SELECT NB_PACIENTE, NB_PATERNO, NB_MATERNO
              FROM SCRITS2.C_PACIENTE
              WHERE NO_CARNET = %s
              """,
        id=carnet,
        cursor=cursor,
    )


def colaborador(id: str, cursor) -> Optional[Dict[str, str]]:
    return existe(
        query="""
              SELECT NB_USUARIO, NB_PATERNO, NB_MATERNO
              FROM SCRITS2.C_USUARIO
              WHERE CL_LOGIN = %s
              """,
        id=id,
        cursor=cursor,
    )
