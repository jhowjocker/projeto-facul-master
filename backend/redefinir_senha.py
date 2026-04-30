import bcrypt
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

username = "dr_joao"        
nova_senha = "novaSenha456"

novo_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

response = supabase.table('medicos').update({
    'password_hash': novo_hash
}).eq('username', username).execute()

print("Senha atualizada:", response.data)