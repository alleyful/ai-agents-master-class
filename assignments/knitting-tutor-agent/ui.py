"""Practical knitting-workbench visual layer for the KnitCoach Streamlit UI."""

import html

import streamlit as st

CANVAS = "#F6F4EE"
PAPER = "#FFFEFA"
INK = "#292C29"
INK_SOFT = "#6D716B"
PINE = "#26342D"
PINE_SOFT = "#33443A"
THREAD = "#C96F4E"
MOSS = "#74806A"
LINE = "#D9D8D0"

_STYLES = f"""
<style>
:root {{
  --canvas: {CANVAS};
  --paper: {PAPER};
  --ink: {INK};
  --ink-soft: {INK_SOFT};
  --pine: {PINE};
  --pine-soft: {PINE_SOFT};
  --thread: {THREAD};
  --moss: {MOSS};
  --line: {LINE};
}}

.stApp {{
  color: var(--ink);
  background-color: var(--canvas);
  background-image: linear-gradient(rgba(41,44,41,.018) 1px, transparent 1px);
  background-size: 100% 24px;
}}
.block-container {{ max-width: 1280px; padding: 1.5rem 2.25rem 8.5rem; }}
header[data-testid="stHeader"] {{ background: transparent; }}
h1, h2, h3, h4 {{ color: var(--ink); letter-spacing: -.025em; }}
p, li {{ line-height: 1.65; }}

/* Dark work rail: clearly separate navigation from the canvas. */
section[data-testid="stSidebar"] {{
  background: var(--pine);
  border-right: 1px solid #17221C;
  color: #F6F1E7;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{ padding: 1.15rem .8rem; }}
div[data-testid="stSidebarCollapseButton"] {{ opacity: 1 !important; }}
div[data-testid="stSidebarCollapseButton"] button {{
  color: #E8EEE9; background: #34463B; border: 1px solid #53645A; border-radius: 3px;
}}
div[data-testid="stExpandSidebarButton"] button {{
  color: var(--pine); background: var(--paper); border: 1px solid #C7CBC4;
  border-radius: 3px; box-shadow: 0 2px 8px rgba(31,42,35,.08);
}}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{ color: #BFC8C1; }}
.brand-mark {{ display: flex; align-items: center; gap: .7rem; padding: .1rem .35rem .75rem; }}
.brand-mark strong {{ display: block; color: #FFFCF4; font-size: 1rem; letter-spacing: -.01em; }}
.brand-mark small {{ display: block; color: #95A198; font-size: .58rem; letter-spacing: .14em; margin-top: .1rem; }}
.stitch-mark {{
  display: grid; place-items: center; width: 2rem; height: 2rem;
  border: 1px solid #607067; color: #F2B096; font: 700 .62rem/1 ui-monospace, monospace;
  background: #1E2A24;
}}
.stitched-rule {{ border-top: 1px dashed #526158; margin: .1rem .35rem .85rem; }}
.lnb-label {{
  color: #87968C !important; font: 700 .59rem/1.2 ui-monospace, monospace;
  letter-spacing: .14em; margin: 1.55rem .45rem .45rem;
}}
section[data-testid="stSidebar"] .stButton > button {{
  justify-content: flex-start; text-align: left; min-height: 2.25rem;
  padding: .42rem .65rem; border: 0; border-left: 3px solid transparent;
  border-radius: 3px; background: transparent; color: #DCE2DD;
  box-shadow: none; font-weight: 520;
}}
section[data-testid="stSidebar"] .stButton > button [data-testid="stMarkdownContainer"] {{ width: 100%; }}
section[data-testid="stSidebar"] .stButton > button p {{ width: 100%; margin: 0; text-align: left !important; }}
section[data-testid="stSidebar"] .stButton > button:hover {{
  background: var(--pine-soft); color: #FFFDF7;
}}
.st-key-lnb_new .stButton > button[kind="primary"] {{
  justify-content: center; min-height: 2.65rem; background: var(--thread);
  border-left-color: var(--thread); color: #FFF; font-weight: 700;
}}
.st-key-lnb_new .stButton > button p {{ text-align: center !important; }}
.st-key-lnb_recent {{ border-bottom: 1px solid #435148; padding-bottom: .8rem; }}
.st-key-lnb_recent .stButton > button[kind="primary"] {{
  background: #394B40; border-left-color: var(--thread); color: #FFFDF7;
}}
.st-key-lnb_tools .stButton > button {{
  color: #BFC8C1; font-size: .78rem;
}}
.st-key-lnb_tools .stButton > button[kind="primary"] {{
  background: #394B40; border-left-color: var(--thread); color: #FFFDF7;
}}
.sidebar-spacer {{ height: 1.25rem; }}
.system-status {{
  display: flex; align-items: center; gap: .45rem; color: #B7C4BA;
  font-size: .7rem; padding: .55rem .5rem .1rem;
}}
.system-status i {{ width: .42rem; height: .42rem; border-radius: 50%; background: #9EAF91; }}
.system-status.demo i {{ background: #D69872; }}

/* Empty conversation: the composer is the center of gravity. */
.st-key-empty_stage {{ min-height: calc(100vh - 5.4rem); display: flex; align-items: center; }}
.st-key-empty_stage > div {{ width: 100%; }}
.workbench-welcome {{ margin: 0 auto 1.1rem; text-align: left; }}
.workbench-welcome h1 {{ font-size: clamp(1.75rem, 3vw, 2.25rem); line-height: 1.28; margin: .45rem 0 .35rem; }}
.workbench-welcome p {{ color: var(--ink-soft); font-size: .88rem; margin: 0; }}
.eyebrow {{
  color: var(--thread); font: 750 .6rem/1.2 ui-monospace, monospace;
  letter-spacing: .14em;
}}
.st-key-empty_composer {{ width: 100%; }}
.st-key-action_shelf {{ margin-top: .75rem; }}
.shelf-label {{
  display: block; color: #858A83; font: 700 .56rem/1.2 ui-monospace, monospace;
  letter-spacing: .13em; margin: .55rem 0 .3rem;
}}
.st-key-resume_actions, .st-key-quick_actions {{ flex-wrap: wrap !important; }}
.st-key-resume_actions .stButton > button,
.st-key-quick_actions .stButton > button {{
  min-height: 1.95rem; padding: .28rem .62rem; border-radius: 3px;
  border: 1px solid #CFD0C9; background: rgba(255,255,255,.55);
  color: #555B55; box-shadow: none; font-size: .72rem; font-weight: 620;
}}
.st-key-resume_actions .stButton > button {{ border-color: #B9C1B7; color: #405146; }}
.st-key-resume_actions .stButton > button:hover,
.st-key-quick_actions .stButton > button:hover {{ border-color: var(--thread); color: #9F5036; }}

/* Technique library: deterministic chart symbols beside pre-authored lessons. */
.library-kicker {{
  display: inline-block; color: var(--thread); font: 700 .62rem/1.2 ui-monospace, monospace;
  letter-spacing: .12em; margin-top: .2rem;
}}
.tech-symbol {{
  display: grid; place-items: center; width: 7.4rem; min-height: 8.3rem;
  border: 1px solid #CCD0C8; background: #FFFEFA; color: var(--pine);
}}
.tech-symbol svg {{ width: 5.25rem; height: 5.25rem; }}
.tech-symbol span {{
  display: block; color: #747A73; font: 700 .68rem/1 ui-monospace, monospace;
  letter-spacing: .06em; margin-bottom: .7rem;
}}
.tech-symbol.compact {{ width: 4.5rem; min-height: 5.2rem; }}
.tech-symbol.compact svg {{ width: 3.25rem; height: 3.25rem; }}
.tech-symbol.compact span {{ font-size: .58rem; margin-bottom: .35rem; }}

/* Active conversation. */
.workspace-heading {{
  display: flex; align-items: center; gap: .65rem; padding: .2rem 0 .8rem;
  border-bottom: 1px solid var(--line); margin-bottom: 1.1rem;
}}
.workspace-heading strong, .workspace-heading small {{ display: block; }}
.workspace-heading strong {{ font-size: .82rem; }}
.workspace-heading small {{ color: var(--ink-soft); font-size: .69rem; margin-top: .08rem; }}
.workspace-thread {{ width: 20px; height: 8px; border-top: 2px solid var(--thread); border-bottom: 1px solid var(--thread); transform: skewX(-20deg); }}
div[data-testid="stChatMessage"] {{ border-radius: 3px; padding: .8rem .9rem; }}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
  background: rgba(255,254,250,.6); border-left: 2px solid #D3D7CF;
}}

/* Notes and the right-side work inspector. */
div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stForm"] {{
  background: rgba(255,254,250,.9); border-color: var(--line) !important;
  border-radius: 4px !important; box-shadow: none !important;
}}
.st-key-detail_panel > div[data-testid="stVerticalBlockBorderWrapper"] {{ border-top: 3px solid var(--pine) !important; }}
.knit-tag {{
  display: inline-block; color: #52614D; background: #E7EBE3;
  border-radius: 2px; padding: .14rem .4rem; font: 700 .62rem/1.4 ui-monospace, monospace;
  letter-spacing: .03em; margin-bottom: .25rem;
}}
.dialog-note, .notice {{
  border-left: 3px solid var(--thread); background: #F5E9E3;
  padding: .7rem .85rem; color: #5D514A; font-size: .82rem; margin-bottom: .9rem;
}}
div[data-testid="stDialog"] [role="dialog"] {{ border-radius: 5px; border-top: 4px solid var(--pine); }}

/* Composer: one clean rectangular tray, with matching inner corners. */
div[data-testid="stChatInput"] {{
  overflow: hidden !important; border: 1px solid #BFC2BA !important;
  border-radius: 8px !important; background: var(--paper) !important;
  box-shadow: 0 4px 14px rgba(35,43,37,.06) !important;
}}
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] [data-baseweb="textarea"],
div[data-testid="stChatInput"] textarea {{
  border: 0 !important; border-radius: 0 !important;
  background: transparent !important; box-shadow: none !important;
}}
div[data-testid="stChatInput"] button {{
  border-radius: 0 !important; box-shadow: none !important;
}}
div[data-testid="stChatInput"]:focus-within {{
  border-color: var(--thread) !important;
  outline: 2px solid rgba(201,111,78,.16);
  outline-offset: 1px;
}}
.st-key-empty_composer div[data-testid="stChatInput"] {{ min-height: 3.85rem; }}

/* Root-level chat_input is fixed by Streamlit. Align it with the conversation. */
div[data-testid="stBottomBlockContainer"] {{
  max-width: none; padding: 2.6rem 2.25rem 1rem;
  background: linear-gradient(transparent 0, var(--canvas) 38%);
}}
div[data-testid="stBottomBlockContainer"] > div {{ max-width: 820px; margin-inline: auto; }}
[data-testid="stMain"]:has(.detail-panel-marker) div[data-testid="stBottomBlockContainer"] {{
  padding-right: calc(38% + 2.4rem);
}}
[data-testid="stMain"]:has(.detail-panel-marker) div[data-testid="stBottomBlockContainer"] > div {{
  max-width: 760px; margin-left: 0; margin-right: auto;
}}

.stButton > button, .stFormSubmitButton > button {{ border-radius: 4px; font-weight: 650; white-space: nowrap; }}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
  background: var(--thread); border-color: var(--thread);
}}

@media (max-width: 760px) {{
  .block-container {{ padding: 1rem 1rem 8rem; }}
  .st-key-empty_stage {{ min-height: calc(100vh - 4rem); align-items: flex-start; padding-top: 18vh; }}
  .st-key-empty_stage [data-testid="stHorizontalBlock"] {{ flex-direction: column; }}
  .st-key-empty_stage [data-testid="column"]:first-child,
  .st-key-empty_stage [data-testid="column"]:last-child {{ display: none; }}
  .st-key-empty_stage [data-testid="column"] {{ width: 100% !important; flex: 1 1 auto !important; }}
  .workbench-welcome h1 {{ font-size: 1.72rem; }}
  div[data-testid="stBottomBlockContainer"],
  [data-testid="stMain"]:has(.detail-panel-marker) div[data-testid="stBottomBlockContainer"] {{ padding: 2.5rem 1rem .8rem; }}
  div[data-testid="stBottomBlockContainer"] > div,
  [data-testid="stMain"]:has(.detail-panel-marker) div[data-testid="stBottomBlockContainer"] > div {{ max-width: none; margin: 0; }}
  div[data-testid="stHorizontalBlock"] {{ flex-direction: column; }}
  div[data-testid="column"] {{ width: 100% !important; flex: 1 1 auto !important; }}
}}
</style>
"""


def inject_styles() -> None:
    st.markdown(_STYLES, unsafe_allow_html=True)


def eyebrow(text: str) -> str:
    return f'<span class="eyebrow">{html.escape(text)}</span>'


def tag(text: str) -> str:
    return f'<span class="knit-tag">{html.escape(text)}</span>'
