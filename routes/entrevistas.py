from flask import Blueprint, render_template, session, redirect, url_for, request
from datetime import datetime
from database.connection import get_connection, release_connection


entrevistas = Blueprint("entrevistas", __name__)


@entrevistas.route("/entrevistas")
def listar():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            i.id,
            i.data_hora,
            i.tipo,
            i.observacoes,
            c.id AS candidatura_id,
            c.cargo,
            e.nome AS empresa
        FROM entrevistas i
        INNER JOIN candidaturas c
            ON i.candidatura_id = c.id
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE c.usuario_id = %s
        ORDER BY i.data_hora ASC
        """,
        (session["usuario_id"],)
    )

    dados = cursor.fetchall()

    cursor.close()
    release_connection(conn)

    return render_template(
        "entrevistas.html",
        entrevistas=dados
    )


@entrevistas.route("/entrevistas/nova", methods=["GET", "POST"])
def nova():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        candidatura_id = request.form["candidatura_id"]

        data = request.form["data"]
        horario = request.form["horario"]

        try:
            data_hora = datetime.strptime(
                f"{data} {horario}",
                "%Y-%m-%d %H:%M"
            )

        except ValueError:
            cursor.close()
            release_connection(conn)
            return "Data ou horário inválido.", 400

        tipo = request.form.get("tipo")
        observacoes = request.form.get("observacoes")

        try:

            cursor.execute(
                """
                SELECT id
                FROM candidaturas
                WHERE id = %s
                AND usuario_id = %s
                """,
                (
                    candidatura_id,
                    session["usuario_id"]
                )
            )

            candidatura = cursor.fetchone()

            if not candidatura:
                cursor.close()
                release_connection(conn)
                return "Candidatura não encontrada.", 404

            cursor.execute(
                """
                INSERT INTO entrevistas (
                    candidatura_id,
                    data_hora,
                    tipo,
                    observacoes
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    candidatura_id,
                    data_hora,
                    tipo,
                    observacoes
                )
            )

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao salvar entrevista: {erro}"

        cursor.close()
        release_connection(conn)

        return redirect(
            url_for("entrevistas.listar")
        )

    cursor.execute(
        """
        SELECT
            c.id,
            c.cargo,
            e.nome AS empresa
        FROM candidaturas c
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE c.usuario_id = %s
        ORDER BY c.criado_em DESC
        """,
        (session["usuario_id"],)
    )

    candidaturas = cursor.fetchall()

    cursor.close()
    release_connection(conn)

    return render_template(
        "entrevista_nova.html",
        candidaturas=candidaturas
    )


@entrevistas.route("/entrevistas/<int:id>")
def detalhes(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            i.id,
            i.data_hora,
            i.tipo,
            i.observacoes,
            c.id AS candidatura_id,
            c.cargo,
            e.nome AS empresa
        FROM entrevistas i
        INNER JOIN candidaturas c
            ON i.candidatura_id = c.id
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE i.id = %s
        AND c.usuario_id = %s
        """,
        (
            id,
            session["usuario_id"]
        )
    )

    entrevista = cursor.fetchone()

    cursor.close()
    release_connection(conn)

    if not entrevista:
        return "Entrevista não encontrada.", 404

    return render_template(
        "entrevista_detalhes.html",
        entrevista=entrevista
    )


@entrevistas.route("/entrevistas/<int:id>/editar", methods=["GET", "POST"])
def editar(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        candidatura_id = request.form["candidatura_id"]

        data = request.form["data"]
        horario = request.form["horario"]

        try:
            data_hora = datetime.strptime(
                f"{data} {horario}",
                "%Y-%m-%d %H:%M"
            )

        except ValueError:
            cursor.close()
            release_connection(conn)
            return "Data ou horário inválido.", 400

        tipo = request.form.get("tipo")
        observacoes = request.form.get("observacoes")

        try:

            cursor.execute(
                """
                SELECT i.id
                FROM entrevistas i
                INNER JOIN candidaturas c
                    ON i.candidatura_id = c.id
                WHERE i.id = %s
                AND c.usuario_id = %s
                """,
                (
                    id,
                    session["usuario_id"]
                )
            )

            entrevista_existente = cursor.fetchone()

            if not entrevista_existente:
                cursor.close()
                release_connection(conn)
                return "Entrevista não encontrada.", 404

            cursor.execute(
                """
                SELECT id
                FROM candidaturas
                WHERE id = %s
                AND usuario_id = %s
                """,
                (
                    candidatura_id,
                    session["usuario_id"]
                )
            )

            candidatura = cursor.fetchone()

            if not candidatura:
                cursor.close()
                release_connection(conn)
                return "Candidatura não encontrada.", 404

            cursor.execute(
                """
                UPDATE entrevistas
                SET
                    candidatura_id = %s,
                    data_hora = %s,
                    tipo = %s,
                    observacoes = %s
                WHERE id = %s
                """,
                (
                    candidatura_id,
                    data_hora,
                    tipo,
                    observacoes,
                    id
                )
            )

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao editar entrevista: {erro}"

        cursor.close()
        release_connection(conn)

        return redirect(
            url_for("entrevistas.listar")
        )

    cursor.execute(
        """
        SELECT
            i.id,
            i.data_hora,
            i.tipo,
            i.observacoes,
            i.candidatura_id
        FROM entrevistas i
        INNER JOIN candidaturas c
            ON i.candidatura_id = c.id
        WHERE i.id = %s
        AND c.usuario_id = %s
        """,
        (
            id,
            session["usuario_id"]
        )
    )

    entrevista = cursor.fetchone()

    if not entrevista:
        cursor.close()
        release_connection(conn)
        return "Entrevista não encontrada.", 404

    cursor.execute(
        """
        SELECT
            c.id,
            c.cargo,
            e.nome AS empresa
        FROM candidaturas c
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE c.usuario_id = %s
        ORDER BY c.criado_em DESC
        """,
        (session["usuario_id"],)
    )

    candidaturas = cursor.fetchall()

    cursor.close()
    release_connection(conn)

    return render_template(
        "entrevista_editar.html",
        entrevista=entrevista,
        candidaturas=candidaturas
    )


@entrevistas.route("/entrevistas/<int:id>/excluir", methods=["POST"])
def excluir(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM entrevistas
            WHERE id = %s
            AND candidatura_id IN (
                SELECT id
                FROM candidaturas
                WHERE usuario_id = %s
            )
            """,
            (
                id,
                session["usuario_id"]
            )
        )

        conn.commit()

    except Exception as erro:

        conn.rollback()
        cursor.close()
        release_connection(conn)

        return f"Erro ao excluir entrevista: {erro}"

    cursor.close()
    release_connection(conn)

    return redirect(
        url_for("entrevistas.listar")
    )