import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import tempfile
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AI Pronunciation Coach", page_icon="🎙️")
st.title("🎙️ Seu Coach de Pronúncia (Gemini)")

# --- SEU MATERIAL DE AULA AQUI ---
TARGET_TEXT = """
Usually, Silas's stubborn vision is to sift seven silky seashells beside the station.
"""

st.info(f"📝 **Tarefa:** Leia o texto abaixo em voz alta:\n\n --- \n\n## {TARGET_TEXT}\n ---")

# --- CONFIGURAÇÃO DO GEMINI ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("Erro: Chave de API não encontrada nos segredos.")
    st.stop()

# O PROMPT MÁGICO
SYSTEM_PROMPT = f"""
You are an expert phonetician and English pronunciation coach.
Your task is to listen to the user's audio and compare it closely to this target text: "{TARGET_TEXT}".

You must analyze the actual audio acoustics, not just a transcription. Focus on specific phonemes, stress, and intonation.

Your output must be structured exactly like this:
1.  **Overall Score:** (Give a score from 0-100% based on native-like accuracy).
2.  **Main Issues identified:** (List 2-3 major phonetic errors).
3.  **Detailed Feedback & Correction:**
    * For each major error, identify the specific word and sound (e.g., "The 'th' in 'think'").
    * Explain *physically* how to correct it (e.g., "Your tongue was behind your teeth. To fix it, place the tip of your tongue slightly between your front teeth and blow air").
4.  **Positive Note:** (One thing they did well).

Keep the tone encouraging but technically precise.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    system_instruction=SYSTEM_PROMPT
)

# --- INTERFACE DE GRAVAÇÃO (NOVA) ---
st.write("Clique no microfone para gravar. A gravação termina automaticamente ao parar de falar ou clicar novamente.")

# O novo gravador retorna um dicionário com os bytes do áudio
audio = mic_recorder(
    start_prompt="Gravar Áudio ⏺️",
    stop_prompt="Parar Gravação ⏹️",
    key='recorder',
    format="wav" # Garante formato compatível
)

if audio:
    # Mostra o player de áudio para o aluno ouvir o que gravou
    st.audio(audio['bytes'])
    
    # Botão para enviar para análise
    if st.button("Analisar minha pronúncia 🚀"):
        with st.spinner("O Gemini está analisando sua fonética..."):
            try:
                # 1. Salva o áudio temporariamente
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
                    fp.write(audio['bytes'])
                    temp_filename = fp.name

                # 2. Envia para o Gemini
                audio_file_ref = genai.upload_file(path=temp_filename)
                
                # 3. Pede a análise
                response = model.generate_content(
                    ["Please analyze my pronunciation based on the target text.", audio_file_ref]
                )
                
                # 4. Resultado
                st.success("Análise concluída!")
                st.markdown(response.text)

                # Limpeza
                os.remove(temp_filename)
                
            except Exception as e:
                st.error(f"Ocorreu um erro na conexão com o Gemini: {e}")
