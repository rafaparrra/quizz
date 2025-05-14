import streamlit as st
import pandas as pd
import random
from pathlib import Path
import unicodedata, re

# Configuración de la página
st.set_page_config(page_title='Quiz por Asignatura', layout='centered')

# Funciones auxiliares para normalizar

def normalize_name(s):
    s = str(s)
    nkfd = unicodedata.normalize('NFD', s)
    no_accents = ''.join(c for c in nkfd if unicodedata.category(c) != 'Mn')
    alnum = re.sub(r'[^A-Za-z0-9]', '', no_accents)
    return alnum.upper()

@st.cache_data
def load_quiz_df():
    path = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(path)
    if 'Asignatura' in df.columns:
        df['Asignatura'] = df['Asignatura'].fillna(method='ffill')
    else:
        df['Asignatura'] = 'General'
    df['Asignatura'] = df['Asignatura'].astype(str).str.strip()
    df['Asignatura_clean'] = df['Asignatura'].apply(normalize_name)
    return df.dropna(subset=['Pregunta'])

@st.cache_data
def load_quiz_normas_shuffled():
    path = Path(__file__).parent / 'Preguntas_Normas_Ciberseguridad_Shuffled.xlsx'
    df = pd.read_excel(path)
    df['Asignatura'] = df['Asignatura'].astype(str).str.strip()
    df['Asignatura_clean'] = df['Asignatura'].apply(normalize_name)
    return df.dropna(subset=['Pregunta'])

@st.cache_data
def load_cases_wide():
    path = Path(__file__).parent / 'Daypo_URLs_por_Asignatura.xlsx'
    return pd.read_excel(path)

def init_quiz(subject_clean):
    df = load_quiz_df()
    if subject_clean == 'TODAS':
        sub = df.sample(frac=1).reset_index(drop=True)
    else:
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
    st.session_state.questions = qs
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.answered = [False] * len(qs)
    st.session_state.feedback = ''

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
    st.session_state.current = max(0, st.session_state.current - 1)
    st.session_state.feedback = ''

def go_next():
    max_idx = len(st.session_state.questions) - 1
    st.session_state.current = min(max_idx, st.session_state.current + 1)
    st.session_state.feedback = ''
    st.session_state.pop('choice', None)

# Carga inicial
df_quiz = load_quiz_df()
cases_wide = load_cases_wide()

# Selector de asignatura
display_subjects = sorted(df_quiz['Asignatura'].unique())
if len(display_subjects) == 1:
    display_subjects = ['TODAS'] + display_subjects
subject = st.selectbox('Selecciona asignatura:', display_subjects, key='subject')
subject_clean = normalize_name(subject)
if st.session_state.get('subject_clean') != subject_clean:
    st.session_state.subject_clean = subject_clean
    init_quiz(subject_clean)
    st.session_state.page = 'quiz'

# Mostrar botón solo si la asignatura seleccionada es Normativa de Ciberseguridad
if normalize_name(subject) == normalize_name('Normativa de Ciberseguridad'):
    if st.button('🧾 Quiz solo Normas de Ciberseguridad'):
        df = load_quiz_normas_shuffled()
        subject_clean = normalize_name('Normativa de Ciberseguridad (solo normas)')
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

        st.session_state.questions = qs
        st.session_state.current = 0
        st.session_state.score = 0
        st.session_state.answered = [False] * len(qs)
        st.session_state.feedback = ''
        st.session_state.page = 'quiz'
        st.session_state.subject_clean = subject_clean

# Botón para Cambiar a Casos
if st.button('Casos Prácticos', key='btn_cases'):
    st.session_state.page = 'cases'

# Renderizado
page = st.session_state.get('page', 'quiz')
if page == 'cases':
    st.header(f'Casos Prácticos – {subject}')
    matches = [col for col in cases_wide.columns if normalize_name(col).find(subject_clean) != -1]
    if matches:
        urls = cases_wide[matches[0]].dropna().tolist()
        if urls:
            for url in urls:
                st.markdown(f"- [Caso Práctico]({url})")
        else:
            st.info('No hay URLs en esa asignatura.')
    else:
        st.info('No hay casos prácticos para esta asignatura.')
    if st.button('Volver a Preguntas', key='btn_back'):
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
    else:
        st.write(f"Asignatura: **{subject}**")
        st.write(f"Pregunta {idx+1} de {total} | Aciertos: {sc} | Errores: {wrong}")
        st.markdown(f"**{qs[idx]['pregunta']}**")
        st.radio('Opciones:', qs[idx]['opciones'], key='choice')

        c1, c2, c3 = st.columns(3)
        with c1:
            c1.button('⬅ Anterior', key='btn_prev', on_click=go_prev, disabled=(idx == 0))
        with c2:
            c2.button('✔ Comprobar', key='btn_check', on_click=check_answer, disabled=st.session_state.answered[idx])
        with c3:
            c3.button('➡ Siguiente', key='btn_next', on_click=go_next, disabled=not st.session_state.answered[idx])

        if st.session_state.feedback:
            if 'Correcto' in st.session_state.feedback:
                st.success(st.session_state.feedback)
            else:
                st.error(st.session_state.feedback)

        if idx == total - 1:
            st.button('🔄 Reiniciar Quiz', key='btn_restart', on_click=lambda: init_quiz(subject_clean))

        # Botón para volver al quiz completo si estás en el modo solo normas
        if subject_clean == normalize_name('Normativa de Ciberseguridad (solo normas)'):
            if st.button('↩ Volver al Quiz completo de Normativa'):
                subject_clean = normalize_name('Normativa de Ciberseguridad')
                st.session_state.subject_clean = subject_clean
                init_quiz(subject_clean)
                st.session_state.page = 'quiz'
