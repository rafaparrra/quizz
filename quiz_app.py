import streamlit as st
import pandas as pd
from pathlib import Path

def main():
    st.set_page_config(page_title="Quiz de Preguntas", layout="centered")
    st.title("Quiz de Preguntas")

    # Ruta al Excel en el repo
    excel_path = Path(__file__).parent / "Quizz Completo.xlsx"
    if not excel_path.exists():
        st.error(f"No encuentro el archivo {excel_path.name}")
        return

    # Carga y filtrado de preguntas
    df = pd.read_excel(excel_path).dropna(subset=["Pregunta"])
    option_cols = [col for col in df.columns if col.startswith("Opción")]
    total = len(df)

    # Inicializar puntuación
    if "score" not in st.session_state:
        st.session_state.score = 0

    # Iterar y mostrar cada pregunta
    for idx, row in df.iterrows():
        st.subheader(f"Pregunta {idx+1} de {total}")
        st.write(row["Pregunta"])

        opciones = [row[col] for col in option_cols]
        respuesta_usuario = st.radio("Selecciona una opción:", opciones, key=f"opt_{idx}")

        if st.button("Enviar respuesta", key=f"btn_{idx}"):
            # Calcula índice de la respuesta correcta (columna 'Resp.' con valores 1–4)
            try:
                correcto_index = int(row["Resp."]) - 1
                correcto = opciones[correcto_index]
            except Exception:
                st.error("Error al leer la respuesta correcta. Revisa la columna 'Resp.' en el Excel.")
                continue

            if respuesta_usuario == correcto:
                st.success("¡Correcto!")
                st.session_state.score += 1
            else:
                st.error(f"Incorrecto. La respuesta correcta es: **{correcto}**")

    # Resultado final
    st.markdown("---")
    st.write(f"**Puntuación final:** {st.session_state.score} / {total}")

if __name__ == "__main__":
    main()
