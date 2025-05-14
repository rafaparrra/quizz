import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz Rápido', layout='centered')

@st.cache_data
func load_questions():
    # Carga y baraja las preguntas aleatoriamente cada sesión
    excel_file = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(excel_file).dropna(subset=['Pregunta'])
    # Baraja el orden de las preguntas sin semilla fija
    df = df.sample(frac=1).reset_index(drop=True)
    questions = []
    for _, row in df.iterrows():
        opciones = [row[c] for c in df.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correcto = opciones[int(row.get('Resp.', 1)) - 1]
        except:
            correcto = None
        random.shuffle(opciones)
        questions.append({'pregunta': row['Pregunta'], 'opciones': opciones, 'correcto': correcto})
    return questions

# Inicializar estado al inicio
def init_state():
    st.session_state.questions = load_questions()
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.feedback = ''

if 'questions' not in st.session_state:
    init_state()

questions = st.session_state.questions
n = len(questions)
idx = st.session_state.current

# Funciones de interacción

def check_answer():
    choice = st.session_state.choice
    correct = questions[idx]['correcto']
    if choice == correct:
        st.session_state.score += 1
        st.session_state.feedback = '¡Correcto! 🎉'
    else:
        st.session_state.feedback = f'Incorrecto. Correcto: {correct}'


def next_question():
    if st.session_state.current < n - 1:
        st.session_state.current += 1
        st.session_state.feedback = ''
        if 'choice' in st.session_state:
            del st.session_state.choice
    else:
        st.session_state.current += 1

# Interfaz principal
st.title('🚀 Quiz Rápido')
if idx < n:
    q = questions[idx]
    st.write(f'Pregunta {idx+1} de {n} | Aciertos: {st.session_state.score}')
    st.markdown(f"**{q['pregunta']}**")
    st.radio('Opciones:', q['opciones'], key='choice')

    col1, col2 = st.columns(2)
    with col1:
        st.button('✔ Comprobar', on_click=check_answer)
    with col2:
        st.button('➡ Siguiente', on_click=next_question)

    if st.session_state.feedback:
        if 'Correcto' in st.session_state.feedback:
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)
else:
    # Resumen final
    st.header('🎉 Resultado Final')
    st.write(f'Has acertado **{st.session_state.score}** de **{n}** preguntas.')
    if st.session_state.score == n:
        st.balloons()
    if st.button('🔄 Reiniciar'):
        st.session_state.clear()
