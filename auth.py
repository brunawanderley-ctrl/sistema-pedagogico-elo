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


def _validate_credentials(username, password):
    """Valida credenciais contra st.secrets."""
    try:
        users = st.secrets["credentials"]["usernames"]
        if username in users:
            stored_password = users[username]["password"]
            return hmac.compare_digest(password, stored_password)
    except (KeyError, FileNotFoundError):
        st.error("Credenciais nao configuradas. Configure .streamlit/secrets.toml ou Streamlit Cloud Secrets.")
        return False
    return False


def _get_display_name(username):
    """Retorna o nome de exibição do usuário."""
    try:
        return st.secrets["credentials"]["usernames"][username]["name"]
    except (KeyError, FileNotFoundError):
        return username


def get_user_unit():
    """
    Retorna a unidade padrao do usuario logado.
    Lê de st.secrets[credentials][usernames][user][unit].
    Retorna None se nao configurado.
    """
    username = st.session_state.get("username")
    if not username:
        return None
    try:
        return st.secrets["credentials"]["usernames"][username].get("unit")
    except (KeyError, FileNotFoundError, AttributeError):
        return None


def get_user_role():
    """
    Retorna o perfil do usuario logado (admin, coordenador, diretor).
    Lê de st.secrets[credentials][usernames][user][role].
    Retorna 'viewer' se nao configurado.
    """
    username = st.session_state.get("username")
    if not username:
        return 'viewer'
    try:
        return st.secrets["credentials"]["usernames"][username].get("role", "viewer")
    except (KeyError, FileNotFoundError, AttributeError):
        return 'viewer'


def logout_button():
    """Mostra botao de logout na sidebar."""
    if st.session_state.get("authenticated"):
        nome = st.session_state.get("display_name", "Usuário")
        st.sidebar.markdown(f"👤 **{nome}**")
        if st.sidebar.button("Sair"):
            st.session_state.clear()
            st.rerun()
