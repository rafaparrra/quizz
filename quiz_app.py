import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz por Asignatura', layout='centered')

# Cargar el DataFrame completo (caché para rendimiento)
@st.cache_data
func load_full_df():
    excel_path = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(excel_path)
    # Asegurar que existe la columna 'Asignatura'
    if 'Asignatura' not in df.columns:
        df['Asignatura'] = 'General'
    return df.dropna(subset=['Pregunta'])

# Inicialización o cambio de asignatura
def init_subject(subject):
    df = load_full_df()
    sub_df = df[df['Asignatura'] == subject].copy()
    sub_df = sub_df.sample(frac=1).reset_index(drop=True)
    qs = []
    for _, row in sub_df.iterrows():
        opts = [row[c] for c in sub_df.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except Exception:
            correct = None
        random.shuffle(opts)
        qs.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    # Guardar en estado
    st.session_state.questions = qs
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.feedback = ''
    st.session_state.answered = [False] * len(qs)
    st.session_state.selections = [None] * len(qs)
    st.session_state.subject = subject

# Cargar DataFrame y cargar lista de asignaturas
df_full = load_full_df()
asignaturas = df_full['Asignatura'].unique().tolist()
selected_subject = st.selectbox('Selecciona Asignatura:', asignaturas)

# Inicializar quiz si no se ha hecho o cambió la asignatura
if 'subject' not in st.session_state or st.session_state.subject != selected_subject:
    init_subject(selected_subject)

# Variables de estado
questions = st.session_state.questions
n = len(questions)
idx = st.session_state.current
correct_count = st.session_state.score
answered_total = sum(st.session_state.answered)
wrong_count = answered_total - correct_count

# Definición de funciones de navegación y comprobación
def check():
    choice = st.session_state.choice
    st.session_state.answered[idx] = True
    st.session_state.selections[idx] = choice
    correct = questions[idx]['correcto']
    if choice == correct:
        st.session_state.score += 1
        st.session_state.feedback = '¡Correcto! 🎉'
    else:
        st.session_state.feedback = f'Incorrecto. Correcto: {correct}'


def go_next():
    if st.session_state.current < n - 1:
        st.session_state.current += 1
    st.session_state.feedback = ''
    if 'choice' in st.session_state:
        del st.session_state.choice


def go_prev():
    if st.session_state.current > 0:
        st.session_state.current -= 1
    st.session_state.feedback = ''
    if 'choice' in st.session_state:
        del st.session_state.choice

# Interfaz de quiz
st.write(f"Asignatura: **{selected_subject}**")
st.write(f'Pregunta {idx+1} de {n} | Aciertos: {correct_count} | Errores: {wrong_count}')
if idx < n:
    q = questions[idx]
    st.markdown(f"**{q['pregunta']}**")
    st.radio('Opciones:', q['opciones'], key='choice')
    cols = st.columns(3)
    with cols[0]:
        st.button('⬅ Anterior', on_click=go_prev, disabled=idx==0)
    with cols[1]:
        st.button('✔ Comprobar', on_click=check, disabled=st.session_state.answered[idx])
    with cols[2]:
        st.button('➡ Siguiente', on_click=go_next, disabled=not st.session_state.answered[idx])
    if st.session_state.feedback:
        if 'Correcto' in st.session_state.feedback:
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)
else:
    st.header('Resultado Final')
    st.write(f'Has acertado **{correct_count}** de **{n}** preguntas y fallado **{wrong_count}**.')
    if correct_count == n:
        st.balloons()
    if st.button('🔄 Reiniciar asignatura'):
        init_subject(selected_subject)
