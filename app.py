from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS

from config import Config
from database.schema import criar_tabelas
from database.connection import get_connection

from routes.auth import auth
from routes.candidaturas import candidaturas
from routes.entrevistas import entrevistas
from routes.curriculos import curriculos
from routes.dashboard import dashboard
from routes.empresas import empresas
from routes.analise import analise
from routes.competencias import competencias
from routes.metas import metas


app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

app.register_blueprint(auth)
app.register_blueprint(candidaturas)
app.register_blueprint(entrevistas)
app.register_blueprint(curriculos)
app.register_blueprint(dashboard)
app.register_blueprint(empresas)
app.register_blueprint(analise)
app.register_blueprint(competencias)
app.register_blueprint(metas)


# =====================================================
# CRIAÇÃO DAS TABELAS
# =====================================================

criar_tabelas()


# =====================================================
# PÁGINA INICIAL PÚBLICA
# =====================================================

@app.route("/")
def inicio():

    return redirect(url_for("auth.cadastro"))


# =====================================================
# VISÃO GERAL
# =====================================================

@app.route("/inicio")
def pagina_inicio():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario_id = session["usuario_id"]

    conn = get_connection()
    cursor = conn.cursor()


    # =================================================
    # CANDIDATURAS
    # =================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidaturas
        WHERE usuario_id = %s
    """, (usuario_id,))

    total_candidaturas = cursor.fetchone()[0]


    # =================================================
    # ENTREVISTAS
    # =================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM entrevistas i
        INNER JOIN candidaturas c
            ON i.candidatura_id = c.id
        WHERE c.usuario_id = %s
    """, (usuario_id,))

    total_entrevistas = cursor.fetchone()[0]


    # =================================================
    # COMPETÊNCIAS
    # =================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM competencias
        WHERE usuario_id = %s
    """, (usuario_id,))

    total_competencias = cursor.fetchone()[0]


    # =================================================
    # CURRÍCULOS
    # =================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM curriculos
        WHERE usuario_id = %s
    """, (usuario_id,))

    total_curriculos = cursor.fetchone()[0]


    # =================================================
    # METAS
    # =================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM metas
        WHERE usuario_id = %s
    """, (usuario_id,))

    total_metas = cursor.fetchone()[0]


    # =================================================
    # EVOLUÇÃO
    # =================================================

    evolucao = 0

    if total_curriculos > 0:
        evolucao += 20

    if total_competencias > 0:
        evolucao += 20

    if total_candidaturas > 0:
        evolucao += 20

    if total_entrevistas > 0:
        evolucao += 20

    if total_metas > 0:
        evolucao += 20


    # =================================================
    # PROCESSOS RECENTES
    # =================================================

    cursor.execute("""
        SELECT
            COALESCE(e.nome, 'Empresa não informada') AS empresa,
            c.cargo,
            c.status
        FROM candidaturas c
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE c.usuario_id = %s
        ORDER BY c.criado_em DESC
        LIMIT 3
    """, (usuario_id,))

    processos_recentes = cursor.fetchall()


    # =================================================
    # PRÓXIMOS COMPROMISSOS
    # =================================================

    cursor.execute("""
        SELECT
            i.data_hora,
            i.tipo,
            c.cargo,
            COALESCE(e.nome, 'Empresa não informada') AS empresa
        FROM entrevistas i
        INNER JOIN candidaturas c
            ON i.candidatura_id = c.id
        LEFT JOIN empresas e
            ON c.empresa_id = e.id
        WHERE c.usuario_id = %s
          AND i.data_hora >= CURRENT_TIMESTAMP
        ORDER BY i.data_hora ASC
        LIMIT 3
    """, (usuario_id,))

    proximos_compromissos = cursor.fetchall()


    cursor.close()
    conn.close()


    return render_template(
        "inicio.html",
        total_candidaturas=total_candidaturas,
        total_entrevistas=total_entrevistas,
        total_competencias=total_competencias,
        total_curriculos=total_curriculos,
        total_metas=total_metas,
        processos_recentes=processos_recentes,
        proximos_compromissos=proximos_compromissos,
        evolucao=evolucao
    )


if __name__ == "__main__":

    criar_tabelas()

    app.run(debug=True)