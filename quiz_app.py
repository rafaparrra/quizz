import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz Interactivo', layout='wide')

# Inicializar quiz y estado en session_state
def init_quiz():
    excel_path = Path(__file__).parent / 'Quizz Completo.xlsx'
    if not excel_path.exists():
        st.error(f"No encuentro el archivo `{excel_path.name}` en el directorio.")
        st.stop()

    df = pd.read_excel(excel_path).dropna(subset=['Pregunta'])
    df = df.sample(frac=1).reset_index(drop=True)

    questions = []
    for _, row in df.iterrows():
        opciones = [row[col] for col in df.columns if col.startswith('Opción') and pd.notna(row[col])]
        try:
            correcto = opciones[int(row.get('Resp.', 1)) - 1]
        except Exception:
            correcto = None
        random.shuffle(opciones)
        questions.append({'pregunta': row['Pregunta'], 'opciones': opciones, 'correcto': correcto})

    st.session_state.questions = questions
    # Claves para respuestas y comprobaciones
    for i in range(len(questions)):
        st.session_state[f'sel_{i}'] = None
        st.session_state[f'answered_{i}'] = False

# Solo inicializa la primera vez
if 'questions' not in st.session_state:
    init_quiz()

questions = st.session_state.questions
num_q = len(questions)

# Interfaz principal
st.title('🎯 Quiz Interactivo')
st.markdown('Selecciona tu respuesta y pulsa **Comprobar** para cada pregunta.')

# Sidebar con progreso dinámico
score = sum(
    1 for i, q in enumerate(questions)
    if st.session_state.get(f'answered_{i}') and st.session_state.get(f'sel_{i}') == q['correcto']
)
st.sidebar.title('Progreso')
st.sidebar.write(f'Acertadas: {score} / {num_q}')
st.sidebar.progress(score / num_q if num_q else 0)

# Mostrar preguntas una a una con feedback inmediato
for i, q in enumerate(questions):
    st.subheader(f'Pregunta {i+1} de {num_q}')
    st.write(q['pregunta'])

    # Selector
    choice = st.radio('', q['opciones'], key=f'opt_{i}')

    # Almacena selección en session_state
    st.session_state[f'sel_{i}'] = choice

    # Botón de comprobar
    if not st.session_state[f'answered_{i}']:
        if st.button('Comprobar', key=f'check_{i}'):
            st.session_state[f'answered_{i}'] = True

    # Feedback si ya comprobado
    if st.session_state[f'answered_{i}']:
        if st.session_state[f'sel_{i}'] == q['correcto']:
            st.success('¡Correcto! 🎉')
        else:
            st.error(f"Incorrecto. La respuesta correcta es: **{q['correcto']}**")

# Reiniciar quiz
st.markdown('---')
if st.button('Reiniciar Quiz'):
    for k in list(st.session_state.keys()):
        if k.startswith('opt_') or k.startswith('answered_') or k == 'questions':
            del st.session_state[k]
    st.experimental_rerun()
