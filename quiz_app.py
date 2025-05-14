import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Quiz de Preguntas",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🎯 Quiz de Preguntas Aleatorio")
st.markdown("Bienvenido al quiz. Las preguntas y las opciones se barajarán para cada sesión.")

# Carga del Excel desde el repositorio
excel_path = Path(__file__).parent / "Quizz Completo.xlsx"
if not excel_path.exists():
    st.error(f"No encuentro el archivo `{excel_path.name}` en el directorio del proyecto.")
    st.stop()

# Carga y barajado de preguntas
df = pd.read_excel(excel_path).dropna(subset=["Pregunta"])
df = df.sample(frac=1, random_state=None).reset_index(drop=True)

total_preguntas = len(df)

# Iniciar puntuación
if 'score' not in st.session_state:
    st.session_state.score = 0

# Barra lateral con progreso
st.sidebar.header("Progreso")
st.sidebar.write(f"Preguntas respondidas: {st.session_state.get('score', 0)} / {total_preguntas}")
st.sidebar.progress(st.session_state.get('score', 0) / total_preguntas if total_preguntas else 0)

# Mostrar cada pregunta en un expander
for idx, row in df.iterrows():
    with st.expander(f"Pregunta {idx+1} de {total_preguntas}", expanded=False):
        st.write(row["Pregunta"])
        # Preparar opciones y respuesta correcta
        opciones = [row[col] for col in df.columns if col.startswith("Opción")]
        correcto = opciones[int(row.get("Resp.", 1)) - 1]
        random.shuffle(opciones)
        # Selector de opción
        respuesta_usuario = st.radio("Elige una opción:", opciones, key=f"opt_{idx}")
        # Botón de envío
        if st.button("Enviar respuesta", key=f"btn_{idx}"):
            if respuesta_usuario == correcto:
                st.success("¡Correcto! 🎉")
                st.session_state.score += 1
            else:
                st.error(f"Incorrecto. La respuesta correcta es: **{correcto}**")

# Resultado final y celebración
st.markdown("---")
st.header("🏁 Resultado final")
st.write(f"Has acertado **{st.session_state.score}** de **{total_preguntas}** preguntas.")
if st.session_state.score == total_preguntas:
    st.balloons()
