# 🎛️ IoT Beat-Lab: Metrónomo Háptico y Expresión Espacial

Aplicación web multipágina en **Streamlit** conectada bidireccionalmente por **MQTT** con un entorno físico simulado en **Wokwi (ESP32)**.

## Estructura del Repositorio para Streamlit Cloud
- `app.py`: Dashboard principal y configuración de topics MQTT.
- `pages/1_Ambiente_1_Cabina_Grabacion.py`: Ambiente 1 (Reconocimiento de Voz y Controles Táctiles -> Wokwi).
- `pages/2_Ambiente_2_Expresion_Espacial.py`: Ambiente 2 (Visión por Computador <-> Sensores HC-SR04 y Potenciómetro en Wokwi).
- `requirements.txt`: Librerías para el despliegue automático en Streamlit Cloud.
