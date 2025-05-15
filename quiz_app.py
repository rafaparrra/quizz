import streamlit as st
import pandas as pd
import random
from pathlib import Path
import unicodedata
import re
from docx import Document

# Configuración de la página
st.set_page_config(page_title='Quiz por Asignatura', layout='wide')

# Función para normalizar nombres def normalize_name(s):
    s = str(s)
    nkfd = unicodedata.normalize('NFD', s)
    no_accents = ''.join(c for c in nkfd if unicodedata.category(c) != 'Mn')
    cleaned = re.sub(r'[^A-Za-z0-9]', '', no_accents)
    return cleaned.upper()

# Carga del Excel completo
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

# Carga del Excel de Normas barajado
def load_quiz_normas_shuffled():
    path = Path(__file__).parent / 'Preguntas_Normas_Ciberseguridad_Shuffled.xlsx'
    df = pd.read_excel(path)
    df['Asignatura'] = df['Asignatura'].astype(str).str.strip()
    df['Asignatura_clean'] = df['Asignatura'].apply(normalize_name)
    return df.dropna(subset=['Pregunta'])

# Carga de preguntas desde archivos DOCX en el root
def load_docx_quiz():
    DOCX_FILES = [
        "Simulacro_Incidentes_Examen_SOL.docx",
        "Puesta_Produccion_Examen_SOL.docx",
        "Simulacro_Hacking_Etico_Examen-SOL.docx",
        "Simulacro_Bastionado_Examen-SOL.docx",
        "Simulacro_Examen_Analisis-SOL.docx",
        "Nombre_Docx_Faltante.docx"
    ]
    rows = []
    base = Path(__file__).parent
    for fname in DOCX_FILES:
        p = base / fname
        if not p.exists():
            st.warning(f"⚠️ No encontrado: {fname}")
            continue
        doc = Document(p)
        lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        if not lines:
            continue
        pregunta = lines[0]
        opciones = []
        for ln in lines[1:]:
            m = re.match(r'^[A-D]\)\s*(.*)', ln)
            if m:
                opciones.append(m.group(1).strip())
            if len(opciones) >= 4:
                break
        while len(opciones) < 4:
            opciones.append(None)
        rows.append({
            'Asignatura': 'Asignatura 2.0',
            'Pregunta': pregunta,
            'Opción 1': opciones[0],
            'Opción 2': opciones[1],
            'Opción 3': opciones[2],
            'Opción 4': opciones[3],
            'Resp.': 1
        })
    df = pd.DataFrame(rows)
    df['Asignatura_clean'] = df['Asignatura'].apply(normalize_name)
    return df

# Carga de casos prácticos
def load_cases_wide():
    path = Path(__file__).parent / 'Daypo_URLs_por_Asignatura.xlsx'
    return pd.read_excel(path)

# Función genérica para iniciar un quiz desde un DataFrame
def init_quiz_from_df(df, subject_clean):
    sub = df[df['Asignatura_clean'] == subject_clean].sample(frac=1).reset_index(drop=True)
    qs = []
    for _, row in sub.iterrows():
        opts = [row[c] for c in df.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correcto = opts[int(row.get('Resp.', 1)) - 1]
        except:
            correcto = None
        random.shuffle(opts)
        qs.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correcto})
    st.session_state.questions = qs
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.answered = [False] * len(qs)
    st.session_state.feedback = ''

# Navegación y comprobación de respuestas
def check_answer():
    idx = st.session_state.current
    choice = st.session_state.choice
    st.session_state.answered[idx] = True
    correcto = st.session_state.questions[idx]['correcto']
    if choice == correcto:
        st.session_state.score += 1
        st.session_state.feedback = '¡Correcto! 🎉'
    else:
        st.session_state.feedback = f"Incorrecto. Correcto: {correcto}"

def go_prev():
    st.session_state.current = max(0, st.session_state.current - 1)
    st.session_state.feedback = ''

def go_next():
    max_idx = len(st.session_state.questions) - 1
    st.session_state.current = min(max_idx, st.session_state.current + 1)
    st.session_state.feedback = ''
    st.session_state.pop('choice', None)

# Carga inicial de datos
df_excel = load_quiz_df()
df_normas = load_quiz_normas_shuffled()
df_docx = load_docx_quiz()
cases_wide = load_cases_wide()

# Sidebar de navegación
st.sidebar.header("Navegación")
page = st.sidebar.selectbox('Elige página:', [
    'Quiz general',
    'Asignatura 2.0',
    'Normativa de Ciberseguridad',
    'Casos Prácticos'
])

# Inicialización según página seleccionada
if page == 'Quiz general':
    init_quiz_from_df(df_excel, normalize_name('TODAS'))
elif page == 'Asignatura 2.0':
    init_quiz_from_df(df_docx, normalize_name('Asignatura 2.0'))
elif page == 'Normativa de Ciberseguridad':
    init_quiz_from_df(df_normas, normalize_name('Normativa de Ciberseguridad (solo normas)'))
else:
    st.header('Casos Prácticos – Normativa de Ciberseguridad')
    matches = [col for col in cases_wide.columns if normalize_name(col).find(normalize_name('Normativa de Ciberseguridad')) != -1]
    if matches:
        urls = cases_wide[matches[0]].dropna().tolist()
        for url in urls:
            st.markdown(f"- [Caso Práctico]({url})")
    else:
        st.info('No hay casos prácticos.')

# Renderizado del quiz
if page != 'Casos Prácticos':
    qs = st.session_state.questions
    total = len(qs)
    idx = st.session_state.current
    sc = st.session_state.score
    ans = sum(st.session_state.answered)
    wrong = ans - sc

    if total == 0:
        st.warning('No hay preguntas.')
    else:
        st.write(f"### {page}")
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

        if idx == total - 1:
            st.button('🔄 Reiniciar Quiz', on_click=lambda: init_quiz_from_df(
                df_excel if page=='Quiz general' else df_docx if page=='Asignatura 2.0' else df_normas,
                normalize_name('TODAS') if page=='Quiz general' else normalize_name(page)
            ))
