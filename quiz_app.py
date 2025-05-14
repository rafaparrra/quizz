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
    if 'Asignatura' in df.columns:
        df['Asignatura'] = df['Asignatura'].fillna(method='ffill')
    else:
        df['Asignatura'] = 'General'
    df['Asignatura'] = df['Asignatura'].astype(str).str.strip()
    df['Asignatura_clean'] = df['Asignatura'].str.upper()
    return df.dropna(subset=['Pregunta'])

# Carga casos prácticos desde columnas específicas
def load_cases_wide():
    path = Path(__file__).parent / 'Daypo_URLs_por_Asignatura.xlsx'
    return pd.read_excel(path)

# Función para normalizar nombres (quitar acentos, signos y mayúsculas)
import unicodedata, re

def normalize_name(s):
    s = str(s)
    nkfd = unicodedata.normalize('NFD', s)
    no_accents = ''.join([c for c in nkfd if unicodedata.category(c) != 'Mn'])
    alnum = re.sub(r'[^A-Za-z0-9]', '', no_accents)
    return alnum.upper()

# Inicializa el quiz para una asignatura dada
def init_quiz(subject_clean):
    df = load_quiz_df()
    if subject_clean == 'TODAS':
        sub_df = df.sample(frac=1).reset_index(drop=True)
    else:
        sub_df = df[df['Asignatura_clean'] == subject_clean].sample(frac=1).reset_index(drop=True)
    qs = []
    for _, row in sub_df.iterrows():
        opts = [row[col] for col in sub_df.columns if col.startswith('Opción') and pd.notna(row[col])]
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except:
            correct = None
        random.shuffle(opts)
        qs.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    st.session_state.questions = qs
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.feedback = ''
    st.session_state.answered = [False] * len(qs)

# Cargar datos
df_quiz = load_quiz_df()
cases_wide = load_cases_wide()
cases_df = cases_wide.copy()  # wide format kept for quiz

# Selección de asignatura
display_subjects = sorted(df_quiz['Asignatura'].unique())
if len(display_subjects) <= 1:
    display_subjects = ['TODAS']
subject = st.selectbox('Selecciona asignatura:', display_subjects)
subject_clean = subject.strip().upper()

# Reiniciar quiz al cambiar asignatura
if st.session_state.get('subject_clean') != subject_clean:
    st.session_state.subject_clean = subject_clean
    init_quiz(subject_clean)
    st.session_state.page = 'quiz'

# Navegación global
col_q, col_c = st.columns(2)
with col_q:
    if st.button('Ver Preguntas'):
        st.session_state.page = 'quiz'
with col_c:
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
    st.header(f'Casos Prácticos – {subject}')
    # Normalizar nombres para matching de columnas
    norm_sub = normalize_name(subject)
    # Buscar columna que contenga el nombre normalizado
    matched = [col for col in cases_wide.columns if normalize_name(col).find(norm_sub) != -1]
    if matched:
        col_name = matched[0]
        urls = cases_wide[col_name].dropna().tolist()
        if urls:
            for url in urls:
                st.markdown(f"- [Caso Práctico]({url})")
        else:
            st.info('No hay URLs en la columna seleccionada.')
    else:
        st.info('No hay casos prácticos configurados para esta asignatura.')
    if st.button('Volver a Preguntas'):
        st.session_state.page = 'quiz'
else:
    qs = st.session_state.questions
    total = len(qs)
    idx = st.session_state.current
    sc = st.session_state.score
    ans = sum(st.session_state.answered)
    wrong = ans - sc

    if total == 0:
        st.warning('No hay preguntas para esta asignatura.')
    elif idx < total:
        st.write(f"Asignatura: **{subject}**")
        st.write(f"Pregunta {idx+1} de {total} | Aciertos: {sc} | Errores: {wrong}")
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
        st.write(f"Has acertado **{sc}** de **{total}** preguntas y fallado **{wrong}**.")
        if sc == total:
            st.balloons()
        if st.button('Reiniciar Quiz'):
            init_quiz(subject_clean)
df_quiz = load_quiz_df()
cases_df = load_cases_wide()
# Normalizar columnas para casos prácticos
if 'Asignatura' in cases_df.columns:
    cases_df['Asignatura'] = cases_df['Asignatura'].astype(str).str.strip()
    cases_df['Asignatura_clean'] = cases_df['Asignatura'].str.upper()
else:
    cases_df['Asignatura'] = 'General'
    cases_df['Asignatura_clean'] = 'GENERAL'

# Selección de asignatura
display_subjects = sorted(df_quiz['Asignatura'].unique())
if len(display_subjects) <= 1:
    display_subjects = ['TODAS']
subject = st.selectbox('Selecciona asignatura:', display_subjects)
subject_clean = subject.strip().upper()

# Reiniciar quiz al cambiar asignatura
if st.session_state.get('subject_clean') != subject_clean:
    st.session_state.subject_clean = subject_clean
    init_quiz(subject_clean)
    st.session_state.page = 'quiz'

# Botones globales para cambiar de página
col_q, col_c = st.columns(2)
with col_q:
    if st.button('Ver Preguntas'):
        st.session_state.page = 'quiz'
with col_c:
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
    st.header(f'Casos Prácticos – {subject}')
    sub = cases_df[cases_df['Asignatura_clean'] == subject_clean]
    if sub.empty:
        st.info('No hay casos prácticos para esta asignatura.')
    else:
        for _, row in sub.iterrows():
            st.markdown(f"- [{row['Asignatura']}]({row['URL']})")
    if st.button('Volver a Preguntas'):
        st.session_state.page = 'quiz'
else:
    qs = st.session_state.questions
    total = len(qs)
    idx = st.session_state.current
    sc = st.session_state.score
    ans = sum(st.session_state.answered)
    wrong = ans - sc

    if total == 0:
        st.warning('No hay preguntas para esta asignatura.')
    elif idx < total:
        st.write(f"Asignatura: **{subject}**")
        st.write(f"Pregunta {idx+1} de {total} | Aciertos: {sc} | Errores: {wrong}")
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
        st.write(f"Has acertado **{sc}** de **{total}** preguntas y fallado **{wrong}**.")
        if sc == total:
            st.balloons()
        if st.button('Reiniciar Quiz'):
            init_quiz(subject_clean)
