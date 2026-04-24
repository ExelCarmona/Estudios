import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Eco-Clima Guard", page_icon="./img/desastre.png", layout="wide")

# Menú de Navegación
st.sidebar.title("Eco-Clima")
opcion = st.sidebar.selectbox(
    "Navegación:",
    ["Panel de Seguridad", "Precipitaciones", "Viento y Humedad"]
)

st.sidebar.divider()
lat = st.sidebar.number_input("Latitud", value=12.1328, format="%.4f")
lon = st.sidebar.number_input("Longitud", value=-86.2504, format="%.4f")

# Obtención de datos
@st.cache_data
def obtener_datos_meteorológicos(latitude, longitude):
    vars = "precipitation,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly={vars}&timezone=auto"
    res = requests.get(url)
    data = res.json()
    
    df = pd.DataFrame({
        "Tiempo": pd.to_datetime(data["hourly"]["time"]),
        "Precipitación": data["hourly"]["precipitation"],
        "Humedad": data["hourly"]["relative_humidity_2m"],
        "Viento_Vel": data["hourly"]["wind_speed_10m"]
    })
    return df

@st.cache_data
def obtener_calidad_aire(lat, lon):
    # API de Calidad del Aire (AQI Europeo y Partículas PM2.5)
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=european_aqi,pm2_5&timezone=auto"
    res = requests.get(url).json()
    
    df_aire = pd.DataFrame({
        "Tiempo": pd.to_datetime(res["hourly"]["time"]),
        "AQI": res["hourly"]["european_aqi"],
        "PM2_5": res["hourly"]["pm2_5"]
    })
    return df_aire


df_clima = obtener_datos_meteorológicos(lat, lon)
df_aire = obtener_calidad_aire(lat, lon)


# Analizamos solo las próximas 12 horas para la seguridad inmediata
df_proximas = df_clima.head(12)
max_lluvia = np.max(df_proximas["Precipitación"].values)
max_viento = np.max(df_proximas["Viento_Vel"].values)
promedio_hum = np.mean(df_proximas["Humedad"].values)

# Renderizado de Páginas
if opcion == "Panel de Seguridad":
    st.title("Evaluación de Riesgos y Seguridad")
    
    # Evaluación de Peligro
    es_peligroso = max_viento > 50 or max_lluvia > 10
    
    if es_peligroso:
        st.error("**ALERTA DE SEGURIDAD:** Se detectan condiciones de riesgo en las próximas horas.")
    else:
        st.success("**CONDICIONES SEGURAS:** No se detectan riesgos meteorológicos extremos.")

    # Columnas de recomendaciones
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Análisis de Riesgo")
        if max_lluvia > 5:
            st.warning(f"**Lluvia Fuerte:** Máximo de {max_lluvia}mm. Riesgo de inundaciones locales.")
        if max_viento > 40:
            st.warning(f"**Viento Intenso:** {max_viento} km/h. Evite estructuras inestables o árboles.")
        if max_lluvia <= 5 and max_viento <= 40:
            st.info("No hay amenazas meteorológicas significativas activas.")

    with col2:
        st.subheader("Recomendaciones")
        # Recomendaciones de vestimenta y transporte
        if max_lluvia > 0.2:
            st.write("- **Lleva paraguas o impermeable.**")
        elif max_viento > 25:
            st.write("- **Si viajas en bicicleta o moto, extrema precauciones.**")
        elif promedio_hum > 85:
            st.write("-**Posible visibilidad reducida por neblina.**")
        if not es_peligroso:
            st.write("- **Es un buen momento para actividades al aire libre.**")
    
    with col3:
        st.subheader("Calidad del Aire")
        max_aqi = np.max(df_aire["AQI"].values)
        if max_aqi > 60:
            st.error("**Aire Contaminado**")
        elif max_aqi > 20:
            st.warning("**Calidad Moderada**")
        else:
            st.success("**Aire Limpio**")
    
    # --- FILA 2: SECCIÓN DE CALIDAD DEL AIRE (Nueva) ---
    st.subheader("Calidad del Aire Detallada")
    c_aire1, c_aire2 = st.columns([1, 2])
    
    with c_aire1:
        aqi_actual = df_aire["AQI"].iloc[0]
        st.metric("AQI Actual (Europa)", f"{aqi_actual} pts")
        st.write("**Recomendación de Salud:**")
        if aqi_actual > 60:
            st.write("Evita hacer ejercicio intenso al aire libre.")
        elif aqi_actual > 20:
            st.write("Personas sensibles deben limitar su exposición.")
        else:
            st.write("Excelente día para actividades exteriores.")

    with c_aire2:
        st.area_chart(df_aire.set_index("Tiempo")["AQI"], color="#16a34a")
    
    # --- NUEVO MÓDULO: SUGERENCIA DE SIEMBRA ---
    st.subheader("Recomdación para sembrar en el huerto")
    
    # Analizamos promedios semanales para la recomendación
    humedad_media = np.mean(df_clima["Humedad"].values)
    lluvia_total = np.sum(df_clima["Precipitación"].values)

    with st.container():
        col_plantas, col_info = st.columns([1, 1])
        
        with col_info:
            st.write(f"**Análisis del entorno:**")
            st.write(f"- Humedad promedio: {humedad_media:.1f}%")
            st.write(f"- Agua disponible (semana): {lluvia_total:.1f} mm")
        
        with col_plantas:
            # Lógica de recomendación basada en datos
            if humedad_media > 70 and lluvia_total > 15:
                categoria = "Selváticas / Tropicales"
                plantas = ["Helechos", "Bambú", "Plataneras", "Hortensias"]
                consejo = "El ambiente es húmedo y lluvioso. Ideal para plantas que aman el agua."
            elif humedad_media < 40 or lluvia_total < 5:
                categoria = "Xerófitas (Clima Seco)"
                plantas = ["Suculentas", "Cactus", "Lavanda", "Romero"]
                consejo = "Poca lluvia detectada. Opta por plantas que resistan la sequía."
            else:
                categoria = "Huerto Estándar"
                plantas = ["Tomates", "Lechugas", "Pimientos", "Rosas"]
                consejo = "Condiciones equilibradas. Casi cualquier planta de huerto prosperará aquí."

            st.markdown(f"""
            <div class="plant-card">
                <h4 style="color: #064e3b; margin-top:0;"> Recomendación: {categoria}</h4>
                <p><b>Podrías sembrar:</b> {", ".join(plantas)}</p>
                <small>{consejo}</small>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    
    # Gráfico de resumen
    st.divider()
    st.caption("Evolución de la lluvia y el viento en las próximas 12 horas")
    st.line_chart(df_proximas.set_index("Tiempo")[["Precipitación", "Viento_Vel"]])

elif opcion == "Precipitaciones":
    st.title("Control de Precipitaciones")
    total_precip = np.sum(df_clima["Precipitación"].values)
    st.metric("Acumulado Semanal", f"{total_precip:.2f} mm")
    st.area_chart(df_clima.set_index("Tiempo")["Precipitación"], color="#22c55e")

elif opcion == "Viento y Humedad":
    st.title("Viento y Humedad")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Viento Máximo", f"{np.max(df_clima['Viento_Vel'].values)} km/h")
        st.bar_chart(df_clima["Viento_Vel"], color="#16a34a")
    with c2:
        st.metric("Humedad Media", f"{np.mean(df_clima['Humedad'].values):.1f}%")
        st.line_chart(df_clima["Humedad"], color="#4ade80")