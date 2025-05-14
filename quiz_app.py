import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página para máxima fluidez
st.set_page_config(page_title='Quiz Rápido', layout='centered')

@st.cache_data
def load_questions():
    """Carga y baraja las preguntas, devuelve lista de dicts."""
    excel_path = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(excel_path).dropna(subset=['Pregunta'])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    questions = []
    for _, row in df.iterrows():
        opts = [row[col] for col in df.columns if col.startswith('Opción') and pd.notna(row[col])]
        correct = None
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except:
            pass
        random.shuffle(opts)
        questions.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    return questions

# Inicialización de session_state
if 'questions' not in st.session_state:
    st.session_state.questions = load_questions()
    st.session_state.score = 0
    st.session_state.current = 0
    st.session_state.answered = [False] * len(st.session_state.questions)

questions = st.session_state.questions
n = len(questions)
idx = st.session_state.current

# Título y progreso simple
st.title('🚀 Quiz Rápido')
st.write(f'Pregunta {idx+1} de {n} — Aciertos: {st.session_state.score}')

# Mostrar pregunta actual
q = questions[idx]
st.markdown(f"**{q['pregunta']}**")
# Selector de opciones
selection = st.radio('Opciones:', q['opciones'], key=f'q_{idx}')

# Botones de acción
col1, col2 = st.columns([1,1])
with col1:
    if not st.session_state.answered[idx]:
        if st.button('✔ Comprobar'):
            st.session_state.answered[idx] = True
            if selection == q['correcto']:
                st.session_state.score += 1
                st.success('¡Correcto!')
            else:
                st.error(f'Incorrecto. Correcto: {q["correcto"]}')
with col2:
    if st.session_state.answered[idx] and idx < n-1:
        if st.button('➡ Siguiente'):
            st.session_state.current += 1
            st.experimental_rerun()
    elif st.session_state.answered[idx] and idx == n-1:
        if st.button('🏁 Ver resultado'):
            st.session_state.current += 1
            st.experimental_rerun()

# Mostrar resultado final si acabó
if st.session_state.current == n:
    st.markdown('---')
    st.header('🎉 Resultado Final')
    st.write(f'Has acertado **{st.session_state.score}** de **{n}** preguntas.')
    if st.session_state.score == n:
        st.balloons()
    if st.button('🔄 Reiniciar Quiz'):
        # Reset completo
        del st.session_state.questions
        del st.session_state.score
        del st.session_state.current
        del st.session_state.answered
        st.experimental_rerun()
