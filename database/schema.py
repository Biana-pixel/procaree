from database.connection import get_connection, release_connection


def criar_tabelas():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # =====================================================
        # USUÁRIOS
        # =====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (

                id SERIAL PRIMARY KEY,

                nome VARCHAR(100) NOT NULL,

                email VARCHAR(150) UNIQUE NOT NULL,

                senha VARCHAR(255) NOT NULL,

                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            );
        """)


        # =====================================================
        # EMPRESAS
        # =====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresas (

                id SERIAL PRIMARY KEY,

                nome VARCHAR(150) NOT NULL,

                site VARCHAR(255),

                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            );
        """)


        # Adiciona usuario_id caso a tabela empresas
        # já exista sem essa coluna.

        cursor.execute("""
            ALTER TABLE empresas
            ADD COLUMN IF NOT EXISTS usuario_id
            INTEGER REFERENCES usuarios(id) ON DELETE CASCADE;
        """)


        # =====================================================
        # CANDIDATURAS
        # =====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidaturas (

                id SERIAL PRIMARY KEY,

                cargo VARCHAR(150) NOT NULL,

                empresa_id INTEGER
                    REFERENCES empresas(id)
                    ON DELETE SET NULL,

                status VARCHAR(30)
                    NOT NULL
                    DEFAULT 'interessado',

                modalidade VARCHAR(30),

                localizacao VARCHAR(150),

                link_vaga VARCHAR(500),

                salario VARCHAR(100),

                descricao TEXT,

                observacoes TEXT,

                data_candidatura DATE,

                criado_em TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                usuario_id INTEGER NOT NULL
                    REFERENCES usuarios(id)
                    ON DELETE CASCADE

            );
        """)


        # =====================================================
        # ENTREVISTAS
        # =====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entrevistas (

                id SERIAL PRIMARY KEY,

                candidatura_id INTEGER NOT NULL
                    REFERENCES candidaturas(id)
                    ON DELETE CASCADE,

                data_hora TIMESTAMP NOT NULL,

                tipo VARCHAR(50),

                observacoes TEXT,

                criado_em TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP

            );
        """)


        # =====================================================
        # CURRÍCULOS
        # =====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS curriculos (

                id SERIAL PRIMARY KEY,

                usuario_id INTEGER NOT NULL
                    REFERENCES usuarios(id)
                    ON DELETE CASCADE,

                nome VARCHAR(150) NOT NULL,

                arquivo_url VARCHAR(500),

                criado_em TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP

            );
        """)


        # =====================================================
        # COMPETÊNCIAS
        # =====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competencias (

                id SERIAL PRIMARY KEY,

                usuario_id INTEGER NOT NULL
                    REFERENCES usuarios(id)
                    ON DELETE CASCADE,

                nome VARCHAR(150) NOT NULL,

                nivel VARCHAR(50) NOT NULL,

                criado_em TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP

            );
        """)


        # =====================================================
        # METAS
        # =====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metas (

                id SERIAL PRIMARY KEY,

                usuario_id INTEGER NOT NULL
                    REFERENCES usuarios(id)
                    ON DELETE CASCADE,

                titulo VARCHAR(150) NOT NULL,

                descricao TEXT,

                prazo DATE,

                status VARCHAR(30)
                    NOT NULL
                    DEFAULT 'pendente',

                criado_em TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP

            );
        """)


        # =====================================================
        # ÍNDICES DE DESEMPENHO
        # =====================================================

        # Candidaturas por usuário
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_candidaturas_usuario
            ON candidaturas(usuario_id);
        """)


        # Candidaturas recentes por usuário
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_candidaturas_usuario_criado
            ON candidaturas(usuario_id, criado_em DESC);
        """)


        # Entrevistas ligadas às candidaturas
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entrevistas_candidatura
            ON entrevistas(candidatura_id);
        """)


        # Entrevistas futuras
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entrevistas_data
            ON entrevistas(data_hora);
        """)


        # Currículos por usuário
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_curriculos_usuario
            ON curriculos(usuario_id);
        """)


        # Competências por usuário
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_competencias_usuario
            ON competencias(usuario_id);
        """)


        # Metas por usuário
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metas_usuario
            ON metas(usuario_id);
        """)


        # Empresas por usuário
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_empresas_usuario
            ON empresas(usuario_id);
        """)


        # =====================================================
        # SALVAR ALTERAÇÕES
        # =====================================================

        conn.commit()

        print("TABELAS DO PROCAREER CRIADAS COM SUCESSO!")


    except Exception:

        conn.rollback()

        raise


    finally:

        cursor.close()

        release_connection(conn)


if __name__ == "__main__":

    criar_tabelas()