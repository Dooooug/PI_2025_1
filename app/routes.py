from flask_cors import CORS  # Importação do Flask-CORS
from flask import request, jsonify
from . import db
from .models import User
from flask import current_app as app

# Adicionar o CORS ao app
CORS(app)  # Habilita o CORS para todas as rotas

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    app.logger.info(f"Dados recebidos: {data}")
    email = data.get('email')
    senha = data.get('senha')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(senha):  # Verifica o email e a senha
        return jsonify({'message': 'Credenciais inválidas'}), 401

    return jsonify({'message': 'Login bem-sucedido'}), 200


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validação e registro de novo usuário
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    # Adicionar verificações de validação aqui...
    if not nome or len(nome) > 150:
        return jsonify({'message': 'O nome deve ter no máximo 500 caracteres'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Usuário já existe'}), 409

    new_user = User(nome=nome, email=email)
    new_user.set_password(senha)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuário registrado com sucesso'}), 201

@app.route('/users', methods=['GET'])
def get_users():
    try:
        # Busca todos os usuários no banco de dados
        users = User.query.all()

        # Se nenhum usuário for encontrado, retorna mensagem apropriada
        if not users:
            return jsonify({'error': 'Nenhum usuário encontrado.'}), 404

        # Formata os dados retornados como uma lista de dicionários
        result = [{'Id': user.id, 'Nome': user.nome, 'Email': user.email} for user in users]

        # Retorna os dados em formato JSON com status 200
        return jsonify(result), 200

    except Exception as e:
        # Em caso de erro no servidor, retorna mensagem apropriada e status 500
        print(f"Erro no servidor: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()

    # Validação de entrada
    if not data or 'email' not in data or 'senha' not in data:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    # Busca pelo usuário
    user = User.query.get_or_404(user_id)

    # Atualização dos campos
    user.email = data['email']  # Altera para "email"
    user.set_password(data['senha'])  # Altera para "senha"

    # Commit para salvar alterações
    db.session.commit()
    return jsonify({'message': 'Usuário atualizado com sucesso'}), 200

