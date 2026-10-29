import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

st.set_page_config(
    page_title="IoT Beat-Lab | Metrónomo Háptico",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #FF4B4B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #888;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎛️ IoT Beat-Lab: Metrónomo Háptico y Expresión Espacial</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema Multimodal Bidireccional para Producción Musical (Streamlit + Wokwi ESP32)</div>', unsafe_allow_html=True)

st.write("""
Bienvenido al centro de control de estudio. Esta aplicación conecta interfaces multimodales web (**Voz**, **Visión Artificial** y **Controles Táctiles**) 
con un entorno físico simulado en **Wokwi (ESP32)** a través del protocolo **MQTT**.
""")

col1, col2 = st.columns(2)

with col1:
    st.info("### 🎙️ Ambiente 1: Cabina de Grabación y Tempo (Voz)\n"
            "Gestiona el tempo de tu sesión (BPM) y el estado del metrónomo físico usando **comandos de voz** o controles directos.\n"
            "- **Modalidades:** Reconocimiento de Voz (Speech-to-Text), Sliders táctiles y Botones.\n"
            "- **Actuadores Wokwi:** Servomotor (Golpe háptico), Buzzer (Click con acento en 4/4) y Anillo LED NeoPixel.")

with col2:
    st.success("### 🖐️ Ambiente 2: Expresión Espacial y Visualizador (Visión + Sensores)\n"
               "Modula parámetros visuales y el color de iluminación del estudio capturando **gestos o color con tu cámara web**, combinados en tiempo real con **sensores físicos desde Wokwi**.\n"
               "- **Modalidades:** Cámara Web (Visión por Computador) + Sensores Hardware (Ultrasónico HC-SR04 y Potenciómetro).\n"
               "- **Bidireccionalidad:** La cámara altera el hardware en Wokwi, y los sensores de Wokwi deforman el sintetizador gráfico en pantalla.")

st.divider()

st.subheader("📡 Configuración del Enlace MQTT")
st.markdown("""
| Parámetro | Valor Configurado | Descripción |
| :--- | :--- | :--- |
| **Broker MQTT** | `broker.mqttdashboard.com` | Servidor público de baja latencia (Puerto TCP: `1883`) |
| **Topic BPM (Pub)** | `studio_multimodal_jp/bpm` | Envía el valor entero del Tempo (40 - 240 BPM) hacia Wokwi |
| **Topic Modo (Pub)** | `studio_multimodal_jp/mode` | Controla el estado de reproducción (`PLAY` / `STOP`) |
| **Topic Color (Pub)** | `studio_multimodal_jp/color` | Envía códigos HEX desde el análisis de visión hacia el anillo NeoPixel |
| **Topic Sensores (Sub)** | `studio_multimodal_jp/sensors` | Recibe JSON desde el ESP32 con distancia ultrasónica, potenciómetro y estado del botón |
""")

st.sidebar.title("Navegación de Ambientes")
st.sidebar.info("Selecciona uno de los dos ambientes en el menú superior izquierdo para interactuar con el ESP32 en Wokwi.")
