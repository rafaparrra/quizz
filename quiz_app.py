import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz Rápido', layout='centered')

@st.cache_data
def load_questions():
    excel = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(excel).dropna(subset=['Pregunta'])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    qs = []
    for _, row in df.iterrows():
        opts = [row[c] for c in df.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except:
            correct = None
        random.shuffle(opts)
        qs.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    return qs

# Inicialización de estado
if 'questions' not in st.session_state:
    st.session_state.questions = load_questions()
    st.session_state.current = 0
    st.session_state.answered = [False] * len(st.session_state.questions)
    st.session_state.selections = [None] * len(st.session_state.questions)
    st.session_state.score = 0

qs = st.session_state.questions
n = len(qs)
idx = st.session_state.current

# Pantalla de Quiz
st.title('🚀 Quiz Rápido')
if idx < n:
    st.write(f'Pregunta {idx+1} de {n}   |   Aciertos: {st.session_state.score}')
    q = qs[idx]
    choice = st.radio('Opciones:', q['opciones'], key=f'choice_{idx}')

    # Comprobar respuesta
    if not st.session_state.answered[idx]:
        if st.button('✔ Comprobar'):
            st.session_state.answered[idx] = True
            st.session_state.selections[idx] = choice
            if choice == q['correcto']:
                st.session_state.score += 1
                st.success('¡Correcto! 🎉')
            else:
                st.error(f'Incorrecto. Correcto: {q["correcto"]}')
    else:
        # Avanzar a siguiente o ver resultado
        if idx < n - 1:
            if st.button('➡ Siguiente'):
                st.session_state.current += 1
        else:
            if st.button('🏁 Ver resultado'):
                st.session_state.current += 1
else:
    # Resultado final
    st.header('🎉 Resultado Final')
    st.write(f'Has acertado **{st.session_state.score}** de **{n}** preguntas.')
    if st.session_state.score == n:
        st.balloons()
    if st.button('🔄 Reiniciar'):
        st.session_state.clear()
