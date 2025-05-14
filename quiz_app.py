import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz Rápido', layout='centered')

# Inicializar estado de la sesión con preguntas aleatorias
if 'questions' not in st.session_state:
    # Carga y baraja las preguntas
    excel_path = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(excel_path).dropna(subset=['Pregunta'])
    df = df.sample(frac=1).reset_index(drop=True)  # orden aleatorio
    qs = []
    for _, row in df.iterrows():
        opts = [row[c] for c in df.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except Exception:
            correct = None
        random.shuffle(opts)
        qs.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    # Estado inicial
    st.session_state.questions = qs
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.feedback = ''
    st.session_state.answered = [False] * len(qs)
    st.session_state.selections = [None] * len(qs)

questions = st.session_state.questions
n = len(questions)
idx = st.session_state.current

# Callbacks de botones
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

# Interfaz principal
st.title('🚀 Quiz Rápido')
if idx < n:
    q = questions[idx]
    st.write(f'Pregunta {idx+1} de {n} | Aciertos: {st.session_state.score}')
    st.markdown(f"**{q['pregunta']}**")
    # Radio para opciones
    st.radio('Opciones:', q['opciones'], key='choice')

    # Botones: Anterior, Comprobar, Siguiente
    cols = st.columns([1,1,1])
    with cols[0]:
        cols[0].button('⬅ Anterior', on_click=go_prev, disabled=idx==0)
    with cols[1]:
        cols[1].button('✔ Comprobar', on_click=check, disabled=st.session_state.answered[idx])
    with cols[2]:
        # Siguiente solo tras comprobar
        cols[2].button('➡ Siguiente', on_click=go_next, disabled=not st.session_state.answered[idx])

    # Mostrar feedback
    if st.session_state.feedback:
        if 'Correcto' in st.session_state.feedback:
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)
else:
    # Pantalla de resultados
    st.header('🎉 Resultado Final')
    st.write(f'Has acertado **{st.session_state.score}** de **{n}** preguntas.')
    if st.session_state.score == n:
        st.balloons()
    # Reiniciar
    if st.button('🔄 Reiniciar'):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
