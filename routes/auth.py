from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.connection import get_connection


auth = Blueprint("auth", __name__)


# =====================================================
# CADASTRO
# =====================================================

@auth.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        senha_hash = generate_password_hash(senha)

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, senha)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (nome, email, senha_hash)
            )

            usuario_id = cursor.fetchone()[0]

            conn.commit()

        except Exception:

            conn.rollback()
            cursor.close()
            conn.close()

            return "Este e-mail já está cadastrado."

        cursor.close()
        conn.close()

        session["usuario_id"] = usuario_id
        session["usuario_nome"] = nome

        # Depois do cadastro → Visão geral
        return redirect(url_for("pagina_inicio"))

    return render_template("cadastro.html")


# =====================================================
# LOGIN
# =====================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    erro = None

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, nome, senha
            FROM usuarios
            WHERE email = %s
            """,
            (email,)
        )

        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if usuario and check_password_hash(usuario[2], senha):

            session["usuario_id"] = usuario[0]
            session["usuario_nome"] = usuario[1]

            # Depois do login → Visão geral
            return redirect(url_for("pagina_inicio"))

        # Login inválido → permanece na tela de login
        erro = "E-mail ou senha incorretos."

    return render_template(
        "login.html",
        erro=erro
    )


# =====================================================
# LOGOUT
# =====================================================

@auth.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))