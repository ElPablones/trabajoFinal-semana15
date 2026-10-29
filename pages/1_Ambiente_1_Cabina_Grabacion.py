import streamlit as st
import paho.mqtt.client as mqtt
import json
import re
import time
import speech_recognition as sr

st.set_page_config(page_title="Ambiente 1: Cabina de Grabación", page_icon="🎙️", layout="wide")

MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
TOPIC_BPM = "studio_multimodal_jp/bpm"
TOPIC_MODE = "studio_multimodal_jp/mode"
TOPIC_SENSORS = "studio_multimodal_jp/sensors"

if "bpm" not in st.session_state:
    st.session_state.bpm = 90
if "playing" not in st.session_state:
    st.session_state.playing = True
if "hw_status" not in st.session_state:
    st.session_state.hw_status = {"dist": 120, "pot": 50, "playing": True, "bpm": 90}

def publish_mqtt(topic, message):
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(topic, str(message))
        client.disconnect()
        return True
    except Exception as e:
        st.error(f"Error de conexión MQTT: {e}")
        return False

def fetch_hardware_state():
    received = {}
    def on_message(client, userdata, msg):
        try:
            received["data"] = json.loads(msg.payload.decode())
        except Exception:
            pass
    client = mqtt.Client()
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(TOPIC_SENSORS)
        client.loop_start()
        time.sleep(0.6)
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    if "data" in received:
        st.session_state.hw_status = received["data"]

st.title("🎙️ Ambiente 1: Set de Grabación y Control de Tempo")
st.write("Controla el **Metrónomo Háptico** en Wokwi mediante **comandos de voz** o controles rápidos de sesión.")

col_voice, col_manual = st.columns([1.2, 1])

with col_voice:
    st.subheader("🗣️ Modalidad 1: Control por Voz (Manos Libres)")
    st.markdown("""
    Graba un comando de voz directo en el micrófono. Ejemplos de comandos reconocidos:
    - **"Tempo a 95"** o **"BPM 120"** (Ajusta la velocidad del servomotor y el click).
    - **"Modo Boom Bap"** (Fija automáticamente el tempo clásico a **90 BPM**).
    - **"Modo Trap"** (Fija el tempo a **140 BPM**).
    - **"Modo Reggaeton"** (Fija el tempo a **95 BPM**).
    - **"Detener"** / **"Pausa"** o **"Iniciar"** / **"Reproducir"**.
    """)

    audio_value = st.audio_input("Haz clic en el micrófono y dicta tu comando de estudio:")

    if audio_value is not None:
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_value) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language="es-ES").lower()
                st.success(f"**Comando Transcrito:** *\"{text}\"*")

                if "boom bap" in text or "boombap" in text:
                    st.session_state.bpm = 90
                    publish_mqtt(TOPIC_BPM, 90)
                    st.toast("🥁 Modo Boom Bap activado: 90 BPM enviados a Wokwi")
                elif "trap" in text:
                    st.session_state.bpm = 140
                    publish_mqtt(TOPIC_BPM, 140)
                    st.toast("🔥 Modo Melodic Trap activado: 140 BPM enviados a Wokwi")
                elif "reggaeton" in text or "reguetón" in text:
                    st.session_state.bpm = 95
                    publish_mqtt(TOPIC_BPM, 95)
                    st.toast("🌴 Modo Reggaeton activado: 95 BPM enviados a Wokwi")
                elif "detener" in text or "pausa" in text or "parar" in text:
                    st.session_state.playing = False
                    publish_mqtt(TOPIC_MODE, "STOP")
                    st.warning("⏹️ Metrónomo detenido por comando de voz.")
                elif "iniciar" in text or "reproducir" in text or "play" in text:
                    st.session_state.playing = True
                    publish_mqtt(TOPIC_MODE, "PLAY")
                    st.info("▶️ Metrónomo iniciado por comando de voz.")
                else:
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        new_bpm = int(numbers[0])
                        if 40 <= new_bpm <= 240:
                            st.session_state.bpm = new_bpm
                            publish_mqtt(TOPIC_BPM, new_bpm)
                            st.toast(f"✅ Tempo ajustado por voz a {new_bpm} BPM")
                        else:
                            st.error("El BPM debe estar entre 40 y 240.")
                    else:
                        st.warning("No se identificó un número de BPM o género válido en el comando.")
        except sr.UnknownValueError:
            st.error("No se pudo entender el audio. Intenta hablar más claro.")
        except Exception as e:
            st.error(f"Error al procesar el audio: {e}")

with col_manual:
    st.subheader("🎛️ Modalidad 2: Controles Táctiles y Presets")
    
    selected_bpm = st.slider("Ajuste Fino de Tempo (BPM):", min_value=40, max_value=240, value=st.session_state.bpm, step=1)
    if selected_bpm != st.session_state.bpm:
        st.session_state.bpm = selected_bpm
        publish_mqtt(TOPIC_BPM, selected_bpm)

    st.write("**Presets Rápidos de Producción:**")
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        if st.button("🥁 Boom Bap (90)", use_container_width=True):
            st.session_state.bpm = 90
            publish_mqtt(TOPIC_BPM, 90)
    with p_col2:
        if st.button("🎹 Lo-Fi Chill (75)", use_container_width=True):
            st.session_state.bpm = 75
            publish_mqtt(TOPIC_BPM, 75)
    with p_col3:
        if st.button("⚡ Trap (140)", use_container_width=True):
            st.session_state.bpm = 140
            publish_mqtt(TOPIC_BPM, 140)

    st.divider()
    c_play, c_stop = st.columns(2)
    with c_play:
        if st.button("▶️ PLAY (Activar Hardware)", type="primary", use_container_width=True):
            st.session_state.playing = True
            publish_mqtt(TOPIC_MODE, "PLAY")
    with c_stop:
        if st.button("⏹️ STOP (Silenciar Wokwi)", use_container_width=True):
            st.session_state.playing = False
            publish_mqtt(TOPIC_MODE, "STOP")

st.divider()
st.subheader("🔄 Estado Bidireccional desde el Hardware (Wokwi ESP32)")
if st.button("🔄 Sincronizar Estado con Wokwi"):
    fetch_hardware_state()

m1, m2, m3 = st.columns(3)
m1.metric("BPM Activo en ESP32", f"{st.session_state.hw_status.get('bpm', st.session_state.bpm)} BPM")
m2.metric("Estado del Botón Físico (Pedal)", "Reproduciendo ▶️" if st.session_state.hw_status.get('playing', True) else "En Pausa ⏹️")
m3.metric("Intervalo entre Golpes Hápticos", f"{int(60000 / max(1, st.session_state.bpm))} ms")
