from flask import Blueprint, render_template, session, redirect, url_for, request
from database.connection import get_connection, release_connection


curriculos = Blueprint("curriculos", __name__)


# ==============================
# LISTAR CURRÍCULOS
# ==============================

@curriculos.route("/curriculos")
def listar():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            nome,
            arquivo_url,
            criado_em
        FROM curriculos
        WHERE usuario_id = %s
        ORDER BY criado_em DESC
        """,
        (session["usuario_id"],)
    )

    curriculos_lista = cursor.fetchall()

    cursor.close()
    release_connection(conn)

    return render_template(
        "curriculos.html",
        curriculos=curriculos_lista
    )


# ==============================
# NOVO CURRÍCULO
# ==============================

@curriculos.route("/curriculos/novo", methods=["GET", "POST"])
def novo():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        nome = request.form.get("nome")
        arquivo_url = request.form.get("arquivo_url")

        if not nome:
            return "O nome do currículo é obrigatório.", 400

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO curriculos (
                    usuario_id,
                    nome,
                    arquivo_url
                )
                VALUES (%s, %s, %s)
                """,
                (
                    session["usuario_id"],
                    nome,
                    arquivo_url
                )
            )

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao salvar currículo: {erro}", 500

        cursor.close()
        release_connection(conn)

        return redirect(
            url_for("curriculos.listar")
        )

    return render_template("curriculo_novo.html")


# ==============================
# DETALHES DO CURRÍCULO
# ==============================

@curriculos.route("/curriculos/<int:id>")
def detalhes(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            nome,
            arquivo_url,
            criado_em
        FROM curriculos
        WHERE id = %s
        AND usuario_id = %s
        """,
        (
            id,
            session["usuario_id"]
        )
    )

    curriculo = cursor.fetchone()

    cursor.close()
    release_connection(conn)

    if not curriculo:
        return "Currículo não encontrado.", 404

    return render_template(
        "curriculo_detalhes.html",
        curriculo=curriculo
    )


# ==============================
# EDITAR CURRÍCULO
# ==============================

@curriculos.route("/curriculos/<int:id>/editar", methods=["GET", "POST"])
def editar(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    # Buscar currículo do usuário logado
    cursor.execute(
        """
        SELECT
            id,
            nome,
            arquivo_url,
            criado_em
        FROM curriculos
        WHERE id = %s
        AND usuario_id = %s
        """,
        (
            id,
            session["usuario_id"]
        )
    )

    curriculo = cursor.fetchone()

    if not curriculo:

        cursor.close()
        release_connection(conn)

        return "Currículo não encontrado.", 404

    # Atualizar currículo
    if request.method == "POST":

        nome = request.form.get("nome")
        arquivo_url = request.form.get("arquivo_url")

        if not nome:

            cursor.close()
            release_connection(conn)

            return "O nome do currículo é obrigatório.", 400

        try:

            cursor.execute(
                """
                UPDATE curriculos
                SET
                    nome = %s,
                    arquivo_url = %s
                WHERE id = %s
                AND usuario_id = %s
                """,
                (
                    nome,
                    arquivo_url,
                    id,
                    session["usuario_id"]
                )
            )

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao atualizar currículo: {erro}", 500

        cursor.close()
        release_connection(conn)

        return redirect(
            url_for("curriculos.listar")
        )

    cursor.close()
    release_connection(conn)

    return render_template(
        "curriculo_editar.html",
        curriculo=curriculo
    )


# ==============================
# EXCLUIR CURRÍCULO
# ==============================

@curriculos.route("/curriculos/<int:id>/excluir", methods=["POST"])
def excluir(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM curriculos
            WHERE id = %s
            AND usuario_id = %s
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

        return f"Erro ao excluir currículo: {erro}", 500

    cursor.close()
    release_connection(conn)

    return redirect(
        url_for("curriculos.listar")
    )