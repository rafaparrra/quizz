import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz Interactivo', layout='wide')

# Función para inicializar preguntas en session_state
def init_quiz():
    excel_path = Path(__file__).parent / 'Quizz Completo.xlsx'
    if not excel_path.exists():
        st.error(f"No encuentro el archivo `{excel_path.name}` en el directorio.")
        st.stop()

    df = pd.read_excel(excel_path).dropna(subset=['Pregunta'])
    df = df.sample(frac=1).reset_index(drop=True)

    # Crear listas de estado para todas las preguntas
    st.session_state.questions = []
    st.session_state.answered = []
    st.session_state.selections = []

    for _, row in df.iterrows():
        opciones = [row[col] for col in df.columns if col.startswith('Opción') and pd.notna(row[col])]
        try:
            correcto = opciones[int(row.get('Resp.', 1)) - 1]
        except Exception:
            correcto = None
        random.shuffle(opciones)
        st.session_state.questions.append({'pregunta': row['Pregunta'], 'opciones': opciones, 'correcto': correcto})
        st.session_state.answered.append(False)
        st.session_state.selections.append(None)

# Inicializar quiz al inicio
if 'questions' not in st.session_state:
    init_quiz()

questions = st.session_state.questions
num_q = len(questions)

# Interfaz principal
st.title('🎯 Quiz Interactivo')
st.markdown('Selecciona tu respuesta y pulsa **Comprobar** para cada pregunta.')

# Mostrar cada pregunta en un expander
for i, q in enumerate(questions):
    with st.expander(f'Pregunta {i+1} de {num_q}', expanded=False):
        st.write(q['pregunta'])
        choice = st.radio('', q['opciones'], key=f'opt_{i}')

        # Comprobar respuesta sólo una vez
        if not st.session_state.answered[i]:
            if st.button('Comprobar', key=f'check_{i}'):
                st.session_state.answered[i] = True
                st.session_state.selections[i] = choice

        # Feedback inmediato tras comprobar
        if st.session_state.answered[i]:
            if st.session_state.selections[i] == q['correcto']:
                st.success('¡Correcto! 🎉')
            else:
                st.error(f"Incorrecto. Respuesta correcta: **{q['correcto']}**")

# Mostrar resultado final cuando todas respondidas
if all(st.session_state.answered):
    score = sum(1 for i in range(num_q) if st.session_state.selections[i] == questions[i]['correcto'])
    st.markdown('---')
    st.header('🏁 Resultado final')
    st.write(f'Has acertado **{score}** de **{num_q}** preguntas.')
    if score == num_q:
        st.balloons()

# Función para reiniciar el quiz
def reset_quiz():
    for key in ['questions', 'answered', 'selections']:
        if key in st.session_state:
            del st.session_state[key]

# Botón de reinicio
st.markdown('---')
st.button('Reiniciar Quiz', on_click=reset_quiz)
