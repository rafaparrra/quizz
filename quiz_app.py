import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Quiz Rápido', layout='centered')

@st.cache_data
def load_questions():
    excel = Path(__file__).parent / 'Quizz Completo.xlsx'
    df = pd.read_excel(excel).dropna(subset=['Pregunta'])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    qs = []
    for _, row in df.iterrows():
        opts = [row[c] for c in df.columns if c.startswith('Opción') and pd.notna(row[c])]
        try:
            correct = opts[int(row.get('Resp.', 1)) - 1]
        except:
            correct = None
        random.shuffle(opts)
        qs.append({'pregunta': row['Pregunta'], 'opciones': opts, 'correcto': correct})
    return qs

# Inicialización del estado
if 'questions' not in st.session_state:
    st.session_state.questions = load_questions()
    st.session_state.current = 0
    st.session_state.answered = [False] * len(st.session_state.questions)
    st.session_state.selections = [None] * len(st.session_state.questions)

qs = st.session_state.questions
n = len(qs)
idx = st.session_state.current

# Pantalla de Quiz
st.title('🚀 Quiz Rápido')
if idx < n:
    st.write(f'Pregunta {idx+1} de {n}   |   Aciertos: {sum(1 for i in range(n) if st.session_state.answered[i] and st.session_state.selections[i] == qs[i]["correcto"]) }')
    q = qs[idx]
    st.markdown(f"**{q['pregunta']}**")

    # Opciones con radio
    choice_key = f'choice_{idx}'
    if choice_key not in st.session_state:
        st.session_state[choice_key] = None
    st.session_state[choice_key] = st.radio('Opciones:', q['opciones'], key=choice_key)

    # Botón Comprobar
    if not st.session_state.answered[idx]:
        if st.button('✔ Comprobar'):
            st.session_state.answered[idx] = True
            st.session_state.selections[idx] = st.session_state[choice_key]
            if st.session_state.selections[idx] == q['correcto']:
                st.success('¡Correcto! 🎉')
            else:
                st.error(f'Incorrecto. Correcto: {q["correcto"]}')
    else:
        # Botón para avanzar o ver resultado
        if idx < n - 1:
            if st.button('➡ Siguiente'):
                st.session_state.current += 1
        else:
            if st.button('🏁 Ver resultado'):
                st.session_state.current += 1
else:
    # Resultado final
    score = sum(1 for i in range(n) if st.session_state.answered[i] and st.session_state.selections[i] == qs[i]['correcto'])
    st.header('🎉 Resultado Final')
    st.write(f'Has acertado **{score}** de **{n}** preguntas.')
    if score == n:
        st.balloons()
    # Reiniciar Quiz
    if st.button('🔄 Reiniciar'):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
