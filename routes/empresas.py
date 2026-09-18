from flask import Blueprint, render_template, request, redirect, url_for, session
from database.connection import get_connection, release_connection


empresas = Blueprint("empresas", __name__)


# LISTAR EMPRESAS
@empresas.route("/empresas")
def listar():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario_id = session["usuario_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, site, criado_em
        FROM empresas
        WHERE usuario_id = %s
        ORDER BY nome ASC
    """, (usuario_id,))

    empresas_lista = cursor.fetchall()

    cursor.close()
    release_connection(conn)

    return render_template(
        "empresas.html",
        empresas=empresas_lista
    )


# NOVA EMPRESA
@empresas.route("/empresas/nova", methods=["GET", "POST"])
def nova():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario_id = session["usuario_id"]

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        site = request.form.get("site", "").strip()

        if not nome:
            return redirect(url_for("empresas.nova"))

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO empresas (nome, site, usuario_id)
                VALUES (%s, %s, %s)
            """, (nome, site, usuario_id))

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao salvar empresa: {erro}", 500

        cursor.close()
        release_connection(conn)

        return redirect(url_for("empresas.listar"))

    return render_template("empresa_nova.html")


# EDITAR EMPRESA
@empresas.route("/empresas/<int:id>/editar", methods=["GET", "POST"])
def editar(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario_id = session["usuario_id"]

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        site = request.form.get("site", "").strip()

        try:

            cursor.execute("""
                UPDATE empresas
                SET nome = %s,
                    site = %s
                WHERE id = %s
                  AND usuario_id = %s
            """, (nome, site, id, usuario_id))

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao atualizar empresa: {erro}", 500

        cursor.close()
        release_connection(conn)

        return redirect(url_for("empresas.listar"))

    cursor.execute("""
        SELECT id, nome, site
        FROM empresas
        WHERE id = %s
          AND usuario_id = %s
    """, (id, usuario_id))

    empresa = cursor.fetchone()

    cursor.close()
    release_connection(conn)

    if not empresa:
        return redirect(url_for("empresas.listar"))

    return render_template(
        "empresa_editar.html",
        empresa=empresa
    )


# EXCLUIR EMPRESA
@empresas.route("/empresas/<int:id>/excluir", methods=["POST"])
def excluir(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario_id = session["usuario_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM empresas
            WHERE id = %s
              AND usuario_id = %s
        """, (id, usuario_id))

        conn.commit()

    except Exception as erro:

        conn.rollback()
        cursor.close()
        release_connection(conn)

        return f"Erro ao excluir empresa: {erro}", 500

    cursor.close()
    release_connection(conn)

    return redirect(url_for("empresas.listar"))