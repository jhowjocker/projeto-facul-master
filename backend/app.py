import os
import re
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client
from validate_docbr import CPF
from dotenv import load_dotenv
import webbrowser

load_dotenv()

app = Flask(__name__, static_folder=None)  # Desabilita o static_folder padrão
CORS(app)

supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

cpf_validator = CPF()

# ==================== Funções de validação ====================
def validar_cpf(numero: str) -> bool:
    """Remove máscara e valida CPF"""
    return cpf_validator.validate(numero)

def validar_email(email: str) -> bool:
    """Valida formato de e-mail com regex simples"""
    padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(padrao, email) is not None

def validar_cep(cep: str) -> bool:
    """Remove não dígitos e verifica se tem 8 números"""
    cep_limpo = ''.join(filter(str.isdigit, cep))
    return len(cep_limpo) == 8

def validar_uf(uf: str) -> bool:
    """Verifica se UF tem 2 letras maiúsculas"""
    return uf is not None and len(uf) == 2 and uf.isalpha() and uf.isupper()

def paciente_existe(email: str = None, cpf: str = None) -> bool:
    """Verifica se já existe paciente com o e-mail ou CPF fornecido"""
    query = supabase.table('pacientes').select('id')
    if email:
        query = query.eq('email', email)
    if cpf:
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        query = query.eq('cpf', cpf_limpo)
    resposta = query.execute()
    return len(resposta.data) > 0

# ==================== Rotas da API ====================
@app.route('/api/pacientes', methods=['POST'])
def cadastrar_paciente():
    dados = request.json

    # --- Campos obrigatórios ---
    campos_obrigatorios = ['nome', 'sobrenome', 'email', 'cpf']
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            return jsonify({'erro': f'Campo {campo} é obrigatório'}), 400

    # --- Validações de formato ---
    # Email
    if not validar_email(dados['email']):
        return jsonify({'erro': 'E-mail inválido'}), 400

    # CPF
    if not validar_cpf(dados['cpf']):
        return jsonify({'erro': 'CPF inválido'}), 400

    # CEP (se informado)
    cep = dados.get('cep')
    if cep and not validar_cep(cep):
        return jsonify({'erro': 'CEP inválido (deve conter 8 dígitos)'}), 400

    # Estado (UF) (se informado)
    estado = dados.get('estado')
    if estado and not validar_uf(estado):
        return jsonify({'erro': 'Estado deve ser uma UF com 2 letras maiúsculas (ex: SP)'}), 400

    # --- Verificação de duplicidade ---
    if paciente_existe(email=dados['email']):
        return jsonify({'erro': 'E-mail já cadastrado'}), 409

    if paciente_existe(cpf=dados['cpf']):
        return jsonify({'erro': 'CPF já cadastrado'}), 409

    # --- Preparação dos dados ---
    cpf_limpo = ''.join(filter(str.isdigit, dados['cpf']))
    cep_limpo = ''.join(filter(str.isdigit, cep)) if cep else None

    novo_paciente = {
        'nome': dados['nome'].strip(),
        'sobrenome': dados['sobrenome'].strip(),
        'email': dados['email'].strip().lower(),
        'cpf': cpf_limpo,
        'cep': cep_limpo,
        'numero': dados.get('numero', '').strip() or None,
        'logradouro': dados.get('logradouro', '').strip() or None,
        'bairro': dados.get('bairro', '').strip() or None,
        'cidade': dados.get('cidade', '').strip() or None,
        'estado': dados.get('estado', '').strip().upper() or None
    }

    try:
        resposta = supabase.table('pacientes').insert(novo_paciente).execute()
        if resposta.data:
            paciente_id = resposta.data[0]['id']
            return jsonify({
                'mensagem': 'Cadastro realizado com sucesso',
                'id': paciente_id
            }), 201
        else:
            return jsonify({'erro': 'Erro ao inserir no banco'}), 500
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/agendamentos', methods=['POST'])
def agendar_consulta():
    dados = request.json
    paciente_id = dados.get('paciente_id')
    data_consulta = dados.get('data_consulta')  # formato YYYY-MM-DD

    if not paciente_id or not data_consulta:
        return jsonify({'erro': 'paciente_id e data_consulta são obrigatórios'}), 400

    # --- Validar formato da data ---
    try:
        data_obj = datetime.strptime(data_consulta, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'erro': 'Data inválida. Use o formato YYYY-MM-DD'}), 400

    # --- Validar se a data é futura (não permitir agendamento para datas passadas) ---
    if data_obj < datetime.now().date():
        return jsonify({'erro': 'Não é possível agendar para uma data passada'}), 400

    # --- Verificar se o paciente existe ---
    paciente = supabase.table('pacientes').select('id').eq('id', paciente_id).execute()
    if not paciente.data:
        return jsonify({'erro': 'Paciente não encontrado'}), 404

    # --- Verificar se já existe agendamento para este paciente na mesma data ---
    agendamento_existente = supabase.table('agendamentos') \
        .select('id') \
        .eq('id_paciente', paciente_id) \
        .eq('data_consulta', data_consulta) \
        .execute()
    if agendamento_existente.data:
        return jsonify({'erro': 'Paciente já possui agendamento nesta data'}), 409

    # --- Inserir agendamento ---
    novo_agendamento = {
        'id_paciente': paciente_id,
        'data_consulta': data_consulta
    }
    try:
        resposta = supabase.table('agendamentos').insert(novo_agendamento).execute()
        if resposta.data:
            return jsonify({'mensagem': 'Consulta agendada com sucesso'}), 201
        else:
            return jsonify({'erro': 'Erro ao agendar'}), 500
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/prontuario/<int:paciente_id>', methods=['GET', 'PUT'])
def gerenciar_prontuario(paciente_id):
    # Controle de acesso simulado
    cargo = request.headers.get('X-User-Role')
    if cargo != 'medico':
        return jsonify({'erro': 'Acesso negado. Apenas médicos podem acessar prontuários.'}), 403

    paciente = supabase.table('pacientes').select('*').eq('id', paciente_id).execute()
    if not paciente.data:
        return jsonify({'erro': 'Paciente não encontrado'}), 404

    paciente_data = paciente.data[0]

    if request.method == 'GET':
        return jsonify({
            'nome': paciente_data['nome'],
            'prontuario': paciente_data.get('numero_prontuario'),
            'doencas_cronicas': paciente_data.get('doencas_cronicas'),
            'evolucao_medica': paciente_data.get('evolucao_medica')
        })

    elif request.method == 'PUT':
        dados = request.json
        update_data = {}
        if 'doencas_cronicas' in dados:
            update_data['doencas_cronicas'] = dados['doencas_cronicas']
        if 'evolucao_medica' in dados:
            update_data['evolucao_medica'] = dados['evolucao_medica']

        if not update_data:
            return jsonify({'erro': 'Nenhum campo para atualizar'}), 400

        try:
            resposta = supabase.table('pacientes') \
                .update(update_data) \
                .eq('id', paciente_id) \
                .execute()
            if resposta.data:
                return jsonify({'mensagem': 'Prontuário atualizado com sucesso'})
            else:
                return jsonify({'erro': 'Erro ao atualizar'}), 500
        except Exception as e:
            return jsonify({'erro': str(e)}), 500


