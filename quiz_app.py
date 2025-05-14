import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz Interactivo', layout='wide')

# Inicializar quiz y estado
def init_quiz():
    excel_path = Path(__file__).parent / 'Quizz Completo.xlsx'
    if not excel_path.exists():
        st.error(f"No encuentro el archivo `{excel_path.name}` en el directorio.")
        st.stop()
    df = pd.read_excel(excel_path).dropna(subset=['Pregunta'])
    df = df.sample(frac=1, random_state=None).reset_index(drop=True)
    st.session_state.questions = []
    for _, row in df.iterrows():
        opciones = [row[col] for col in df.columns if col.startswith('Opción') and pd.notna(row[col])]
        try:
            correcto = opciones[int(row.get('Resp.', 1)) - 1]
        except Exception:
            correcto = None
        random.shuffle(opciones)
        st.session_state.questions.append({
            'pregunta': row['Pregunta'],
            'opciones': opciones,
            'correcto': correcto
        })
    st.session_state.score = 0
    # Crear keys individuales para trackear respuestas
    for i in range(len(st.session_state.questions)):
        st.session_state[f'answered_{i}'] = False
        st.session_state[f'selected_{i}'] = None

# Si no está inicializado, lanzar init
if 'questions' not in st.session_state:
    init_quiz()

# Mostrar progreso en sidebar
num_q = len(st.session_state.questions)
st.sidebar.title('Progreso')
st.sidebar.write(f'Acertadas: {st.session_state.score} / {num_q}')
st.sidebar.progress(0 if num_q == 0 else st.session_state.score / num_q)

# Título principal
st.title('🎯 Quiz Interactivo')
st.markdown('Selecciona tu respuesta y pulsa **Comprobar** para cada pregunta.')

# Mostrar preguntas y lógica por pregunta
for i, q in enumerate(st.session_state.questions):
    st.subheader(f'Pregunta {i+1} de {num_q}')
    st.write(q['pregunta'])
    # Radio con la opción seleccionada
    st.session_state[f'selected_{i}'] = st.radio(
        '', q['opciones'], key=f'sel_{i}'
    )
    if not st.session_state[f'answered_{i}']:
        if st.button('Comprobar', key=f'check_{i}'):
            st.session_state[f'answered_{i}'] = True
            if st.session_state[f'selected_{i}'] == q['correcto']:
                st.session_state.score += 1
                st.success('¡Correcto! 🎉')
            else:
                st.error(f"Incorrecto. La respuesta correcta es: **{q['correcto']}**")
    else:
        # Feedback permanente después de comprobar
        if st.session_state[f'selected_{i}'] == q['correcto']:
            st.success('Has contestado correctamente 😊')
        else:
            sel = st.session_state[f'selected_{i}']
            st.error(f"Contestaste: **{sel}**. Correcto: **{q['correcto']}**")

# Botón para reiniciar
st.markdown('---')
if st.button('Reiniciar Quiz'):
    # Limpiar únicamente las claves que hemos creado
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith('answered_') or k.startswith('selected_') or k in ['questions', 'score']]
    for k in keys_to_delete:
        del st.session_state[k]
    st.experimental_rerun()
