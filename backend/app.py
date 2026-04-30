import os
import re
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, session  
from flask_cors import CORS
from supabase import create_client, Client
from validate_docbr import CPF
from dotenv import load_dotenv
import bcrypt                                  
import smtplib                                  
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText          
from email.mime.base import MIMEBase          
from email import encoders 
import webbrowser

load_dotenv()

# Define o diretório base do projeto (um nível acima da pasta /backend)
# Isso garante que o Flask encontre os arquivos estáticos independente de onde o script é iniciado.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERRO: SUPABASE_URL ou SUPABASE_KEY não encontradas no arquivo .env")
    # Não encerra o app aqui para permitir que o Flask suba e mostre erros nas rotas

app = Flask(__name__, static_folder=None)  
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-123')  
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}}) # Temporariamente mais permissivo para debug

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,   # Como é localhost (HTTP), não usamos HTTPS
    SESSION_COOKIE_HTTPONLY=True
)

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("AVISO: Cliente Supabase não inicializado.")

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
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

# ==================== Novas rotas para área médica ====================

@app.route('/api/medicos/login', methods=['POST'])
def medico_login():
    """Login do médico - valida usuário e senha"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'erro': 'Usuário e senha são obrigatórios'}), 400

    # Buscar médico no Supabase
    response = supabase.table('medicos').select('*').eq('username', username).execute()
    if not response.data:
        return jsonify({'erro': 'Usuário não encontrado'}), 401

    medico = response.data[0]
    password_hash = medico['password_hash'].encode('utf-8')

    if bcrypt.checkpw(password.encode('utf-8'), password_hash):
        session['medico_logado'] = username
        print("Sessão definida para:", session['medico_logado'])   # <-- adicione
        return jsonify({'success': True, 'message': 'Login realizado com sucesso'})
    else:
        return jsonify({'erro': 'Senha incorreta'}), 401


@app.route('/api/medicos/logout', methods=['POST'])
def medico_logout():
    """Logout do médico"""
    session.pop('medico_logado', None)
    return jsonify({'success': True})


@app.route('/api/pacientes/emails', methods=['GET'])
def listar_emails_pacientes():
    """Retorna lista de e-mails dos pacientes (protegido)"""
    if not session.get('medico_logado'):
        return jsonify({'erro': 'Não autorizado'}), 401

    response = supabase.table('pacientes').select('email').execute()
    emails = [row['email'] for row in response.data]
    return jsonify(emails)


@app.route('/api/enviar-exame', methods=['POST'])
def enviar_exame():
    """Envia arquivo por e-mail (protegido)"""
    if not session.get('medico_logado'):
        return jsonify({'erro': 'Não autorizado'}), 401

    # Obtém dados do formulário multipart
    email_paciente = request.form.get('email')
    arquivo = request.files.get('arquivo')

    if not email_paciente or not arquivo:
        return jsonify({'erro': 'E-mail e arquivo são obrigatórios'}), 400

    # Valida extensão
    if not arquivo.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({'erro': 'Formato de arquivo inválido. Use PNG ou JPG.'}), 400

    try:
        # Configuração do e-mail
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = email_paciente
        msg['Subject'] = 'Resultado do seu exame'

        corpo = "Prezado paciente, segue em anexo o resultado do seu exame."
        msg.attach(MIMEText(corpo, 'plain'))

        # Anexa o arquivo
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(arquivo.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{arquivo.filename}"')
        msg.attach(part)

        # Envia via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return jsonify({'success': True, 'message': 'E-mail enviado com sucesso'})
    except Exception as e:
        return jsonify({'erro': f'Falha ao enviar e-mail: {str(e)}'}), 500

# ==================== Rotas para servir arquivos estáticos e HTML ====================

@app.route('/')
def serve_index():
    """Serve a página inicial index.html"""
    if os.path.exists(os.path.join(BASE_DIR, 'index.html')):
        return send_from_directory(BASE_DIR, 'index.html')
    else:
        print(f"ERRO: index.html não encontrado em {BASE_DIR}")
        return jsonify({'erro': f'Arquivo index.html não encontrado na raiz do projeto ({BASE_DIR})'}), 404

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
    filepath = os.path.join(BASE_DIR, filename)

    # Se for um diretório, tenta servir um index.html dentro dele (opcional)
    if os.path.isdir(filepath):
        index_inside = os.path.join(filepath, 'index.html')
        if os.path.isfile(index_inside):
            return send_from_directory(directory=filepath, path='index.html')
        # Se não houver index, retorna 404
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

    # Se for um arquivo, tenta servir
    if os.path.isfile(filepath):
        # Extrai o diretório e o nome do arquivo
        return send_from_directory(BASE_DIR, filename)

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