from flask import Blueprint, render_template, session, redirect, url_for, request
from database.connection import get_connection, release_connection


candidaturas = Blueprint("candidaturas", __name__)


@candidaturas.route("/candidaturas")
def listar():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            c.id,
            c.cargo,
            e.nome AS empresa,
            c.status,
            c.modalidade,
            c.localizacao,
            c.salario,
            c.link_vaga,
            c.descricao,
            c.observacoes,
            c.data_candidatura
        FROM candidaturas c
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE c.usuario_id = %s
        ORDER BY c.criado_em DESC
        """,
        (session["usuario_id"],)
    )

    dados = cursor.fetchall()

    cursor.close()
    release_connection(conn)

    return render_template(
        "candidaturas.html",
        candidaturas=dados
    )


@candidaturas.route("/candidaturas/nova", methods=["GET", "POST"])
def nova():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        cargo = request.form["cargo"]
        empresa = request.form.get("empresa")
        status = request.form.get("status")
        modalidade = request.form.get("modalidade")
        localizacao = request.form.get("localizacao")
        salario = request.form.get("salario")
        link_vaga = request.form.get("link_vaga")
        descricao = request.form.get("descricao")
        observacoes = request.form.get("observacoes")

        conn = get_connection()
        cursor = conn.cursor()

        try:

            empresa_id = None

            if empresa:

                cursor.execute(
                    """
                    SELECT id
                    FROM empresas
                    WHERE nome = %s
                    """,
                    (empresa,)
                )

                empresa_existente = cursor.fetchone()

                if empresa_existente:
                    empresa_id = empresa_existente[0]

                else:

                    cursor.execute(
                        """
                        INSERT INTO empresas (nome)
                        VALUES (%s)
                        RETURNING id
                        """,
                        (empresa,)
                    )

                    empresa_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO candidaturas (
                    cargo,
                    empresa_id,
                    status,
                    modalidade,
                    localizacao,
                    salario,
                    link_vaga,
                    descricao,
                    observacoes,
                    usuario_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    cargo,
                    empresa_id,
                    status,
                    modalidade,
                    localizacao,
                    salario,
                    link_vaga,
                    descricao,
                    observacoes,
                    session["usuario_id"]
                )
            )

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao salvar candidatura: {erro}"

        cursor.close()
        release_connection(conn)

        return redirect(url_for("candidaturas.listar"))

    return render_template("candidatura_nova.html")


@candidaturas.route("/candidaturas/<int:id>")
def detalhes(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            c.id,
            c.cargo,
            e.nome AS empresa,
            e.site,
            c.status,
            c.modalidade,
            c.localizacao,
            c.salario,
            c.link_vaga,
            c.descricao,
            c.observacoes,
            c.data_candidatura,
            c.criado_em
        FROM candidaturas c
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE c.id = %s
        AND c.usuario_id = %s
        """,
        (id, session["usuario_id"])
    )

    candidatura = cursor.fetchone()

    cursor.close()
    release_connection(conn)

    if not candidatura:
        return "Candidatura não encontrada.", 404

    return render_template(
        "candidatura_detalhes.html",
        candidatura=candidatura
    )


@candidaturas.route("/candidaturas/<int:id>/editar", methods=["GET", "POST"])
def editar(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        cargo = request.form["cargo"]
        empresa = request.form.get("empresa")
        status = request.form.get("status")
        modalidade = request.form.get("modalidade")
        localizacao = request.form.get("localizacao")
        salario = request.form.get("salario")
        link_vaga = request.form.get("link_vaga")
        descricao = request.form.get("descricao")
        observacoes = request.form.get("observacoes")

        try:

            empresa_id = None

            if empresa:

                cursor.execute(
                    """
                    SELECT id
                    FROM empresas
                    WHERE nome = %s
                    """,
                    (empresa,)
                )

                empresa_existente = cursor.fetchone()

                if empresa_existente:
                    empresa_id = empresa_existente[0]

                else:

                    cursor.execute(
                        """
                        INSERT INTO empresas (nome)
                        VALUES (%s)
                        RETURNING id
                        """,
                        (empresa,)
                    )

                    empresa_id = cursor.fetchone()[0]

            cursor.execute(
                """
                UPDATE candidaturas
                SET
                    cargo = %s,
                    empresa_id = %s,
                    status = %s,
                    modalidade = %s,
                    localizacao = %s,
                    salario = %s,
                    link_vaga = %s,
                    descricao = %s,
                    observacoes = %s
                WHERE id = %s
                AND usuario_id = %s
                """,
                (
                    cargo,
                    empresa_id,
                    status,
                    modalidade,
                    localizacao,
                    salario,
                    link_vaga,
                    descricao,
                    observacoes,
                    id,
                    session["usuario_id"]
                )
            )

            conn.commit()

        except Exception as erro:

            conn.rollback()
            cursor.close()
            release_connection(conn)

            return f"Erro ao editar candidatura: {erro}"

        cursor.close()
        release_connection(conn)

        return redirect(
            url_for("candidaturas.listar")
        )

    cursor.execute(
        """
        SELECT
            c.id,
            c.cargo,
            e.nome AS empresa,
            c.status,
            c.modalidade,
            c.localizacao,
            c.salario,
            c.link_vaga,
            c.descricao,
            c.observacoes
        FROM candidaturas c
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE c.id = %s
        AND c.usuario_id = %s
        """,
        (id, session["usuario_id"])
    )

    candidatura = cursor.fetchone()

    cursor.close()
    release_connection(conn)

    if not candidatura:
        return "Candidatura não encontrada.", 404

    return render_template(
        "candidatura_editar.html",
        candidatura=candidatura
    )


@candidaturas.route("/candidaturas/<int:id>/excluir", methods=["POST"])
def excluir(id):

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM candidaturas
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

        return f"Erro ao excluir candidatura: {erro}"

    cursor.close()
    release_connection(conn)

    return redirect(
        url_for("candidaturas.listar")
    )