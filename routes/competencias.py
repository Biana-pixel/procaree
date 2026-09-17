from flask import Blueprint, render_template, request, redirect, url_for, session
from database.connection import get_connection


competencias = Blueprint("competencias", __name__)


# LISTAR COMPETÊNCIAS
@competencias.route("/competencias")
def listar():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, nivel, criado_em
        FROM competencias
        WHERE usuario_id = %s
        ORDER BY nome ASC
    """, (session["usuario_id"],))

    competencias_lista = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "competencias.html",
        competencias=competencias_lista
    )


# NOVA COMPETÊNCIA
@competencias.route("/competencias/nova", methods=["GET", "POST"])
def nova():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        nivel = request.form.get("nivel", "").strip()

        if not nome or not nivel:
            return redirect(url_for("competencias.nova"))

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO competencias (
                usuario_id,
                nome,
                nivel
            )
            VALUES (%s, %s, %s)
        """, (
            session["usuario_id"],
            nome,
            nivel
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("competencias.listar"))

    return render_template("competencia_nova.html")


# EDITAR COMPETÊNCIA
@competencias.route(
    "/competencias/<int:id>/editar",
    methods=["GET", "POST"]
)
def editar(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        nivel = request.form.get("nivel", "").strip()

        cursor.execute("""
            UPDATE competencias
            SET nome = %s,
                nivel = %s
            WHERE id = %s
            AND usuario_id = %s
        """, (
            nome,
            nivel,
            id,
            session["usuario_id"]
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("competencias.listar"))

    cursor.execute("""
        SELECT id, nome, nivel
        FROM competencias
        WHERE id = %s
        AND usuario_id = %s
    """, (
        id,
        session["usuario_id"]
    ))

    competencia = cursor.fetchone()

    cursor.close()
    conn.close()

    if not competencia:
        return redirect(url_for("competencias.listar"))

    return render_template(
        "competencia_editar.html",
        competencia=competencia
    )


# EXCLUIR COMPETÊNCIA
@competencias.route(
    "/competencias/<int:id>/excluir",
    methods=["POST"]
)
def excluir(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM competencias
        WHERE id = %s
        AND usuario_id = %s
    """, (
        id,
        session["usuario_id"]
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("competencias.listar"))