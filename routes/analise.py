from flask import Blueprint, render_template, session, redirect, url_for
from database.connection import get_connection, release_connection


analise = Blueprint("analise", __name__)


@analise.route("/analise-perfil")
def perfil():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario_id = session["usuario_id"]

    conn = get_connection()
    cursor = conn.cursor()

    # Total de candidaturas
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM candidaturas
        WHERE usuario_id = %s
        """,
        (usuario_id,)
    )

    total_candidaturas = cursor.fetchone()[0]

    # Total de entrevistas
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM entrevistas i
        INNER JOIN candidaturas c
            ON i.candidatura_id = c.id
        WHERE c.usuario_id = %s
        """,
        (usuario_id,)
    )

    total_entrevistas = cursor.fetchone()[0]

    # Total de currículos
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM curriculos
        WHERE usuario_id = %s
        """,
        (usuario_id,)
    )

    total_curriculos = cursor.fetchone()[0]

    # Status das candidaturas
    cursor.execute(
        """
        SELECT status, COUNT(*)
        FROM candidaturas
        WHERE usuario_id = %s
        GROUP BY status
        """,
        (usuario_id,)
    )

    status_candidaturas = cursor.fetchall()

    cursor.close()
    release_connection(conn)

    # Define o nível de atividade
    if total_candidaturas >= 10 or total_entrevistas >= 3:
        nivel_atividade = "Alto"
    elif total_candidaturas >= 5 or total_entrevistas >= 1:
        nivel_atividade = "Médio"
    else:
        nivel_atividade = "Inicial"

    return render_template(
        "analise_perfil.html",
        total_candidaturas=total_candidaturas,
        total_entrevistas=total_entrevistas,
        total_curriculos=total_curriculos,
        status_candidaturas=status_candidaturas,
        nivel_atividade=nivel_atividade
    )