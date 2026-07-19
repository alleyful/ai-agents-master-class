"""KnitCoach entry point for the chat-first knitting workbench."""

import os

import streamlit as st


def _load_cloud_secrets() -> None:
    """Map Streamlit Cloud secrets to the provider environment once."""
    try:
        for key in ("OPENAI_API_KEY", "KNITCOACH_MODEL_PROVIDER", "KNITTING_AGENT_MODEL", "KNITCOACH_ROUTER_MODEL"):
            value = st.secrets.get(key)
            if value and not os.getenv(key):
                os.environ[key] = str(value)
    except (FileNotFoundError, KeyError):
        pass


_load_cloud_secrets()

import ui  # noqa: E402
from common import initialize_session  # noqa: E402
from views.home import render  # noqa: E402

st.set_page_config(
    page_title="KnitCoach",
    page_icon="🧶",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.inject_styles()


def run_app() -> None:
    initialize_session()
    render()


if __name__ == "__main__":
    run_app()
