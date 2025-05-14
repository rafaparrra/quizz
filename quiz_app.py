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

# Título y descripción
st.title("🎯 Quiz de Preguntas Aleatorio")
st.markdown("Bienvenido al quiz. Las preguntas y las opciones se barajarán para cada sesión.")

# Ruta al Excel en el repositorio
excel_path = Path(__file__).parent / "Quizz Completo.xlsx"
if not excel_path.exists():
    st.error(f"No encuentro el archivo `{excel_path.name}` en el directorio.")
    st.stop()

# Lectura y barajado de preguntas
df = pd.read_excel(excel_path).dropna(subset=["Pregunta"])
df = df.sample(frac=1).reset_index(drop=True)

# Preparar datos de preguntas: texto, opciones barajadas y respuesta correcta original
question_data = []
for _, row in df.iterrows():
    # Obtener opciones no nulas
    opciones = [row[col] for col in df.columns if col.startswith("Opción") and pd.notna(row[col])]
    # Identificar la respuesta correcta antes de barajar
    try:
        correcto = opciones[int(row.get("Resp.", 1)) - 1]
    except Exception:
        correcto = None
    # Barajar opciones para mostrar
    random.shuffle(opciones)
    question_data.append((row["Pregunta"], opciones, correcto))

# Mostrar todas las preguntas en un formulario
form = st.form("quiz_form")
for i, (pregunta, opciones, _) in enumerate(question_data):
    form.write(f"**Pregunta {i+1} de {len(question_data)}:** {pregunta}")
    form.radio("", opciones, key=f"q_{i}")

# Botón único de envío al final
enviar = form.form_submit_button("Enviar todas las respuestas")

# Al enviar, calcular puntuación y mostrar resultados
if enviar:
    score = 0
    for i, (_, _, correcto) in enumerate(question_data):
        respuesta = st.session_state.get(f"q_{i}")
        if respuesta == correcto:
            score += 1
    st.markdown("---")
    st.header("🏁 Resultado final")
    st.write(f"Has acertado **{score}** de **{len(question_data)}** preguntas.")
    if score == len(question_data):
        st.balloons()
    # Botón para reiniciar la sesión (rebarajar preguntas y resetear respuestas)
    if st.button("Reiniciar Quiz"):
        # Eliminar respuestas del session_state
        for i in range(len(question_data)):
            key = f"q_{i}"
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()
