import bcrypt
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

username = "dr_novo"        
password = "senha123"       

password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

response = supabase.table('medicos').insert({
    'username': username,
    'password_hash': password_hash
}).execute()

print("Médico criado:", response.data)