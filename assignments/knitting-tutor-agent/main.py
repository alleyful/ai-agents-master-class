"""KnitCoach entry point for the chat-first knitting workbench."""

import streamlit as st

import ui
from common import initialize_session
from views.home import render

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
