import streamlit as st
import paho.mqtt.client as mqtt
import numpy as np
import json
import time
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(page_title="Ambiente 2: Expresión Espacial", page_icon="🖐️", layout="wide")

MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
TOPIC_COLOR = "studio_multimodal_jp/color"
TOPIC_BPM = "studio_multimodal_jp/bpm"
TOPIC_SENSORS = "studio_multimodal_jp/sensors"

if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = {"dist": 80, "pot": 50, "playing": True, "bpm": 90}
if "detected_hex" not in st.session_state:
    st.session_state.detected_hex = "#00FF88"
if "brightness_val" not in st.session_state:
    st.session_state.brightness_val = 128

def publish_mqtt(topic, message):
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(topic, str(message))
        client.disconnect()
    except Exception as e:
        st.error(f"Error MQTT: {e}")

def read_sensors_once():
    result = {}
    def on_message(client, userdata, msg):
        try:
            result["payload"] = json.loads(msg.payload.decode())
        except Exception:
            pass
    client = mqtt.Client()
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(TOPIC_SENSORS)
        client.loop_start()
        time.sleep(0.55)
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    if "payload" in result:
        st.session_state.sensor_data = result["payload"]

st.title("🖐️ Ambiente 2: Expresión Espacial y Visualizador Sintético")
st.write("Interactúa mediante **Visión por Computador (Cámara Web)** y recibe modulaciones en tiempo real desde el **Sensor Ultrasónico y Potenciómetro en Wokwi**.")

col_cam, col_vis = st.columns([1, 1.2])

with col_cam:
    st.subheader("📷 Modalidad 1: Visión por Computador (Cámara -> Wokwi)")
    st.markdown("""
    Captura un gesto, tu mano o un objeto frente a la cámara. El algoritmo analiza la **luminosidad espacial y el color dominante** del centro de la imagen:
    1. Envía el **color dominante (HEX)** por MQTT al **Anillo LED NeoPixel** en Wokwi.
    2. Si activas el mapeo dinámico, el brillo de tu gesto modula el **BPM físico**.
    """)

    img_file = st.camera_input("Captura un gesto o filtro de color frente a la cámara:")
    map_brightness_to_bpm = st.checkbox("Mapear luminosidad de la imagen al Tempo (BPM)", value=False)

    if img_file is not None:
        image = Image.open(img_file).convert("RGB")
        img_array = np.array(image)

        h, w, _ = img_array.shape
        roi = img_array[int(h*0.25):int(h*0.75), int(w*0.25):int(w*0.75)]

        avg_r = int(np.mean(roi[:, :, 0]))
        avg_g = int(np.mean(roi[:, :, 1]))
        avg_b = int(np.mean(roi[:, :, 2]))
        brightness = int(0.299 * avg_r + 0.587 * avg_g + 0.114 * avg_b)

        hex_color = f"#{avg_r:02x}{avg_g:02x}{avg_b:02x}"
        st.session_state.detected_hex = hex_color
        st.session_state.brightness_val = brightness

        publish_mqtt(TOPIC_COLOR, hex_color)
        st.success(f"🎨 Color `{hex_color}` enviado al Anillo NeoPixel en Wokwi (Brillo: {brightness}/255)")

        if map_brightness_to_bpm:
            mapped_bpm = int(np.interp(brightness, [0, 255], [60, 180]))
            publish_mqtt(TOPIC_BPM, mapped_bpm)
            st.info(f"⚡ BPM modulado por visión a: **{mapped_bpm} BPM**")

with col_vis:
    st.subheader("🌊 Modalidad 2: Sintetizador Gráfico (Wokwi -> Streamlit)")
    st.markdown("""
    Mueve el **Sensor Ultrasónico (HC-SR04)** y el **Potenciómetro** en el simulador Wokwi:
    - **Distancia Ultrasónica (`cm`):** Controla la **Amplitud (Volumen visual)** de la onda.
    - **Potenciómetro (`%`):** Controla la **Frecuencia y Armónicos (Filtro)** del sintetizador visual.
    """)

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if st.button("📡 Leer Sensores de Wokwi Ahora", type="primary", use_container_width=True):
            read_sensors_once()
    with b_col2:
        live_poll = st.toggle("🔄 Monitoreo Continuo (Live Stream)", value=False)

    if live_poll:
        read_sensors_once()

    dist_cm = st.session_state.sensor_data.get("dist", 80)
    pot_pct = st.session_state.sensor_data.get("pot", 50)

    s1, s2, s3 = st.columns(3)
    s1.metric("Distancia Mano (HC-SR04)", f"{dist_cm} cm")
    s2.metric("Perilla de Filtro (Potenciómetro)", f"{pot_pct} %")
    s3.metric("Color Activo en Estudio", st.session_state.detected_hex)

    t = np.linspace(0, 4 * np.pi, 600)
    amplitude = np.interp(dist_cm, [2, 300], [2.5, 0.2])
    freq = np.interp(pot_pct, [0, 100], [1.0, 8.0])
    harmonic = (st.session_state.brightness_val / 255.0) * np.sin(freq * 2.5 * t)

    wave = amplitude * np.sin(freq * t + harmonic)

    fig, ax = plt.subplots(figsize=(8, 3.2), facecolor='#0E1117')
    ax.set_facecolor('#0E1117')
    ax.plot(t, wave, color=st.session_state.detected_hex, linewidth=2.5)
    ax.fill_between(t, wave, color=st.session_state.detected_hex, alpha=0.25)
    ax.set_ylim(-3.0, 3.0)
    ax.axis('off')
    st.pyplot(fig)

    if live_poll:
        time.sleep(0.5)
        st.rerun()