@app.route('/api/disponibilidade', methods=['GET'])
def verificar_disponibilidade():
    data = request.args.get('data')
    if not data:
        return jsonify({'erro': 'Parâmetro data é obrigatório'}), 400

    # Validar formato da data
    try:
        datetime.strptime(data, '%Y-%m-%d')
    except ValueError:
        return jsonify({'erro': 'Data inválida. Use o formato YYYY-MM-DD'}), 400

    agendamentos = supabase.table('agendamentos') \
        .select('id', count='exact') \
        .eq('data_consulta', data) \
        .execute()
    total = agendamentos.count if hasattr(agendamentos, 'count') else len(agendamentos.data)

    disponivel = total < 20  # limite de 20 consultas por dia
    return jsonify({
        'data': data,
        'agendamentos': total,
        'disponivel': disponivel
    })

# ==================== Rotas para servir arquivos estáticos e HTML ====================

@app.route('/')
def serve_index():
    """Serve a página inicial index.html"""
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/<path:filename>')
def serve_static_or_html(filename):
    """
    Serve arquivos estáticos (css, js, img, etc.) ou páginas HTML.
    Evita conflito com rotas da API.
    """
    # Se começar com 'api/', não é arquivo estático, retorna 404 para não mascarar rotas da API
    if filename.startswith('api/'):
        return jsonify({'erro': 'Rota não encontrada'}), 404

    # Caminho completo para o arquivo solicitado
    filepath = os.path.join(os.getcwd(), filename)

    # Se for um diretório, tenta servir um index.html dentro dele (opcional)
    if os.path.isdir(filepath):
        index_inside = os.path.join(filepath, 'index.html')
        if os.path.isfile(index_inside):
            return send_from_directory(filepath, 'index.html')
        # Se não houver index, retorna 404
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

    # Se for um arquivo, tenta servir
    if os.path.isfile(filepath):
        # Extrai o diretório e o nome do arquivo
        directory = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        return send_from_directory(directory, basename)

    # Se não encontrou, retorna 404
    return jsonify({'erro': 'Arquivo não encontrado'}), 404

# ==================== Função para abrir o navegador ====================
def abrir_navegador():
    time.sleep(1.5)  # Aguarda o servidor iniciar
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Inicia a thread que abrirá o navegador
    threading.Thread(target=abrir_navegador).start()
    # Inicia o servidor Flask
    app.run(debug=True, use_reloader=False)