import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz por Asignatura', layout='centered')

# Carga y cache de datos completos del quiz
@st.cache_data
 def load_quiz_df():
    path = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(path)
    # Normalizar Asignatura
    df['Asignatura'] = df['Asignatura'].astype(str).str.strip()
    df['Asignatura_clean'] = df['Asignatura'].str.upper()
    return df.dropna(subset=['Pregunta'])

# Carga y prepara casos prácticos (wide-to-long)
@st.cache_data
 def load_cases_df():
    path = Path(__file__).parent / 'Daypo_URLs_por_Asignatura.xlsx'
    wide = pd.read_excel(path)
    # Melt columnas en filas
    cases = wide.melt(var_name='Asignatura', value_name='URL')
    cases['Asignatura'] = cases['Asignatura'].astype(str).str.strip()
    cases['Asignatura_clean'] = cases['Asignatura'].str.upper()
    return cases.dropna(subset=['URL'])

# Inicializa el quiz para una asignatura dada
 def init_quiz(subject_clean):
    df = load_quiz_df()
    sub = df[df['Asignatura_clean'] == subject_clean].sample(frac=1).reset_index(drop=True)
    qs = []
    for _, row in sub.iterrows():
        opts = [row[c] for c in sub.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except:
            correct = None
        random.shuffle(opts)
        qs.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    # Guardar en estado de sesión
    st.session_state.questions = qs
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.feedback = ''
    st.session_state.answered = [False] * len(qs)

# Cargar datos
 df_quiz = load_quiz_df()
 cases_df = load_cases_df()

# Lista de asignaturas para mostrar
 display_subjects = sorted(df_quiz['Asignatura'].unique())
 subject = st.selectbox('Selecciona asignatura:', display_subjects)
 subject_clean = subject.strip().upper()

# Si cambia asignatura, reiniciar quiz
def_subject = st.session_state.get('subject_clean')
 if def_subject != subject_clean:
    st.session_state.subject_clean = subject_clean
    init_quiz(subject_clean)
    st.session_state.page = 'quiz'

# Botones globales para cambiar de página
d1, d2 = st.columns(2)
 with d1:
    if st.button('Ver Preguntas'):
        st.session_state.page = 'quiz'
 with d2:
    if st.button('Casos Prácticos'):
        st.session_state.page = 'cases'

# Funciones de interacción
 def check_answer():
    idx = st.session_state.current
    choice = st.session_state.choice
    st.session_state.answered[idx] = True
    correct = st.session_state.questions[idx]['correcto']
    if choice == correct:
        st.session_state.score += 1
        st.session_state.feedback = '¡Correcto! 🎉'
    else:
        st.session_state.feedback = f"Incorrecto. Correcto: {correct}"

 def go_prev():
    if st.session_state.current > 0:
        st.session_state.current -= 1
    st.session_state.feedback = ''

 def go_next():
    max_idx = len(st.session_state.questions) - 1
    if st.session_state.current < max_idx:
        st.session_state.current += 1
    st.session_state.feedback = ''
    st.session_state.pop('choice', None)

# Mostrar según página seleccionada
 page = st.session_state.get('page', 'quiz')
 if page == 'cases':
    st.header(f'Casos Prácticos - {subject}')
    sub = cases_df[cases_df['Asignatura_clean'] == subject_clean]
    if sub.empty:
        st.info('No hay casos prácticos para esta asignatura.')
    else:
        for _, row in sub.iterrows():
            st.markdown(f"- [{row['Asignatura']}]({row['URL']})")
    if st.button('Volver a Preguntas'):
        st.session_state.page = 'quiz'
 else:
    # Quiz
    qs = st.session_state.questions
    total = len(qs)
    idx = st.session_state.current
    sc = st.session_state.score
    ans = sum(st.session_state.answered)
    wrong = ans - sc

    if total == 0:
        st.warning('No hay preguntas para esta asignatura.')
    elif idx < total:
        st.write(f'Asignatura: **{subject}**')
        st.write(f'Pregunta {idx+1} de {total} | Aciertos: {sc} | Errores: {wrong}')
        st.markdown(f"**{qs[idx]['pregunta']}**")
        st.radio('Opciones:', qs[idx]['opciones'], key='choice')

        c1, c2, c3 = st.columns(3)
        with c1:
            c1.button('⬅ Anterior', on_click=go_prev, disabled=(idx == 0))
        with c2:
            c2.button('✔ Comprobar', on_click=check_answer, disabled=st.session_state.answered[idx])
        with c3:
            c3.button('➡ Siguiente', on_click=go_next, disabled=not st.session_state.answered[idx])

        if st.session_state.feedback:
            if 'Correcto' in st.session_state.feedback:
                st.success(st.session_state.feedback)
            else:
                st.error(st.session_state.feedback)
    else:
        st.header('Resultado Final')
        st.write(f'Has acertado **{sc}** de **{total}** preguntas y fallado **{wrong}**.')
        if sc == total:
            st.balloons()
        if st.button('Reiniciar Quiz'):
            init_quiz(subject_clean)
