import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz Rápido', layout='centered')

# Inicializar estado de la sesión con preguntas y orden aleatorio
if 'questions' not in st.session_state:
    excel_path = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(excel_path).dropna(subset=['Pregunta'])
    df = df.sample(frac=1).reset_index(drop=True)
    qs = []
    for _, row in df.iterrows():
        opts = [row[c] for c in df.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except Exception:
            correct = None
        random.shuffle(opts)
        qs.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    st.session_state.questions = qs
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.feedback = ''
    st.session_state.answered = [False] * len(qs)
    st.session_state.selections = [None] * len(qs)

questions = st.session_state.questions
n = len(questions)
idx = st.session_state.current

# Funciones de interacción
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
    if idx < n - 1:
        st.session_state.current += 1
    st.session_state.feedback = ''
    if 'choice' in st.session_state:
        del st.session_state.choice


def go_prev():
    if idx > 0:
        st.session_state.current -= 1
    st.session_state.feedback = ''
    if 'choice' in st.session_state:
        del st.session_state.choice

# Cálculo de aciertos y fallos
correct_count = st.session_state.score
answered_total = sum(st.session_state.answered)
wrong_count = answered_total - correct_count

# Interfaz principal
st.title('🚀 Quiz Rápido')
if idx < n:
    q = questions[idx]
    st.write(f'Pregunta {idx+1} de {n} | Aciertos: {correct_count} | Errores: {wrong_count}')
    st.markdown(f"**{q['pregunta']}**")
    st.radio('Opciones:', q['opciones'], key='choice')

    cols = st.columns(3)
    with cols[0]:
        cols[0].button('⬅ Anterior', on_click=go_prev, disabled=idx==0)
    with cols[1]:
        cols[1].button('✔ Comprobar', on_click=check, disabled=st.session_state.answered[idx])
    with cols[2]:
        cols[2].button('➡ Siguiente', on_click=go_next, disabled=not st.session_state.answered[idx])

    if st.session_state.feedback:
        if 'Correcto' in st.session_state.feedback:
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)
else:
    # Pantalla de resultados
    st.header('🎉 Resultado Final')
    st.write(f'Has acertado **{correct_count}** de **{n}** preguntas y fallado **{wrong_count}**.')
    if correct_count == n:
        st.balloons()
    if st.button('🔄 Reiniciar'):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
