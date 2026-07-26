import streamlit as st
import httpx
import os

# Configuración de página
st.set_page_config(
    page_title="🏛️ Panel de RAG Conversacional Privado - Demo",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar variables de entorno y API URL
API_URL = os.getenv("API_URL", "http://localhost:8080")

# Inicializar estados de sesión si no existen
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "last_chunks" not in st.session_state:
    st.session_state["last_chunks"] = []

# Título de la Aplicación
st.title("🏛️ RAG Conversacional - Gran Logia de la República de Venezuela")
st.markdown("---")

# Función para realizar login real contra la API
def perform_login(email, password):
    try:
        response = httpx.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10.0
        )
        if response.status_code == 200:
            res_data = response.json()
            st.session_state["token"] = res_data["access_token"]
            st.session_state["user_info"] = res_data["user"]
            st.success(f"Sesión iniciada exitosamente como {res_data['user']['nombre']}!")
            st.rerun()
        else:
            st.error(f"Error de autenticación ({response.status_code}): {response.json().get('detail', 'Credenciales incorrectas')}")
    except Exception as e:
        st.error(f"No se pudo conectar con el servicio de autenticación: {e}")

# Cerrar Sesión
def logout():
    st.session_state["token"] = None
    st.session_state["user_info"] = None
    st.session_state["chat_history"] = []
    st.session_state["last_chunks"] = []
    st.info("Sesión cerrada correctamente.")
    st.rerun()

# --- DISEÑO COLUMNAS PRINCIPALES ---
col_main, col_sidebar = st.columns([7, 3])

# --- BARRA LATERAL (CREDENCIALES DE DEMO Y TRANSPARENCIA) ---
with col_sidebar:
    st.header("🔑 Control de Acceso (Demo)")

    # 3 Tarjetas de usuarios de prueba con botón de login real
    st.markdown("### Seleccione un perfil para autenticación real (JWT):")

    # Tarjeta 1: Miembro Activo
    with st.container(border=True):
        st.markdown("**🟢 Miembro Activo Demo**")
        st.caption("Acceso: Público + Documentos de Miembros (Al día)")
        st.markdown("`Email: miembro.activo@demo.local`")
        if st.button("Iniciar Sesión (Activo)", key="login_activo", use_container_width=True):
            perform_login("miembro.activo@demo.local", "Demo2026!Activo")

    # Tarjeta 2: Miembro en Mora
    with st.container(border=True):
        st.markdown("**🔴 Miembro en Mora Demo (Entredicho)**")
        st.caption("Acceso: Degradado automáticamente a Público (Mora >90 días)")
        st.markdown("`Email: miembro.entredicho@demo.local`")
        if st.button("Iniciar Sesión (En Mora)", key="login_mora", use_container_width=True):
            perform_login("miembro.entredicho@demo.local", "Demo2026!Mora")

    # Tarjeta 3: Administrador
    with st.container(border=True):
        st.markdown("**🛡️ Administrador Demo**")
        st.caption("Acceso: Total (Público + Miembro + Administrador)")
        st.markdown("`Email: admin.demo@demo.local`")
        if st.button("Iniciar Sesión (Admin)", key="login_admin", use_container_width=True):
            perform_login("admin.demo@demo.local", "Demo2026!Admin")

    if st.session_state["token"]:
        st.markdown("---")
        st.button("🔴 Cerrar Sesión", on_click=logout, use_container_width=True)

    # --- PANEL DE TRANSPARENCIA RAG ---
    st.header("🔍 Transparencia RAG")
    if st.session_state["last_chunks"]:
        st.markdown(f"**{len(st.session_state['last_chunks'])} fragmentos autorizados recuperados en la última consulta:**")
        for i, chunk in enumerate(st.session_state["last_chunks"], 1):
            with st.expander(f"Fuente [{i}]: {chunk['documento_origen']} ({chunk['nivel_acceso'].upper()})"):
                st.write(chunk["texto"])
    else:
        st.info("Realice una consulta para inspeccionar los documentos fuente recuperados y sus niveles de acceso.")

# --- COLUMNA DE CHAT PRINCIPAL ---
with col_main:
    # Información del Usuario Autenticado
    if st.session_state["user_info"]:
        user = st.session_state["user_info"]
        rol_display = user["rol"].upper()
        estado_display = user["estado_membresia"].upper()

        # Color del badge de estado
        estado_color = ":green[ACTIVO]" if estado_display == "ACTIVO" else ":red[ENTREDICHO (MORA)]"

        st.markdown(
            f"👤 **Usuario:** {user['nombre']} | **Rol:** `{rol_display}` | **Estado de Membresía:** {estado_color}"
        )
        if estado_display == "ENTREDICHO (MORA)":
            st.error(
                "⚠️ **Aviso de Degradación por Mora:** Su cuenta tiene más de 3 meses (90 días) de mora. "
                "Según las reglas de negocio, ha sido degradado temporalmente a nivel **PÚBLICO**. "
                "Para recuperar el acceso de miembro, liquide su saldo con el tesorero."
            )
    else:
        st.markdown("👤 **Modo:** `PÚBLICO` (Anónimo - Sin Autenticación)")
        st.info("Actualmente navega con acceso Público. Solo puede consultar comunicados e información institucional de libre acceso.")

    # Panel de Chat Conversacional
    st.header("💬 Conversación con el RAG")

    # Mostrar historial de chat
    for chat in st.session_state["chat_history"]:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # Entrada de texto del usuario
    query = st.chat_input("Escriba su consulta al RAG...")

    if query:
        # Mostrar el mensaje del usuario
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state["chat_history"].append({"role": "user", "content": query})

        # Realizar llamada a la API
        headers = {}
        if st.session_state["token"]:
            headers["Authorization"] = f"Bearer {st.session_state['token']}"

        with st.spinner("Procesando consulta localmente con el motor RAG..."):
            try:
                response = httpx.post(
                    f"{API_URL}/chat/query",
                    json={"query": query},
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    res_data = response.json()
                    response_text = res_data["response"]
                    sources = res_data["sources"]

                    # Guardar fuentes para el panel de transparencia
                    st.session_state["last_chunks"] = sources

                    # Mostrar la respuesta de la IA
                    with st.chat_message("assistant"):
                        st.markdown(response_text)
                    st.session_state["chat_history"].append({"role": "assistant", "content": response_text})

                    # Actualizar estado de membresía dinámicamente si cambió o se reportó en la respuesta
                    if "estado_membresia" in res_data and st.session_state["user_info"]:
                        st.session_state["user_info"]["estado_membresia"] = res_data["estado_membresia"]

                elif response.status_code == 429:
                    st.error("⚠️ **Control de Flujo (Rate Limiter):** Demasiadas peticiones concurrentes. Por favor, espere un momento.")
                else:
                    err_msg = response.json().get("detail", "Error desconocido")
                    st.error(f"Error del servicio ({response.status_code}): {err_msg}")

            except Exception as e:
                st.error(f"Error al conectar con la API del RAG: {e}")

        st.rerun()
