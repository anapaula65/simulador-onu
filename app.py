# Simulador de Votaciones del Consejo de Seguridad de la ONU
# App simple para proyecto de clase (Ciencia de Datos, primer año)
# Python 3.11+ | streamlit | pandas | plotly

import random

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# CONSTANTES DEL MOTOR (se pueden ajustar aquí)
# ---------------------------------------------------------------------------

# Umbrales de alineamiento para el voto base
UMBRAL_SI = 0.7            # alineamiento > 0.7  -> Sí
UMBRAL_ABSTENCION = 0.4    # 0.4 a 0.7           -> Abstención
                            # < 0.4               -> No

# Votos a favor mínimos para aprobar (sin vetos)
VOTOS_MINIMOS = 9

# Probabilidad extra de que un miembro permanente vote No (veto)
# según el tema de la resolución. Es un factor por tema, no un modelo.
FACTOR_TEMA = {
    "Cambio climático": 0.05,
    "Cooperación económica": 0.05,
    "Protección de civiles": 0.30,
    "Derechos humanos": 0.35,
    "Seguridad internacional": 0.45,
}

# Semilla fija para que la simulación sea reproducible
# (probada para que aparezcan los tres tipos de resultado)
SEMILLA = 0

# ---------------------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------------------


@st.cache_data
def cargar_miembros():
    """Lee data/miembros.csv y devuelve los 15 miembros del Consejo."""
    return pd.read_csv("data/miembros.csv")


@st.cache_data
def cargar_afinidad():
    df = pd.read_csv("data/afinidad_real.csv")
    df.columns = df.columns.str.strip()
    afinidad = {}
    for _, row in df.iterrows():
        afinidad[(row['pais_a'], row['pais_b'])] = row['valor']
    return afinidad
# ---------------------------------------------------------------------------
# MOTOR DE SIMULACIÓN
# ---------------------------------------------------------------------------

def obtener_alineamiento(afinidad, proponente, pais):
    """Devuelve qué tan alineado está 'pais' con el proponente (0 a 1)."""
    if proponente == pais:
        return 1.0  # el proponente siempre vota a favor de su propia resolución

    # Buscar el par en los dos sentidos (la afinidad es simétrica)
    valor = afinidad.get((proponente, pais), afinidad.get((pais, proponente)))
    if valor is None:
        return 0.5  # si falta el par, se asume alineamiento neutro
    return float(valor)


def votar(alineamiento, es_permanente, tema, rng):
    """Regla base por umbrales + posible veto de un miembro permanente."""
    # 1) Voto por umbrales de alineamiento
    if alineamiento > UMBRAL_SI:
        voto = "Sí"
    elif alineamiento >= UMBRAL_ABSTENCION:
        voto = "Abstención"
    else:
        voto = "No"

    # 2) Regla de veto: un permanente que no vota "Sí" puede votar No
    #    por el tema sensible (factor de probabilidad del tema)
    if es_permanente and voto != "Sí":
        if rng.random() < FACTOR_TEMA[tema]:
            voto = "No"

    return voto


def simular(miembros, afinidad, tema, proponente):
    """Simula la votación completa y devuelve la tabla y el resultado."""
    rng = random.Random(SEMILLA)

    filas = []
    vetos = []  # países permanentes que votaron No

    for m in miembros.itertuples():
        alineamiento = obtener_alineamiento(afinidad, proponente, m.pais)
        es_permanente = m.tipo_miembro == "Permanente"
        voto = votar(alineamiento, es_permanente, tema, rng)

        # Regla de veto: permanente que vota No cuenta como veto
        if voto == "No" and m.poder_veto == "Sí":
            vetos.append(m.pais)

        filas.append(
            {
                "País": m.pais,
                "Tipo": m.tipo_miembro,
                "Región": m.region,
                "Voto": voto,
            }
        )

    tabla = pd.DataFrame(filas)
    conteo = tabla["Voto"].value_counts()
    si = int(conteo.get("Sí", 0))
    no = int(conteo.get("No", 0))
    abstencion = int(conteo.get("Abstención", 0))

    # 3) Resultado final según las reglas del Consejo
    if vetos:
        resultado = "VETADA por " + ", ".join(vetos)
        color = "red"
    elif si >= VOTOS_MINIMOS:
        resultado = "APROBADA"
        color = "green"
    else:
        faltan = VOTOS_MINIMOS - si
        resultado = f"RECHAZADA por falta de {faltan} votos"
        color = "orange"

    return tabla, resultado, color, {"Sí": si, "No": no, "Abstención": abstencion}


# ---------------------------------------------------------------------------
# INTERFAZ STREAMLIT
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Simulador Consejo de Seguridad ONU", layout="centered")

st.title("Simulador de Votaciones del Consejo de Seguridad de la ONU")
st.markdown(
    "Simula una votación ficticia entre los **15 miembros** del Consejo "
    "(5 permanentes con veto + 10 rotativos de 2024). Elige un tema y un "
    "país proponente para ver cómo votaría cada miembro."
)

miembros = cargar_miembros()
afinidad = cargar_afinidad()

# Selectores de entrada
tema = st.selectbox("Tema de la resolución", list(FACTOR_TEMA.keys()))
proponente = st.selectbox("País proponente", sorted(miembros["pais"].tolist()))

# Botón de simulación
if st.button("Simular votación"):
    tabla, resultado, color, conteo = simular(miembros, afinidad, tema, proponente)

    # Mensaje final grande con el resultado
    st.subheader("Resultado")
    st.markdown(
        f"<h1 style='text-align: center; color: {color};'>{resultado}</h1>",
        unsafe_allow_html=True,
    )

    # Tabla con los 15 países
    st.subheader("Votos de los 15 miembros")
    st.dataframe(tabla, width="stretch", hide_index=True)

    # Gráfico de barras con el conteo de votos
    st.subheader("Conteo de votos")
    df_conteo = pd.DataFrame(
        {"Voto": list(conteo.keys()), "Cantidad": list(conteo.values())}
    )
    fig = px.bar(
        df_conteo,
        x="Voto",
        y="Cantidad",
        color="Voto",
        color_discrete_map={"Sí": "green", "No": "red", "Abstención": "gray"},
        title=f"{conteo['Sí']} a favor · {conteo['No']} en contra · {conteo['Abstención']} abstenciones",
    )
    fig.update_layout(showlegend=False, yaxis_title="Número de votos")
    st.plotly_chart(fig)
else:
    st.info("Elige tema y proponente, luego pulsa **Simular votación**.")
