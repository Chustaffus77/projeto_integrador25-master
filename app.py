from flask import Flask, request, jsonify, render_template
import mysql.connector
import threading
import webbrowser
app = Flask(__name__)
 
# Configuração do banco de dados
db_config = {
    'host': 'localhost',  # IP local do servidor MySQL
    'user': 'root',       # Usuário do MySQL
    'password': 'alunolab', # Senha do MySQL
    'database': 'pi25', # Nome do banco de dados
    'port': 3303          # Porta padrão do MySQL
}
try:
    conn = mysql.connector.connect(**db_config)
    print("Conexão com o banco de dados foi bem-sucedida!")
except mysql.connector.Error as erro:
    print(f"Erro na conexão: {erro}")
 
# Rota API para a página principal
@app.route('/')
def index():
    return render_template('index.html')
 
# Rota API para SALVAR registro
@app.route('/salvar', methods=['POST'])
def salvar():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    cpf = data.get('cpf')
    cnpj = data.get('cnpj')
    senha = data.get('senha')




    if not nome or not email or not cpf or not cnpj or not senha :
        return jsonify({'message': 'Dados incompletos!'}), 400
 
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nome, email, cpf, cnpj, senha) VALUES (%s, %s, %s, %s, %s)", (nome, email, cpf, cnpj, senha ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registro salvo com sucesso!'})
 
 
# Rota API para LOCALIZAR registro pelo nome
@app.route('/localizar', methods=['GET'])
def localizar():
    nome = request.args.get('nome', '')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cadastros WHERE nome = %s",(nome,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(data)
 
# Rota API para totalizar os registros
@app.route('/total_registros', methods=['GET'])
def total_registros():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cadastros")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({'total_registros': total}), 200
   
 
# ROTA API para navegar retornando pelo indice
@app.route('/navegar/<int:index>', methods=['GET'])
def navegar(index):
    direcao = request.args.get('direcao', 'proximo')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cadastros LIMIT 1 OFFSET %s", (index,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(data)
 
# Rota API para a EXCLUSÃO do registro
@app.route('/excluir', methods=['POST'])
def excluir():
    nome = request.args.get('nome','')
    conn = mysql.connector.connect(**db_config)
    cursor =  conn.cursor()
    cursor.execute("DELETE FROM cadastros WHERE nome = %s", (nome,))
    conn.commit()
    if cursor.rowcount > 0:
        return jsonify({'message': f'Registro "{nome}" excluido com sucesso!'}),200
    else:
        return jsonify({'message': 'registro não encontrado.'}),404
 
# ROTA API para permitir ALTERAÇÃO de registros
@app.route('/atualizar/<int:codigo>', methods = ['POST'])
def atualizar(codigo):
    try:
        data = request.get_json()
        nome = data.get('nome')
        idade = data.get('idade')
        if not nome or not idade:
            return jsonify({'message': 'Nome e idade são obrigatórios!'}),400
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
 
        # atualizar daddos
        cursor.execute("UPDATE cadastros SET idade = %s, nome = %s WHERE id = %s", (idade, nome, codigo))
        conn.commit()
       
        if cursor.rowcount > 0:
            return jsonify({'message': 'Registro ATUALIZADO com SUCESSO!'}), 200
        else:
            return jsonify({'message':'Registro NÃO encontrado!'}), 400
    except Exception as erro:
        return jsonify({'message':f'Erro ao atualizar: {str(erro)}'}),500
   
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
 
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')
 
if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True, use_reloader=False)