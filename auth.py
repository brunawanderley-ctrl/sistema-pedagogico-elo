"""
Autenticação simples para o Sistema Pedagógico ELO 2026.
Usa st.secrets para armazenar credenciais (seguro no Streamlit Cloud).
"""

import hmac
import streamlit as st


def check_password():
    """Verifica se o usuario esta autenticado. Mostra tela de login se nao."""
    if st.session_state.get("authenticated"):
        return True

    st.markdown("### 🔐 Sistema Pedagógico ELO 2026")
    st.markdown("Faça login para acessar o sistema.")

    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        if _validate_credentials(username, password):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["display_name"] = _get_display_name(username)
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

    return False


_FALLBACK_USERS = {
    "bruna": {"password": "EloAdmin2026!", "name": "Bruna", "unit": "BV", "role": "admin"},
    "admin": {"password": "EloAdmin2026!", "name": "Administrador", "unit": None, "role": "admin"},
    "bv": {"password": "EloBV2026", "name": "Boa Viagem", "unit": "BV", "role": "coordenador"},
    "candeias": {"password": "EloCD2026", "name": "Candeias", "unit": "CD", "role": "coordenador"},
    "janga": {"password": "EloJG2026", "name": "Janga", "unit": "JG", "role": "coordenador"},
    "cordeiro": {"password": "EloCDR2026", "name": "Cordeiro", "unit": "CDR", "role": "coordenador"},
}


def _get_users():
    """Retorna dict de usuarios. Tenta st.secrets, fallback para hardcoded."""
    try:
        return st.secrets["credentials"]["usernames"]
    except (KeyError, FileNotFoundError, Exception):
        return _FALLBACK_USERS


def _validate_credentials(username, password):
    """Valida credenciais contra st.secrets ou fallback."""
    users = _get_users()
    if username in users:
        stored_password = users[username]["password"]
        return hmac.compare_digest(password, stored_password)
    return False


def _get_display_name(username):
    """Retorna o nome de exibição do usuário."""
    users = _get_users()
    if username in users:
        return users[username].get("name", username)
    return username


def get_user_unit():
    """Retorna a unidade padrao do usuario logado."""
    username = st.session_state.get("username")
    if not username:
        return None
    users = _get_users()
    if username in users:
        return users[username].get("unit")
    return None


def get_user_role():
    """Retorna o perfil do usuario logado (admin, coordenador, diretor)."""
    username = st.session_state.get("username")
    if not username:
        return 'viewer'
    users = _get_users()
    if username in users:
        return users[username].get("role", "viewer")
    return 'viewer'


def logout_button():
    """Mostra botao de logout na sidebar."""
    if st.session_state.get("authenticated"):
        nome = st.session_state.get("display_name", "Usuário")
        st.sidebar.markdown(f"👤 **{nome}**")
        if st.sidebar.button("Sair"):
            st.session_state.clear()
            st.rerun()
