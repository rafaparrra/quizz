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

# Inicialización del estado de la sesión
def init_state():
    st.session_state.questions = load_questions()
    st.session_state.current = 0
    st.session_state.answered = [False] * len(st.session_state.questions)
    st.session_state.selections = [None] * len(st.session_state.questions)
    st.session_state.score = 0

if 'questions' not in st.session_state:
    init_state()

qs = st.session_state.questions
n = len(qs)
idx = st.session_state.current

# Pantalla de Quiz
st.title('🚀 Quiz Rápido')

if idx < n:
    # Encabezado de progreso
    st.write(f'Pregunta {idx+1} de {n}   |   Aciertos: {st.session_state.score}')
    # Mostrar el texto de la pregunta
    question_text = qs[idx]['pregunta']
    st.markdown(f"**{question_text}**")

    # Opciones de respuesta
    choice = st.radio('Opciones:', qs[idx]['opciones'], key=f'choice_{idx}')

    # Botón para comprobar la respuesta
    if not st.session_state.answered[idx]:
        if st.button('✔ Comprobar', key=f'check_{idx}'):
            st.session_state.answered[idx] = True
            st.session_state.selections[idx] = choice
            if choice == qs[idx]['correcto']:
                st.session_state.score += 1
                st.success('¡Correcto! 🎉')
            else:
                st.error(f'Incorrecto. Correcto: {qs[idx]["correcto"]}')
    else:
        # Después de comprobar, avanzar a la siguiente o ver resultado
        if idx < n - 1:
            if st.button('➡ Siguiente', key=f'next_{idx}'):
                st.session_state.current += 1
        else:
            if st.button('🏁 Ver resultado', key='finish'):
                st.session_state.current += 1
else:
    # Resultado final
    st.header('🎉 Resultado Final')
    st.write(f'Has acertado **{st.session_state.score}** de **{n}** preguntas.')
    if st.session_state.score == n:
        st.balloons()
    # Botón para reiniciar el quiz
    if st.button('🔄 Reiniciar', key='reset'):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()
