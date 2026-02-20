"""
Autenticacao simples para o Sistema Pedagogico ELO 2026.
Usa st.secrets para armazenar credenciais (seguro no Streamlit Cloud).

Senhas armazenadas como SHA-256 hex digest.
Fallback para plaintext garante retrocompatibilidade.
Suporte a variaveis de ambiente ELO_PASS_{USUARIO} para override.
"""

import hashlib
import hmac
import os
import streamlit as st

# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def _hash_password(password: str) -> str:
    """Gera SHA-256 hex digest de uma senha."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _is_sha256_hex(value: str) -> bool:
    """Verifica se uma string parece ser um hash SHA-256 (64 hex chars)."""
    return len(value) == 64 and all(c in "0123456789abcdef" for c in value)


# ---------------------------------------------------------------------------
# Usuarios — senhas em SHA-256
# ---------------------------------------------------------------------------

_FALLBACK_USERS = {
    "bruna": {
        "password_hash": _hash_password("EloAdmin2026!"),
        "password": "EloAdmin2026!",          # plaintext fallback
        "name": "Bruna",
        "unit": "BV",
        "role": "admin",
    },
    "admin": {
        "password_hash": _hash_password("EloAdmin2026!"),
        "password": "EloAdmin2026!",
        "name": "Administrador",
        "unit": None,
        "role": "admin",
    },
    "bv": {
        "password_hash": _hash_password("EloBV2026"),
        "password": "EloBV2026",
        "name": "Boa Viagem",
        "unit": "BV",
        "role": "coordenador",
    },
    "candeias": {
        "password_hash": _hash_password("EloCD2026"),
        "password": "EloCD2026",
        "name": "Candeias",
        "unit": "CD",
        "role": "coordenador",
    },
    "janga": {
        "password_hash": _hash_password("EloJG2026"),
        "password": "EloJG2026",
        "name": "Janga",
        "unit": "JG",
        "role": "coordenador",
    },
    "cordeiro": {
        "password_hash": _hash_password("EloCDR2026"),
        "password": "EloCDR2026",
        "name": "Cordeiro",
        "unit": "CDR",
        "role": "coordenador",
    },
}

# Cache de senhas alteradas em runtime (persiste apenas na sessao do processo)
_RUNTIME_PASSWORD_OVERRIDES: dict[str, str] = {}  # usuario -> password_hash

# ---------------------------------------------------------------------------
# Resolucao de usuarios
# ---------------------------------------------------------------------------

def _get_users():
    """Retorna dict de usuarios. Tenta st.secrets, fallback para hardcoded."""
    try:
        return st.secrets["credentials"]["usernames"]
    except (KeyError, FileNotFoundError, Exception):
        return _FALLBACK_USERS


def _resolve_password_hash(username: str) -> tuple[str | None, str]:
    """
    Resolve o hash da senha para um usuario, com prioridade:
      1. Override em runtime (via alterar_senha)
      2. Variavel de ambiente ELO_PASS_{USUARIO}  (valor = plaintext -> hasheia)
      3. Campo password_hash do dict de usuarios
      4. Campo password (plaintext legacy) -> hasheia
    Retorna (SHA-256 hex digest ou None, fonte).
    Fonte pode ser: "runtime", "env", "hash", "legacy", "none".
    """
    # 1. Runtime override
    if username in _RUNTIME_PASSWORD_OVERRIDES:
        return _RUNTIME_PASSWORD_OVERRIDES[username], "runtime"

    # 2. Variavel de ambiente
    env_key = f"ELO_PASS_{username.upper()}"
    env_val = os.environ.get(env_key)
    if env_val:
        return _hash_password(env_val), "env"

    # 3/4. Dict de usuarios
    users = _get_users()
    if username not in users:
        return None, "none"

    user = users[username]

    # 3. Hash armazenado
    if "password_hash" in user:
        return user["password_hash"], "hash"

    # 4. Plaintext legacy -> hash on the fly
    if "password" in user:
        return _hash_password(user["password"]), "legacy"

    return None, "none"


# ---------------------------------------------------------------------------
# Validacao
# ---------------------------------------------------------------------------

def _validate_credentials(username: str, password: str) -> bool:
    """
    Valida credenciais. Aceita:
      - Hash SHA-256 armazenado (preferencial)
      - Plaintext fallback se nao houver hash e sem override ativo
      - Override por env var ELO_PASS_{USUARIO}
      - Override por alterar_senha() em runtime
    """
    users = _get_users()
    if username not in users:
        return False

    expected_hash, source = _resolve_password_hash(username)
    if expected_hash is None:
        return False

    # Compara o hash da senha digitada com o hash esperado
    input_hash = _hash_password(password)
    if hmac.compare_digest(input_hash, expected_hash):
        return True

    # Fallback final: comparacao direta plaintext SOMENTE quando a fonte
    # eh o dict de usuarios (legacy/hash). Se houver override de runtime
    # ou env var, o plaintext do dict NAO deve ser aceito.
    if source in ("legacy", "hash"):
        user = users[username]
        stored_plain = user.get("password")
        if stored_plain and not _is_sha256_hex(stored_plain):
            return hmac.compare_digest(password, stored_plain)

    return False


# ---------------------------------------------------------------------------
# Alteracao de senha (uso futuro)
# ---------------------------------------------------------------------------

def alterar_senha(usuario: str, senha_antiga: str, senha_nova: str) -> tuple[bool, str]:
    """
    Altera a senha de um usuario em runtime.

    A alteracao persiste apenas durante a execucao do processo (em memoria).
    Para persistencia permanente, integrar com banco de dados ou arquivo.

    Retorna (sucesso: bool, mensagem: str).
    """
    users = _get_users()
    if usuario not in users:
        return False, "Usuario nao encontrado."

    # Valida senha antiga
    if not _validate_credentials(usuario, senha_antiga):
        return False, "Senha atual incorreta."

    # Validacao minima da nova senha
    if len(senha_nova) < 6:
        return False, "A nova senha deve ter pelo menos 6 caracteres."

    if senha_nova == senha_antiga:
        return False, "A nova senha deve ser diferente da atual."

    # Armazena hash da nova senha em runtime
    _RUNTIME_PASSWORD_OVERRIDES[usuario] = _hash_password(senha_nova)

    return True, "Senha alterada com sucesso."


# ---------------------------------------------------------------------------
# Funcoes publicas (interface inalterada)
# ---------------------------------------------------------------------------

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


def _get_display_name(username):
    """Retorna o nome de exibicao do usuario."""
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
