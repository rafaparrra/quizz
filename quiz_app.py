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
    questions = []
    for _, row in df.iterrows():
        opts = [row[c] for c in df.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except:
            correct = None
        random.shuffle(opts)
        questions.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    return questions

# Callbacks para botones
def check_answer():
    idx = st.session_state.current
    choice = st.session_state[f'choice_{idx}']
    st.session_state.answered[idx] = True
    st.session_state.selections[idx] = choice
    if choice == st.session_state.questions[idx]['correcto']:
        st.session_state.score += 1
        st.success('¡Correcto! 🎉')
    else:
        correct = st.session_state.questions[idx]['correcto']
        st.error(f'Incorrecto. Correcto: {correct}')

def next_question():
    st.session_state.current += 1

def restart_quiz():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Inicialización del estado
if 'questions' not in st.session_state:
    st.session_state.questions = load_questions()
    st.session_state.current = 0
    total = len(st.session_state.questions)
    st.session_state.answered = [False] * total
    st.session_state.selections = [None] * total
    st.session_state.score = 0

questions = st.session_state.questions
n = len(questions)
idx = st.session_state.current

# Interfaz
st.title('🚀 Quiz Rápido')
if idx < n:
    st.write(f'Pregunta {idx+1} de {n}   |   Aciertos: {st.session_state.score}')
    st.markdown(f"**{questions[idx]['pregunta']}**")

    # Radio widget
    st.radio(
        'Opciones:',
        questions[idx]['opciones'],
        key=f'choice_{idx}'
    )

    # Botón Comprobar principal
    if not st.session_state.answered[idx]:
        st.button('✔ Comprobar', on_click=check_answer, key=f'check_{idx}')
    else:
        # Una vez comprobado, botón para avanzar o finalizar
        if idx < n-1:
            st.button('➡ Siguiente', on_click=next_question, key=f'next_{idx}')
        else:
            st.button('🏁 Ver resultado', on_click=next_question, key='finish')
else:
    # Resultado final
    st.header('🎉 Resultado Final')
    st.write(f'Has acertado **{st.session_state.score}** de **{n}** preguntas.')
    if st.session_state.score == n:
        st.balloons()
    st.button('🔄 Reiniciar', on_click=restart_quiz, key='reset')
