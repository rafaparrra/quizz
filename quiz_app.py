import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz por Asignatura', layout='centered')

# Carga y cache de datos
@st.cache_data
def load_full_df():
    path = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(path)
    if 'Asignatura' not in df.columns:
        df['Asignatura'] = 'General'
    return df.dropna(subset=['Asignatura','Pregunta'])

@st.cache_data
def load_urls_df():
    path = Path(__file__).parent / 'Daypo_URLs_por_Asignatura.xlsx'
    df = pd.read_excel(path)
    if 'Asignatura' not in df.columns:
        df['Asignatura'] = 'General'
    return df.dropna(subset=['Asignatura','URL'])

# Inicializa o reinicia el quiz para la asignatura seleccionada
def init_subject(subject):
    df = load_full_df()
    sub = df[df['Asignatura']==subject].sample(frac=1).reset_index(drop=True)
    qs = []
    for _, row in sub.iterrows():
        opts = [row[c] for c in sub.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correct = opts[int(row.get('Resp.',1))-1]
        except:
            correct = None
        random.shuffle(opts)
        qs.append({'pregunta':row['Pregunta'],'opciones':opts,'correcto':correct})
    st.session_state.questions = qs
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.feedback = ''
    st.session_state.answered = [False]*len(qs)

# Datos
df_full = load_full_df()
asignaturas = sorted(df_full['Asignatura'].unique())
urls_df = load_urls_df()

# Selección de asignatura
subject = st.selectbox('Selecciona asignatura:', asignaturas)

# Página actual: quiz o casos
if 'page' not in st.session_state:
    st.session_state.page = 'quiz'
# Si cambia asignatura, reiniciar quiz y volver a 'quiz'
if st.session_state.get('subject') != subject:
    st.session_state.subject = subject
    st.session_state.page = 'quiz'
    init_subject(subject)

# Botones de navegación entre páginas
d1, d2 = st.columns([1,1])
with d1:
    if st.button('Ver Preguntas'):
        st.session_state.page = 'quiz'
with d2:
    if st.button('Casos Prácticos'):
        st.session_state.page = 'cases'

# Callback de quiz: comprobar y navegar
def check():
    idx = st.session_state.current
    choice = st.session_state.choice
    st.session_state.answered[idx] = True
    correct = st.session_state.questions[idx]['correcto']
    if choice == correct:
        st.session_state.score += 1
        st.session_state.feedback = '¡Correcto! 🎉'
    else:
        st.session_state.feedback = f'Incorrecto. Correcto: {correct}'

def go_prev():
    if st.session_state.current > 0:
        st.session_state.current -= 1
    st.session_state.feedback = ''


def go_next():
    if st.session_state.current < len(st.session_state.questions)-1:
        st.session_state.current += 1
    st.session_state.feedback = ''
    if 'choice' in st.session_state:
        del st.session_state.choice

# Mostrar contenido según la página seleccionada
if st.session_state.page == 'cases':
    st.header(f'Casos Prácticos - {subject}')
    subset = urls_df[urls_df['Asignatura']==subject]
    if subset.empty:
        st.info('No hay casos prácticos para esta asignatura.')
    else:
        for _, row in subset.iterrows():
            title = row.get('Título', row['URL'])
            url = row['URL']
            st.markdown(f'- [{title}]({url})')
    if st.button('Volver a Preguntas'):
        st.session_state.page = 'quiz'

else:  # Página de quiz
    idx = st.session_state.current
    qs = st.session_state.questions
    n = len(qs)
    sc = st.session_state.score
    ans = sum(st.session_state.answered)
    wrong = ans - sc

    if idx < n:
        st.write(f'Asignatura: {subject} | Pregunta {idx+1}/{n} | Aciertos: {sc} | Errores: {wrong}')
        st.markdown(f"**{qs[idx]['pregunta']}**")
        st.radio('Opciones:', qs[idx]['opciones'], key='choice')

        c1, c2, c3 = st.columns(3)
        with c1:
            c1.button('⬅ Anterior', on_click=go_prev, disabled=idx==0)
        with c2:
            c2.button('✔ Comprobar', on_click=check, disabled=st.session_state.answered[idx])
        with c3:
            c3.button('➡ Siguiente', on_click=go_next, disabled=not st.session_state.answered[idx])

        if st.session_state.feedback:
            if 'Correcto' in st.session_state.feedback:
                st.success(st.session_state.feedback)
            else:
                st.error(st.session_state.feedback)
    else:
        st.header('Resultado Final')
        st.write(f'Has acertado **{sc}** de **{n}** preguntas y fallado **{wrong}**.')
        if sc == n:
            st.balloons()
        if st.button('Reiniciar Quiz'):
            init_subject(subject)
