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
        correct = None
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except:
            pass
        random.shuffle(opts)
        qs.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    return qs

# Inicialización de estado
def init_state():
    qs = load_questions()
    st.session_state.questions = qs
    st.session_state.current = 0
    st.session_state.answered = [False] * len(qs)
    st.session_state.selections = [None] * len(qs)
    st.session_state.score = 0

if 'questions' not in st.session_state:
    init_state()

qs = st.session_state.questions
n = len(qs)
idx = st.session_state.current

# Título y progreso
st.title('🚀 Quiz Rápido')
st.write(f'Pregunta {idx+1} de {n}   |   Aciertos: {st.session_state.score}')

# Mostrar pregunta actual
d = qs[idx]
st.markdown(f"**{d['pregunta']}**")
deselected = st.radio('Opciones:', d['opciones'], key=f'choice_{idx}')

# Comprobar o avanzar
if not st.session_state.answered[idx]:
    if st.button('✔ Comprobar', key=f'check_{idx}'):
        st.session_state.answered[idx] = True
        st.session_state.selections[idx] = deselected
        if deselected == d['correcto']:
            st.session_state.score += 1
            st.success('¡Correcto! 🎉')
        else:
            st.error(f'Incorrecto. Correcto: {d["correcto"]}')
else:
    if idx < n - 1:
        if st.button('➡ Siguiente'):
            st.session_state.current = idx + 1
    else:
        if st.button('🏁 Resultado'):
            st.session_state.current = idx + 1

# Resultado final\if st.session_state.current == n:
    st.markdown('---')
    st.header('🎉 Resultado Final')
    st.write(f'Has acertado **{st.session_state.score}** de **{n}** preguntas.')
    if st.session_state.score == n:
        st.balloons()
    if st.button('🔄 Reiniciar'):
        st.session_state.clear()
