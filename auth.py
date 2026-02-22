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
    "bruna_vitoria": {
        "password_hash": _hash_password("BrunaVitoria"),
        "password": "BrunaVitoria",
        "name": "Bruna Vitória — Coord. BV",
        "unit": "BV",
        "role": "coordenador",
    },
    "gilberto": {
        "password_hash": _hash_password("Gilberto"),
        "password": "Gilberto",
        "name": "Gilberto Santos — Coord. BV",
        "unit": "BV",
        "role": "coordenador",
    },
    "elisangela": {
        "password_hash": _hash_password("Elisangela"),
        "password": "Elisangela",
        "name": "Elisângela Luiz — Coord. CD",
        "unit": "CD",
        "role": "coordenador",
    },
    "vanessa": {
        "password_hash": _hash_password("Vanessa"),
        "password": "Vanessa",
        "name": "Vanessa — Coord. CD",
        "unit": "CD",
        "role": "coordenador",
    },
    "alline": {
        "password_hash": _hash_password("Alline"),
        "password": "Alline",
        "name": "Alline — Coord. CD",
        "unit": "CD",
        "role": "coordenador",
    },
    "lecinane": {
        "password_hash": _hash_password("Lecinane"),
        "password": "Lecinane",
        "name": "Lecinane — Coord. JG",
        "unit": "JG",
        "role": "coordenador",
    },
    "pietro": {
        "password_hash": _hash_password("Pietro"),
        "password": "Pietro",
        "name": "Pietro — Coord. JG",
        "unit": "JG",
        "role": "coordenador",
    },
    "vanessa_cdr": {
        "password_hash": _hash_password("Vanessa"),
        "password": "Vanessa",
        "name": "Vanessa Porciúncula — Coord. CDR",
        "unit": "CDR",
        "role": "coordenador",
    },
    "ana_claudia": {
        "password_hash": _hash_password("Ana"),
        "password": "Ana",
        "name": "Ana Cláudia — Coord. CDR",
        "unit": "CDR",
        "role": "coordenador",
    },
    "dir_bv": {
        "password_hash": _hash_password("Betinha"),
        "password": "Betinha",
        "name": "Betinha — Direcao Boa Viagem",
        "unit": "BV",
        "role": "diretor",
    },
    "dir_cd": {
        "password_hash": _hash_password("Ricardo"),
        "password": "Ricardo",
        "name": "Ricardo — Direcao Candeias",
        "unit": "CD",
        "role": "diretor",
    },
    "dir_jg": {
        "password_hash": _hash_password("123"),
        "password": "123",
        "name": "Direcao Janga",
        "unit": "JG",
        "role": "diretor",
    },
    "dir_cdr": {
        "password_hash": _hash_password("Emiliana"),
        "password": "Emiliana",
        "name": "Emiliana — Direcao Cordeiro",
        "unit": "CDR",
        "role": "diretor",
    },
    "dir_rede": {
        "password_hash": _hash_password("redeelo"),
        "password": "redeelo",
        "name": "Direção Rede ELO",
        "unit": None,
        "role": "diretor",
    },
    "prof_demo": {
        "password_hash": _hash_password("EloProf2026"),
        "password": "EloProf2026",
        "name": "Professor Demo",
        "unit": "BV",
        "role": "professor",
        "professor_nome": "PROFESSOR DEMONSTRACAO",
    },
}

# ---------------------------------------------------------------------------
# Roles e aliases
# ---------------------------------------------------------------------------
ROLE_CEO = 'ceo'
ROLE_DIRETOR = 'diretor'
ROLE_COORDENADOR = 'coordenador'
ROLE_PROFESSOR = 'professor'

_ROLE_ALIASES = {'admin': 'ceo'}

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


def _resolve_password_hash(username: str) -> "tuple":
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
    """Retorna o perfil do usuario logado (ceo, diretor, coordenador).
    Aplica alias: admin -> ceo."""
    username = st.session_state.get("username")
    if not username:
        return 'viewer'
    users = _get_users()
    if username in users:
        role = users[username].get("role", "viewer")
        return _ROLE_ALIASES.get(role, role)
    return 'viewer'


def is_ceo():
    """Verifica se o usuario logado tem perfil CEO."""
    return get_user_role() == ROLE_CEO


def is_diretor():
    """Verifica se o usuario logado tem perfil Diretor."""
    return get_user_role() == ROLE_DIRETOR


def is_coordenador():
    """Verifica se o usuario logado tem perfil Coordenador."""
    return get_user_role() == ROLE_COORDENADOR


def is_professor():
    """Verifica se o usuario logado tem perfil Professor."""
    return get_user_role() == ROLE_PROFESSOR


def get_professor_name():
    """Retorna o nome do professor no SIGA (para filtrar dados).
    Cada professor so ve seus proprios dados."""
    username = st.session_state.get("username")
    if not username:
        return None
    users = _get_users()
    if username in users:
        return users[username].get("professor_nome")
    return None


def get_visible_units():
    """Retorna lista de unidades visiveis para o usuario logado.
    CEO: todas | Diretor/Coordenador: apenas sua unidade."""
    from normalizacao import UNIDADES
    role = get_user_role()
    if role == ROLE_CEO:
        return list(UNIDADES)
    unit = get_user_unit()
    return [unit] if unit else list(UNIDADES)


def logout_button():
    """Mostra botao de logout na sidebar."""
    if st.session_state.get("authenticated"):
        nome = st.session_state.get("display_name", "Usuário")
        st.sidebar.markdown(f"👤 **{nome}**")
        if st.sidebar.button("Sair"):
            st.session_state.clear()
            st.rerun()
