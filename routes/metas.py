from flask import Blueprint, render_template, request, redirect, url_for, session
from database.connection import get_connection, release_connection
from datetime import datetime


metas = Blueprint("metas", __name__)


# LISTAR METAS
@metas.route("/metas")
def listar():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, titulo, descricao, prazo, status, criado_em
        FROM metas
        WHERE usuario_id = %s
        ORDER BY
            CASE
                WHEN status = 'pendente' THEN 0
                ELSE 1
            END,
            prazo ASC NULLS LAST,
            titulo ASC
    """, (session["usuario_id"],))

    metas_lista = cursor.fetchall()

    cursor.close()
    release_connection(conn)

    return render_template(
        "metas.html",
        metas=metas_lista
    )


# NOVA META
@metas.route("/metas/nova", methods=["GET", "POST"])
def nova():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        prazo = request.form.get("prazo", "").strip()

        if not titulo:
            return redirect(url_for("metas.nova"))

        # VALIDAÇÃO DA DATA
        if prazo:

            try:
                # Obriga exatamente o formato YYYY-MM-DD
                if len(prazo) != 10:
                    return redirect(url_for("metas.nova"))

                datetime.strptime(prazo, "%Y-%m-%d")

            except ValueError:
                return redirect(url_for("metas.nova"))

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO metas (
                    usuario_id,
                    titulo,
                    descricao,
                    prazo
                )
                VALUES (%s, %s, %s, %s)
            """, (
                session["usuario_id"],
                titulo,
                descricao if descricao else None,
                prazo if prazo else None
            ))

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao salvar meta: {erro}", 500

        cursor.close()
        release_connection(conn)

        return redirect(url_for("metas.listar"))

    return render_template("meta_nova.html")


# EDITAR META
@metas.route(
    "/metas/<int:id>/editar",
    methods=["GET", "POST"]
)
def editar(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        prazo = request.form.get("prazo", "").strip()

        if not titulo:
            cursor.close()
            release_connection(conn)

            return redirect(
                url_for("metas.editar", id=id)
            )

        # VALIDAÇÃO DA DATA
        if prazo:

            try:
                if len(prazo) != 10:
                    cursor.close()
                    release_connection(conn)

                    return redirect(
                        url_for("metas.editar", id=id)
                    )

                datetime.strptime(prazo, "%Y-%m-%d")

            except ValueError:
                cursor.close()
                release_connection(conn)

                return redirect(
                    url_for("metas.editar", id=id)
                )

        try:

            cursor.execute("""
                UPDATE metas
                SET titulo = %s,
                    descricao = %s,
                    prazo = %s
                WHERE id = %s
                AND usuario_id = %s
            """, (
                titulo,
                descricao if descricao else None,
                prazo if prazo else None,
                id,
                session["usuario_id"]
            ))

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao atualizar meta: {erro}", 500

        cursor.close()
        release_connection(conn)

        return redirect(url_for("metas.listar"))

    cursor.execute("""
        SELECT id, titulo, descricao, prazo, status
        FROM metas
        WHERE id = %s
        AND usuario_id = %s
    """, (
        id,
        session["usuario_id"]
    ))

    meta = cursor.fetchone()

    cursor.close()
    release_connection(conn)

    if not meta:
        return redirect(url_for("metas.listar"))

    return render_template(
        "meta_editar.html",
        meta=meta
    )


# CONCLUIR META
@metas.route(
    "/metas/<int:id>/concluir",
    methods=["POST"]
)
def concluir(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE metas
            SET status = 'concluida'
            WHERE id = %s
            AND usuario_id = %s
        """, (
            id,
            session["usuario_id"]
        ))

        conn.commit()

    except Exception as erro:

        conn.rollback()
        cursor.close()
        release_connection(conn)

        return f"Erro ao concluir meta: {erro}", 500

    cursor.close()
    release_connection(conn)

    return redirect(url_for("metas.listar"))


# EXCLUIR META
@metas.route(
    "/metas/<int:id>/excluir",
    methods=["POST"]
)
def excluir(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM metas
            WHERE id = %s
            AND usuario_id = %s
        """, (
            id,
            session["usuario_id"]
        ))

        conn.commit()

    except Exception as erro:

        conn.rollback()
        cursor.close()
        release_connection(conn)

        return f"Erro ao excluir meta: {erro}", 500

    cursor.close()
    release_connection(conn)

    return redirect(url_for("metas.listar"))