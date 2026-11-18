# Simulador de Votaciones del Consejo de Seguridad de la ONU

Este es un producto interactivo desarrollado para el curso de Ciencia de Datos. Consiste en un simulador web que predice cómo votarían los 15 miembros del Consejo de Seguridad de la ONU (5 permanentes con veto + 10 rotativos de 2024) sobre una resolución ficticia, basándose en datos históricos reales.

## 🛠️ Tecnologías utilizadas
- **Python 3**
- **Pandas** para el procesamiento y cálculo de datos.
- **Streamlit** para la interfaz web interactiva.
- **PyArrow** para la lectura de datos en formato Parquet.

## 📊 Fuente de los Datos
Los datos utilizados son **100% reales**. Se descargaron de Hugging Face (`sam-bha/un-general-assembly-votes-2000-2023`), un dataset que contiene los registros de votación de la Asamblea General de la ONU entre los años 2000 y 2023.

## 🧠 Metodología (Ciencia de Datos)
1. **Procesamiento:** El script `procesar_datos.py` lee el archivo original en formato `.parquet` y filtra los votos de los 15 países correspondientes al Consejo de Seguridad de 2024.
2. **Cálculo de Afinidad:** Se calcula la afinidad entre cada par de países usando la fórmula estadística: 
   `(votos_de_acuerdo - votos_en_desacuerdo) / total_votos_validos`.
3. **Escalado:** El resultado (que va de -1 a 1) se escala matemáticamente a un rango de 0 a 1 usando la fórmula `(resultado + 1) / 2`, donde 1 significa alineación perfecta y 0 significa oposición total.

## ⚖️ Reglas de Simulación
- **Aprobación:** Se necesitan al menos 9 votos a favor (de 15 posibles) y ningún veto.
- **Veto:** Si cualquiera de los 5 miembros permanentes (EE.UU., Rusia, China, Francia, Reino Unido) vota "No", la resolución fracasa automáticamente.
- **Votación:** El sentido del voto de cada país se asigna según su nivel de afinidad histórica con el país proponente.

## 🚀 Cómo ejecutar el proyecto localmente
1. Clonar o descargar esta carpeta.
2. Abrir una terminal en la carpeta del proyecto.
3. Crear y activar un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
