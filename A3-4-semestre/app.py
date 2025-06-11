from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from mysql.connector import Error
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'laurinha'  # Chave muito secreta

# conecta com o banco de dados
def criar_conexao():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='cadastroA3',
            user='root',
            password=''
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
    return None

# página inicial
@app.route('/')
def index():
    return render_template('index.html')

# cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()

                # Verifica se o email já existe
                email_cursor = conn.cursor()
                email_cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                usuario_existente_email = email_cursor.fetchone()
                email_cursor.close()
                if usuario_existente_email:
                    # Mostra a mensagem de erro no mensagem.html
                    return render_template(
                        'mensagemcadastro.html',
                        titulo='Erro no Cadastro',
                        mensagem='Este e-mail já está em uso. Por favor, utilize outro.',
                        url_link=url_for('cadastro') 
                    )
                # Verifica se o nome já existe
                nome_cursor = conn.cursor()
                nome_cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (nome,))
                usuario_existente_nome = nome_cursor.fetchone()
                nome_cursor.close()
                if usuario_existente_nome:
                    #Mostra a mensagem de erro no mensagem.html
                    return render_template(
                        'mensagemcadastro.html',
                        titulo='Erro no Cadastro',
                        mensagem='Este nome de usuário já está em uso. Por favor, escolha outro.',
                        url_link=url_for('cadastro')
                    )
                # Registra o usuário 
                query = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
                valores = (nome, email, senha)
                cursor.execute(query, valores)
                conn.commit()
                
                session['usuario'] = nome
                return redirect(url_for('jogo'))

            except Error as e:
                return f"Erro ao inserir usuário: {e}"
            finally:
                if 'cursor' in locals() and cursor is not None:
                    cursor.close()
                if conn is not None:
                    conn.close()
        else:
            return "Erro na conexão com o banco de dados."

    return render_template('cadastro.html')

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True, buffered=True)
                query = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
                cursor.execute(query, (email, senha))
                usuario = cursor.fetchone()

                if usuario:
                    session['usuario'] = usuario['nome']
                    return redirect(url_for('jogo'))
                else:
                    return render_template(
                        'mensagem.html',
                        titulo='Erro de Login',
                        mensagem='Email ou senha inválidos.',
                        url_link=url_for('login')
                    )
            except Error as e:
                return f"Erro no login: {e}"
            finally:
                if 'cursor' in locals() and cursor is not None:
                    cursor.close()
                if conn is not None:
                    conn.close()

    return render_template('login.html')

# página do jogo
@app.route('/jogo')
def jogo():
    print(f"Conteúdo da sessão ao carregar jogo.html: {session}") # Esta linha é a chave!
    return render_template('jogo.html', session=session)

# Esqueci a senha
@app.route('/senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form['email']
        nova_senha = request.form['nova_senha']

        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                query = "UPDATE usuarios SET senha = %s WHERE email = %s"
                cursor.execute(query, (nova_senha, email))
                conn.commit()

                if cursor.rowcount == 0:
                    return render_template(
                        'mensagemsenha.html',
                        titulo='Erro',
                        mensagem='Email não encontrado.',
                        url_link=url_for('esqueci_senha')
                    )
            except Error as e:
                return f"Erro ao atualizar a senha: {e}"
            finally:
                if 'cursor' in locals() and cursor is not None:
                    cursor.close()
                if conn is not None:
                    conn.close()
    return render_template('senha.html')

@app.route('/deslogar')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/salvar_pontuacao', methods=['POST'])
def salvar_pontuacao():
    if 'usuario' not in session:
        return jsonify({'erro': 'Usuário não logado'}), 401

    dados = request.get_json()
    pontos = dados.get('pontos', 0)
    nome_usuario = session['usuario']

    conn = criar_conexao()
    if conn:
        try:
            cursor = conn.cursor()

            # Tenta atualizar a pontuação do usuário
            cursor.execute("UPDATE ranking SET pontos = %s WHERE nome = %s", (pontos, nome_usuario))

            # Se nenhuma linha foi afetada, insere novo registro
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO ranking (nome, pontos) VALUES (%s, %s)", (nome_usuario, pontos))

            conn.commit()
        except Exception as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    return jsonify({'sucesso': True}), 200

    
@app.route('/ranking')
def ranking():

    conn = criar_conexao()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            #ordena por quantidade de pontos
            cursor.execute("SELECT nome, pontos FROM ranking ORDER BY pontos DESC")
            resultados = cursor.fetchall()
        except Exception as e:
            resultados = []
        finally:
            cursor.close()
            conn.close()
    else:
        resultados = []

    return render_template('ranking.html', ranking=resultados)

if __name__ == '__main__':
    app.run(debug=True) 