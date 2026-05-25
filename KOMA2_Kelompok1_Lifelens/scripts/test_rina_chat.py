import os
import asyncio
from dotenv import load_dotenv
from app.services.supabase_client import get_supabase_client
from app.services.gemini import get_rina_response
from app.services.encryption import encrypt_text

load_dotenv()

async def test_full_flow():
    print("--- Memulai Tes Integrasi RINA ---")
    
    supabase = get_supabase_client()
    
    # 1. Pastikan ada user test
    print("Mengecek user test...")
    test_user_id = "00000000-0000-0000-0000-000000000000"
    user_res = supabase.table('users').select('*').eq('id', test_user_id).execute()
    
    if not user_res.data:
        print("User test tidak ada, membuat user baru...")
        supabase.table('users').insert({
            "id": test_user_id,
            "display_name": "User Pengetesan"
        }).execute()
    else:
        print("OK: User test ditemukan.")

    # 2. Buat session test
    print("Membuat session test...")
    session_res = supabase.table('sessions').insert({
        "user_id": test_user_id,
        "summary": "Testing session flow"
    }).execute()
    session_id = session_res.data[0]['id']
    print(f"OK: Session created (ID: {session_id})")

    # 3. Simulasi chat
    user_message = "Hai Rina, aku hari ini capek banget kerja lembur terus."
    print(f"\nUser: {user_message}")
    
    try:
        rina_response, extracted_data = await get_rina_response(test_user_id, user_message)
        # Bersihkan dari karakter non-ASCII untuk print saja
        safe_rina_msg = rina_response.encode('ascii', 'ignore').decode('ascii')
        print(f"RINA: {safe_rina_msg}")
        print(f"Data Terdeteksi: {extracted_data}")
        
        # 4. Simpan ke database (simulasi apa yang dilakukan API nantinya)
        print("\nMencoba simpan pesan terenkripsi ke Supabase...")
        
        # Simpan pesan User
        supabase.table('conversation_texts').insert({
            "session_id": session_id,
            "encrypted_text": encrypt_text(user_message),
            "sender": "user"
        }).execute()
        
        # Simpan pesan Rina
        supabase.table('conversation_texts').insert({
            "session_id": session_id,
            "encrypted_text": encrypt_text(rina_response),
            "sender": "rina"
        }).execute()
        
        print("OK: Chat berhasil disimpan dan dienkripsi!")
            
    except Exception as e:
        import traceback
        print(f"Error saat integrasi: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_flow())
