import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz Interactivo', layout='wide')

@st.cache_data(show_spinner=False)
def load_questions(filepath):
    """Lee y baraja las preguntas del Excel (carga en caché)."""
    df = pd.read_excel(filepath).dropna(subset=['Pregunta'])
    df = df.sample(frac=1, random_state=None).reset_index(drop=True)
    questions = []
    for _, row in df.iterrows():
        opciones = [row[col] for col in df.columns if col.startswith('Opción') and pd.notna(row[col])]
        try:
            correcto = opciones[int(row.get('Resp.', 1)) - 1]
        except Exception:
            correcto = None
        random.shuffle(opciones)
        questions.append({'pregunta': row['Pregunta'], 'opciones': opciones, 'correcto': correcto})
    return questions

# Ruta al Excel y carga de preguntas
excel_path = Path(__file__).parent / 'Quizz Completo.xlsx'
if not excel_path.exists():
    st.error(f"No encuentro el archivo `{excel_path.name}` en el directorio.")
    st.stop()
questions = load_questions(excel_path)
num_q = len(questions)

# Inicializar estado solo una vez para listas de respuestas y comprobaciones
if 'answered' not in st.session_state:
    st.session_state.answered = [False] * num_q
    st.session_state.selections = [None] * num_q

# Título y descripción
st.title('🎯 Quiz Interactivo')
st.markdown('Selecciona tu respuesta y pulsa **Comprobar** para cada pregunta.')

# Mostrar preguntas con expanders para no recargar toda la página
for i, q in enumerate(questions):
    with st.expander(f'Pregunta {i+1} de {num_q}', expanded=False):
        st.write(q['pregunta'])
        choice = st.radio('', q['opciones'], key=f'opt_{i}')
        if not st.session_state.answered[i]:
            if st.button('Comprobar', key=f'check_{i}'):
                st.session_state.answered[i] = True
                st.session_state.selections[i] = choice
        if st.session_state.answered[i]:
            if st.session_state.selections[i] == q['correcto']:
                st.success('¡Correcto! 🎉')
            else:
                st.error(f"Incorrecto. La respuesta correcta es: **{q['correcto']}**")

# Al terminar todas, mostrar resultado
enabled_all = all(st.session_state.answered)
if enabled_all:
    score = sum(1 for i in range(num_q) if st.session_state.selections[i] == questions[i]['correcto'])
    st.markdown('---')
    st.header('🏁 Resultado final')
    st.write(f'Has acertado **{score}** de **{num_q}** preguntas.')
    if score == num_q:
        st.balloons()

# Botón para reiniciar el quiz
def reset_quiz():
    del st.session_state.answered
    del st.session_state.selections
    st.experimental_rerun()

st.markdown('---')
st.button('Reiniciar Quiz', on_click=reset_quiz)
