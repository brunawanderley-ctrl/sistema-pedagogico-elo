"""
Autenticação simples para o Sistema Pedagógico ELO 2026.
Usa st.secrets para armazenar credenciais (seguro no Streamlit Cloud).
"""

import hmac
import streamlit as st


def check_password():
    """Autenticação desativada - acesso direto. Reativar quando definir quais páginas terão senha."""
    return True


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
    """Desativado - sem login, sem logout."""
    pass
