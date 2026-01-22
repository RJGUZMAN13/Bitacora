# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 09:10:02 2026

@author: rjguz
"""

import streamlit as st
import pandas as pd
import datetime
import uuid
from io import BytesIO

# --- Configuración de la página ---
st.set_page_config(page_title="Bitácora de Mantenimiento", layout="wide")

# --- Credenciales de ejemplo ---
USERS = {
    "juan": "1234",
    "admin": "adminpass"
}

# --- Simulación de base de datos temporal ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "ID", "Usuario", "Actividad", "Tipo", "Área", "Máquina", "Inicio", "Fin", "Duración (min)", "Duración (hrs)"
    ])

# --- Login y cierre de sesión ---
st.sidebar.title("Login")
if "usuario" not in st.session_state:
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    login_button = st.sidebar.button("Entrar")

    if login_button:
        if username in USERS and USERS[username] == password:
            st.session_state["usuario"] = username
            st.sidebar.success("Login exitoso ✅")
        else:
            st.sidebar.error("Usuario o contraseña incorrectos ❌")
else:
    st.sidebar.write(f"Usuario: {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

# --- Si el usuario está loggeado ---
if "usuario" in st.session_state:
    st.title(f"Bitácora de Mantenimiento - Usuario: {st.session_state['usuario']}")

    # --- Tabs para organizar ---
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Registro", "📋 Historial", "📊 Rendimiento", "📂 Descargas"])

    # --- Tab 1: Registro ---
    with tab1:
        st.subheader("Registrar Actividad")

        with st.form("actividad_form", clear_on_submit=True):
            tipo = st.selectbox("Tipo de mantenimiento", ["Autonomo", "Preventivo (maquina operando)",
                                                           "Correctivo (sin paro)", "mejora", "5s'" ])
            actividad = st.text_area("Descripción de la actividad")
            area = st.selectbox("Área de trabajo", ["Gats", "Ford", "Audi",
                                                    "BMW", "Volkswagen", "Cummins",
                                                    "Facilidades", "Otra"])
            maquina = st.text_input("Máquina / Operación")

            fecha_inicio = st.date_input("Fecha de inicio", datetime.date.today())
            hora_inicio = st.time_input("Hora de inicio", datetime.datetime.now().time())
            inicio = datetime.datetime.combine(fecha_inicio, hora_inicio)

            fecha_fin = st.date_input("Fecha de fin", fecha_inicio)
            hora_fin = st.time_input("Hora de fin", (datetime.datetime.now() + datetime.timedelta(hours=1)).time())
            fin = datetime.datetime.combine(fecha_fin, hora_fin)

            submitted = st.form_submit_button("Guardar actividad")

            if submitted:
                if fecha_inicio < datetime.date.today() or fecha_fin < datetime.date.today():
                    st.error("No puedes registrar actividades con fechas anteriores a la actual ❌")
                elif fin > inicio:
                    duracion_min = (fin - inicio).total_seconds() / 60
                    duracion_hrs = duracion_min / 60
                    unique_id = f"ACT-{uuid.uuid4().hex[:6].upper()}"
                    nueva_fila = {
                        "ID": unique_id,
                        "Usuario": st.session_state["usuario"],
                        "Actividad": actividad,
                        "Tipo": tipo,
                        "Área": area,
                        "Máquina": maquina,
                        "Inicio": inicio.strftime("%d-%m-%Y %H:%M"),
                        "Fin": fin.strftime("%d-%m-%Y %H:%M"),
                        "Duración (min)": round(duracion_min, 2),
                        "Duración (hrs)": round(duracion_hrs, 2)
                    }
                    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([nueva_fila])], ignore_index=True)
                    st.success(f"Actividad registrada ✅ | ID: {unique_id} | Duración: {round(duracion_hrs,2)} hrs")
                else:
                    st.error("La hora de fin debe ser mayor que la hora de inicio ❌")

    # --- Tab 2: Historial ---
    with tab2:
        st.subheader("Historial de actividades")

        if not st.session_state.data.empty:
            filtro_fecha = st.date_input("Selecciona una fecha para filtrar", datetime.date.today())
            df_filtrado = st.session_state.data.copy()
            df_filtrado["Fecha"] = pd.to_datetime(df_filtrado["Inicio"], format="%d-%m-%Y %H:%M").dt.date
            df_filtrado = df_filtrado[df_filtrado["Fecha"] == filtro_fecha]

            st.markdown("""
            <style>
            .card {
                background-color: #1F4E78;
                color: white;
                padding: 16px;
                margin-bottom: 14px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                font-family: 'Segoe UI', sans-serif;
                line-height: 1.6;
            }
            .card b {
                color: #ffffff;
            }
            </style>
            """, unsafe_allow_html=True)

            for idx, row in df_filtrado.iterrows():
                st.markdown(
                    f"""
                    <div class="card">
                    <b>ID:</b> {row['ID']}<br>
                    <b>Usuario:</b> {row['Usuario']}<br>
                    <b>Actividad:</b> {row['Actividad']}<br>
                    <b>Tipo:</b> {row['Tipo']}<br>
                    <b>Área:</b> {row['Área']}<br>
                    <b>Máquina:</b> {row['Máquina']}<br>
                    <b>Inicio:</b> {row['Inicio']}<br>
                    <b>Fin:</b> {row['Fin']}<br>
                    <b>Duración:</b> {row['Duración (hrs)']} hrs
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.subheader("Tabla de registros")
            st.dataframe(df_filtrado.drop(columns=["Fecha"]))

    # --- Tab 3: Rendimiento ---
    with tab3:
        st.subheader("Gráficas de productividad")
        if not st.session_state.data.empty:
            st.markdown("**Horas por tipo de mantenimiento**")
            st.bar_chart(st.session_state.data.groupby("Tipo")["Duración (hrs)"].sum())

            st.markdown("**Horas por trabajador**")
            st.bar_chart(st.session_state.data.groupby("Usuario")["Duración (hrs)"].sum())

            st.markdown("**Horas por área**")
            st.bar_chart(st.session_state.data.groupby("Área")["Duración (hrs)"].sum())

            st.markdown("**Horas por máquina**")
            st.bar_chart(st.session_state.data.groupby("Máquina")["Duración (hrs)"].sum())

            st.markdown("**Resumen ejecutivo**")
            resumen = st.session_state.data.groupby(["Usuario", "Área", "Máquina"])["Duración (hrs)"].sum().reset_index()
            st.dataframe(resumen)

    # --- Tab 4: Descargas ---
    with tab4:
        st.subheader("Descargar bitácora en Excel")

        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine="xlsxwriter")
            df.to_excel(writer, sheet_name="Bitácora", index=False)

            workbook = writer.book
            worksheet = writer.sheets["Bitácora"]

            header_format = workbook.add_format({
                "bold": True, "text_wrap": True, "valign": "top",
                "fg_color": "#1F4E78", "font_color": "white", "border": 1
            })

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 20)

            writer.close()
            return output.getvalue()

        excel_data = to_excel(st.session_state.data)
        st.download_button(
            label="📥 Descargar Excel profesional",
            data=excel_data,
            file_name="Bitacora_Mantenimiento.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )