from flask import Blueprint, render_template, session, redirect, url_for
from database.connection import get_connection


dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def inicio():

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

    # Candidaturas em andamento
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM candidaturas
        WHERE usuario_id = %s
        AND status = 'Em andamento'
        """,
        (usuario_id,)
    )

    candidaturas_andamento = cursor.fetchone()[0]

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

    # Dados para o gráfico de evolução
    cursor.execute(
        """
        SELECT
            DATE(criado_em) AS data,
            COUNT(*) AS quantidade
        FROM candidaturas
        WHERE usuario_id = %s
        GROUP BY DATE(criado_em)
        ORDER BY DATE(criado_em)
        """,
        (usuario_id,)
    )

    dados_grafico = cursor.fetchall()

    grafico_labels = [
        item[0].strftime("%d/%m/%Y")
        for item in dados_grafico
    ]

    grafico_valores = [
        item[1]
        for item in dados_grafico
    ]

    # Próximas entrevistas
    cursor.execute(
        """
        SELECT
            i.id,
            i.data_hora,
            i.tipo,
            c.cargo,
            e.nome AS empresa
        FROM entrevistas i
        INNER JOIN candidaturas c
            ON i.candidatura_id = c.id
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE c.usuario_id = %s
        AND i.data_hora >= CURRENT_TIMESTAMP
        ORDER BY i.data_hora ASC
        LIMIT 5
        """,
        (usuario_id,)
    )

    proximas_entrevistas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_candidaturas=total_candidaturas,
        candidaturas_andamento=candidaturas_andamento,
        total_entrevistas=total_entrevistas,
        total_curriculos=total_curriculos,
        grafico_labels=grafico_labels,
        grafico_valores=grafico_valores,
        proximas_entrevistas=proximas_entrevistas
    )