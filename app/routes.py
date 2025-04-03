from flask_cors import CORS  # Importação do Flask-CORS
from flask import request, jsonify
from . import db
from .models import User, Product
from flask import current_app as app
from flask import session
from werkzeug.security import generate_password_hash

app.secret_key = 204314

# Adicionar o CORS ao app
CORS(app)  # Habilita o CORS para todas as rotas

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    app.logger.info(f"Dados recebidos: {data}")
    email = data.get('email')
    senha = data.get('senha')

    # Busca o usuário no banco de dados pelo email
    user = User.query.filter_by(email=email).first()

    # Verifica se o usuário existe e se a senha está correta
    if not user or not user.check_password(senha):  # check_password é uma função que valida a senha
        return jsonify({'message': 'Credenciais inválidas'}), 401

    # Retorna o ID do usuário junto com a mensagem de sucesso
    return jsonify({'message': 'Login bem-sucedido', 'id': user.id}), 200


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

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        # Busca o usuário pelo ID
        user = User.query.get(user_id)

        # Verifica se o usuário existe
        if not user:
            return jsonify({'error': 'Usuário não encontrado.'}), 404

        # Retorna os dados do usuário
        return jsonify({'Id': user.id, 'Nome': user.nome, 'Email': user.email}), 200

    except Exception as e:
        print(f"Erro no servidor: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500
    
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        if user_id <= 0:
            return jsonify({'error': 'ID do usuário inválido'}), 400

        data = request.get_json()
        print(f"Dados recebidos para atualização do usuário {user_id}: {data}")

        if not data:
            return jsonify({'error': 'Dados de entrada são obrigatórios'}), 400
        if 'email' not in data:
            return jsonify({'error': 'O campo email é obrigatório'}), 400
        if 'senha' not in data:
            return jsonify({'error': 'O campo senha é obrigatório'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': f'Usuário com ID {user_id} não encontrado'}), 404

        print(f"Usuário encontrado: ID={user.id}, Email={user.email}")

        user.email = data['email']
        user.senha = generate_password_hash(data['senha'])  # Hash da senha

        try:
            db.session.commit()
            print(f"Alterações salvas com sucesso para o usuário ID={user.id}")

            return jsonify({
                'message': 'Usuário atualizado com sucesso',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nome': user.nome if hasattr(user, 'nome') else 'Nome não definido',
                }
            }), 200  # Código de status 200 OK
        except Exception as commit_error:
            print(f"Erro ao salvar alterações no banco: {commit_error}")
            db.session.rollback()
            return jsonify({'error': 'Erro ao salvar no banco de dados'}), 500

    except Exception as e:
        print(f"Erro no servidor: {e}")
        return jsonify({'error': 'Erro interno no servidor. Tente novamente.'}), 500


@app.route('/current_user', methods=['GET'])
def get_current_user():
    try:
        # Exemplo: obtendo user_id da sessão
        user_id = session.get('user_id')  # Certifique-se de que `session` esteja configurada

        # Validação: Certifica-se de que o usuário está autenticado
        if not user_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401

        # Busca o usuário no banco de dados pelo ID
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': f'Usuário com ID {user_id} não encontrado'}), 404

        # Retorna as informações do usuário autenticado
        return jsonify({
            'id': user.id,
            'email': user.email,
            'nome': user.nome if hasattr(user, 'nome') else 'Nome não definido'
        }), 200
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500
    
@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    
    # Verificação dos campos obrigatórios
    if not data or 'codigo' not in data or 'nome_do_produto' not in data:
        return jsonify({"error": "Campos obrigatórios faltando"}), 400

    new_product = Product(
        codigo=data.get('codigo'),
        qtade_maxima_armazenada=data.get('qtadeMaximaArmazenada'),
        nome_do_produto=data.get('nomeDoProduto'),
        fornecedor=data.get('fornecedor'),
        estado_fisico=data.get('estadoFisico'),
        local_de_armazenamento=data.get('localDeArmazenamento'),
        substancia1=data.get('substancia1'),
        nCas1=data.get('nCas1'),
        concentracao1=data.get('concentracao1'),
        substancia2=data.get('substancia2'),
        nCas2=data.get('nCas2'),
        concentracao2=data.get('concentracao2'),
        substancia3=data.get('substancia3'),
        nCas3=data.get('nCas3'),
        concentracao3=data.get('concentracao3'),
        perigos_fisicos=','.join(data.get('perigosFisicos', [])),
        perigos_saude=','.join(data.get('perigosSaude', [])),
        perigos_meio_ambiente=','.join(data.get('perigosMeioAmbiente', [])),
        palavra_de_perigo=data.get('palavraDePerigo'),
        categoria=data.get('categoria')
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Produto adicionado com sucesso!", "product": {
        "id": new_product.id,
        "codigo": new_product.codigo,
        "qtade_maxima_armazenada": new_product.qtade_maxima_armazenada,
        "nome_do_produto": new_product.nome_do_produto,
        "fornecedor": new_product.fornecedor,
        "estado_fisico": new_product.estado_fisico,
        "local_de_armazenamento": new_product.local_de_armazenamento,
        "substancia1": new_product.substancia1,
        "nCas1": new_product.nCas1,
        "concentracao1": new_product.concentracao1,
        "substancia2": new_product.substancia2,
        "nCas2": new_product.nCas2,
        "concentracao2": new_product.concentracao2,
        "substancia3": new_product.substancia3,
        "nCas3": new_product.nCas3,
        "concentracao3": new_product.concentracao3,
        "perigos_fisicos": new_product.perigos_fisicos.split(','),
        "perigos_saude": new_product.perigos_saude.split(','),
        "perigos_meio_ambiente": new_product.perigos_meio_ambiente.split(','),
        "palavra_de_perigo": new_product.palavra_de_perigo,
        "categoria": new_product.categoria
    }}), 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_list = [{
        "id": p.id,
        "codigo": p.codigo,
        "qtade_maxima_armazenada": p.qtade_maxima_armazenada,
        "nome_do_produto": p.nome_do_produto,
        "fornecedor": p.fornecedor,
        "estado_fisico": p.estado_fisico,
        "local_de_armazenamento": p.local_de_armazenamento,
        "substancia1": p.substancia1,
        "nCas1": p.nCas1,
        "concentracao1": p.concentracao1,
        "substancia2": p.substancia2,
        "nCas2": p.nCas2,
        "concentracao2": p.concentracao2,
        "substancia3": p.substancia3,
        "nCas3": p.nCas3,
        "concentracao3": p.concentracao3,
        "perigos_fisicos": p.perigos_fisicos.split(','),
        "perigos_saude": p.perigos_saude.split(','),
        "perigos_meio_ambiente": p.perigos_meio_ambiente.split(','),
        "palavra_de_perigo": p.palavra_de_perigo,
        "categoria": p.categoria
    } for p in products]

    return jsonify(products_list), 200
    
if __name__ == '__main__':
    app.run(debug=True)
    





