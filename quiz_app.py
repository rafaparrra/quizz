import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title='Quiz de Preguntas',
    layout='centered',
    initial_sidebar_state='expanded'
)

# Función para inicializar preguntas en session_state
def init_quiz():
    excel_path = Path(__file__).parent / 'Quizz Completo.xlsx'
    if not excel_path.exists():
        st.error(f'No encuentro el archivo `{excel_path.name}` en el directorio.')
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
        questions.append({
            'pregunta': row['Pregunta'],
            'opciones': opciones,
            'correcto': correcto
        })
    st.session_state.questions = questions
    st.session_state.score = 0
    st.session_state.answered = [False] * len(questions)

# Inicializar si es la primera vez
if 'questions' not in st.session_state:
    init_quiz()

questions = st.session_state.questions
n = len(questions)

st.title('🎯 Quiz Interactivo')
st.markdown('Selecciona tu respuesta y pulsa **Comprobar** para ver si es correcta sin recargar.')

# Mostrar cada pregunta
total_answered = st.session_state.score
for idx, q in enumerate(questions):
    st.subheader(f'Pregunta {idx+1} de {n}')
    st.write(q['pregunta'])
    answer_key = f'answer_{idx}'
    chosen = st.radio('', q['opciones'], key=answer_key)
    if not st.session_state.answered[idx]:
        if st.button('Comprobar', key=f'check_{idx}'):
            is_correct = (chosen == q['correcto'])
            st.session_state.answered[idx] = True
            if is_correct:
                st.session_state.score += 1
                st.success('¡Correcto! 🎉')
            else:
                st.error(f'Incorrecto. La respuesta correcta es: **{q["correcto"]}**')
    else:
        if st.session_state[f'answer_{idx}'] == q['correcto']:
            st.success('Has contestado correctamente 😊')
        else:
            st.error(f"Contestaste: **{st.session_state[f'answer_{idx}']}**. Correcto: **{q['correcto']}**")

# Mostrar puntuación actual
st.sidebar.header('Progreso')
st.sidebar.write(f'Acertadas: {st.session_state.score} / {n}')
st.sidebar.progress(st.session_state.score / n)

# Botón para reiniciar toda la sesión
st.markdown('---')
if st.button('Reiniciar Quiz'):
    for key in list(st.session_state.keys()):
        if key.startswith('answer_') or key.startswith('check_') or key in ['questions', 'score', 'answered']:
            del st.session_state[key]
    st.experimental_rerun()
