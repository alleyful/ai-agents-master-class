"""Practical knitting-workbench visual layer for the KnitCoach Streamlit UI."""

import html

import streamlit as st

CANVAS = "#FAF7EF"
PAPER = "#FFFDF8"
INK = "#30342C"
INK_SOFT = "#6B7166"
PINE = "#4D5E48"
PINE_SOFT = "#D6DED0"
THREAD = "#D5A13B"
MOSS = "#7F8E73"
LINE = "#DDD8CD"
SAGE_RAIL = "#DDE4D7"

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
  --sage-rail: {SAGE_RAIL};
}}

.stApp {{
  color: var(--ink);
  background-color: var(--canvas);
  background-image: none;
}}
.block-container {{
  max-width: 1280px; padding: 1.5rem 2.25rem 8.5rem;
  container-type: inline-size; container-name: knit-main;
}}
header[data-testid="stHeader"] {{ background: transparent; }}
h1, h2, h3, h4 {{ color: var(--ink); letter-spacing: -.025em; }}
p, li {{ line-height: 1.65; overflow-wrap: anywhere; }}
div[data-testid="column"] {{ min-width: 0; }}

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

/* Empty conversation: journey first, then one adaptive composer. */
.st-key-empty_stage {{ min-height: auto; display: flex; align-items: flex-start; padding: 1.2vh 0 7rem; }}
.st-key-empty_stage > div {{ width: 100%; }}
.workbench-welcome {{ margin: 0 auto .65rem; text-align: left; }}
.workbench-welcome h1 {{ font-size: clamp(1.6rem, 2.6vw, 2.05rem); line-height: 1.22; margin: .3rem 0 .2rem; }}
.workbench-welcome p {{ color: var(--ink-soft); font-size: .88rem; margin: 0; }}
.journey-current {{
  display: flex; align-items: baseline; gap: .65rem; margin-top: .55rem;
  padding-left: .7rem; border-left: 3px solid var(--thread);
}}
.journey-current strong {{ color: var(--pine); font-size: .78rem; }}
.journey-current span {{ color: var(--ink-soft); font-size: .72rem; }}
.eyebrow {{
  color: var(--thread); font: 750 .6rem/1.2 ui-monospace, monospace;
  letter-spacing: .14em;
}}
.st-key-empty_composer {{ width: 100%; }}
.st-key-action_shelf {{ margin-top: .35rem; }}
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

[class*="st-key-journey_"] .stButton > button {{
  justify-content: flex-start; min-height: 3rem; padding: .38rem .5rem;
  border: 1px solid #D1D2CB; border-radius: 5px; background: rgba(255,254,250,.72);
  color: var(--ink); box-shadow: none; text-align: left; white-space: normal;
}}
[class*="st-key-journey_"] .stButton > button [data-testid="stMarkdownContainer"] {{ width: 100%; }}
[class*="st-key-journey_"] .stButton > button p {{
  width: 100%; margin: 0; text-align: left; line-height: 1.25; font-size: .69rem;
}}
[class*="st-key-journey_"] .stButton > button strong {{
  color: var(--ink); font-size: .86rem; letter-spacing: -.01em;
}}
[class*="st-key-journey_"] .stButton > button:hover {{
  border-color: var(--thread); background: #FFF9F5; color: #8E4934;
}}
[class*="st-key-journey_"] .stButton > button[kind="primary"] {{
  border-color: var(--pine); background: var(--pine); color: #DDE5DF;
}}
[class*="st-key-journey_"] .stButton > button[kind="primary"] strong {{ color: #FFFDF7; }}
.journey-flow {{
  display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
  margin: .45rem 0 .2rem; color: #969A94; font-size: .65rem;
}}
.journey-step {{
  display: inline-flex; align-items: center; min-height: 1.6rem; padding: .18rem .55rem;
  border: 1px solid #D4D5CF; border-radius: 999px; background: rgba(255,255,255,.45);
  color: #6B706A; font-weight: 650;
}}
.journey-step.current {{ border-color: var(--thread); background: #F5E6DF; color: #8E4934; }}

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

/* Chain-stitch quick view: use the same paper, ink and thread palette as the workbench. */
.st-key-chain_board > div[data-testid="stVerticalBlockBorderWrapper"] {{
  border-top: 3px solid var(--pine) !important; padding: 1rem 1rem .8rem;
  background: rgba(255,254,250,.78); box-shadow: none !important;
}}
.chain-board-kicker {{
  color: var(--thread); font: 750 .6rem/1.2 ui-monospace, monospace;
  letter-spacing: .13em;
}}
[class*="st-key-chain_card_"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
  height: 100%; overflow: hidden; padding: .7rem; border-color: #D2D3CC !important;
  background: var(--paper); transition: border-color .16s ease, transform .16s ease;
}}
[class*="st-key-chain_card_"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
  border-color: var(--thread) !important; transform: translateY(-2px);
}}
.chain-step-number {{
  display: inline-grid; place-items: center; min-width: 2rem; height: 1.4rem;
  padding: 0 .35rem; margin-bottom: .25rem; border-radius: 2px;
  background: var(--pine); color: #FFFDF7;
  font: 750 .65rem/1 ui-monospace, monospace; letter-spacing: .06em;
}}
.chain-card-title {{
  color: var(--ink); font-weight: 750; font-size: .92rem;
  margin-top: .15rem; letter-spacing: -.01em;
}}
.st-key-chain_board [data-testid="stImage"] img {{ border-radius: 2px; }}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {{ gap: .3rem; }}
div[data-testid="stTabs"] [data-baseweb="tab"] {{
  min-height: 2.35rem; padding: .4rem .75rem; border: 1px solid #D1D2CB;
  border-radius: 3px 3px 0 0; background: rgba(255,254,250,.55);
}}

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

/* Beginner project menu: visual choice comes before tools and practice. */
[class*="st-key-project_board_"] {{ margin-top: 1rem; }}
.project-board-kicker {{
  color: var(--thread); font: 750 .6rem/1.2 ui-monospace, monospace;
  letter-spacing: .13em;
}}
[class*="st-key-project_choice_"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
  height: 100%; overflow: hidden; padding: .72rem; border-color: #D3D3CB !important;
  background: #FFFEFA; transition: border-color .16s ease, transform .16s ease;
}}
[class*="st-key-project_choice_"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
  border-color: var(--thread) !important; transform: translateY(-2px);
}}
[class*="st-key-project_choice_"] [data-testid="stImage"] img {{
  aspect-ratio: 4 / 3; object-fit: cover; border-radius: 2px;
}}
[class*="st-key-project_choice_"] h4 {{ margin: .12rem 0 .2rem; font-size: .92rem; }}
[class*="st-key-project_choice_"] p {{ font-size: .7rem; line-height: 1.42; }}
[class*="st-key-project_choice_"] .stButton > button {{ width: 100%; margin-top: .15rem; }}
.st-key-selected_project_ > div[data-testid="stVerticalBlockBorderWrapper"],
[class*="st-key-selected_project_"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
  border-left: 4px solid var(--thread) !important; padding: .65rem;
}}
[class*="st-key-selected_project_"] [data-testid="stImage"] img {{
  aspect-ratio: 4 / 3; object-fit: cover; border-radius: 2px;
}}
.project-facts {{ display: flex; gap: .35rem; flex-wrap: wrap; margin: -.05rem 0 .4rem; }}
.project-facts span {{
  display: inline-flex; padding: .12rem .38rem; background: #F2EEE7; color: #6B625A;
  border-radius: 2px; font-size: .64rem; font-weight: 680;
}}

/* Compact journey expansion: two starter blocks stay above the composer. */
[class*="st-key-journey_starter_"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
  padding: .62rem .75rem !important; background: rgba(255,254,250,.72);
}}
[class*="st-key-journey_starter_"] h3 {{ margin: 0 0 .12rem; font-size: 1rem; }}
[class*="st-key-journey_starter_"] [data-testid="stCaptionContainer"] {{
  font-size: .68rem; margin-bottom: .15rem;
}}
[class*="st-key-project_board_"] {{ margin-top: .35rem; }}
[class*="st-key-compact_project_"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
  height: 100%; padding: .48rem !important; background: #FFFEFA;
}}
[class*="st-key-compact_project_"] [data-testid="stImage"] img {{
  aspect-ratio: 1 / 1; object-fit: cover; border-radius: 3px;
}}
[class*="st-key-compact_project_"] p {{ margin-bottom: .12rem; font-size: .69rem; line-height: 1.35; }}
[class*="st-key-compact_project_"] .knit-tag {{ margin-bottom: .1rem; font-size: .56rem; }}
[class*="st-key-compact_project_"] .stButton > button {{
  min-height: 1.9rem; padding: .25rem .4rem; font-size: .66rem;
}}

/* A technique appears once as a compact chip; details open in the drawer. */
[class*="st-key-technique_strip_"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
  padding: .5rem .65rem; background: #F9F7F1; border-style: dashed !important;
}}
[class*="st-key-technique_strip_"] [data-testid="stCaptionContainer"] {{ margin-bottom: -.2rem; }}
[class*="st-key-technique_chip_"] .stButton > button {{
  min-height: 1.9rem; padding: .25rem .6rem; border-radius: 999px;
  border-color: #C7CDC4; background: #FFFDF8; color: #405146; font-size: .72rem;
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
div[data-testid="stDialog"]:has(.work-detail-marker) [role="dialog"] {{
  border-top: 4px solid var(--pine); background: var(--paper); overflow-x: hidden;
}}

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
/* Root-level chat_input is fixed by Streamlit. Align it with the conversation. */
div[data-testid="stBottomBlockContainer"] {{
  max-width: none; padding: 2.6rem 2.25rem 1rem;
  background: linear-gradient(transparent 0, var(--canvas) 38%);
}}
div[data-testid="stBottomBlockContainer"] > div {{ max-width: 820px; margin-inline: auto; }}

.stButton > button, .stFormSubmitButton > button {{
  border-radius: 4px; font-weight: 650; white-space: normal; overflow-wrap: anywhere; line-height: 1.25;
}}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
  background: var(--thread); border-color: var(--thread);
}}

/* Final sage workshop direction: light rail, quiet surfaces, knitting detail only. */
section[data-testid="stSidebar"] {{
  background: var(--sage-rail); border-right: 1px solid #C9D1C4; color: var(--ink);
}}
section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] button {{
  color: #40503C !important; background: #F8F5EC !important;
  border: 1px solid #AEB9A8 !important; box-shadow: 0 2px 7px rgba(51,66,48,.1) !important;
}}
section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] button:hover {{
  color: #2F3E2C !important; background: #FFFDF8 !important; border-color: #879681 !important;
}}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{ color: #677064; }}
.brand-mark strong {{ color: #344232; font-family: ui-serif, Georgia, serif; font-size: 1.1rem; }}
.brand-mark small {{ color: #758072; }}
.stitch-mark {{ border-radius: 50%; border-color: #879582; color: #4D5E48; background: transparent; }}
.stitched-rule {{ border-top-color: #B5C0AF; }}
.lnb-label {{ color: #687565 !important; font-family: inherit; font-weight: 700; letter-spacing: .04em; }}
section[data-testid="stSidebar"] .stButton > button {{
  color: #3E493B; border-radius: 10px; min-height: 2.65rem; padding: .52rem .68rem;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{ background: rgba(255,253,248,.55); color: #344232; }}
.st-key-lnb_new .stButton > button[kind="primary"] {{
  justify-content: flex-start; text-align: left; background: var(--paper); color: #344232;
  border: 1px solid #C6CEC1; border-left: 4px solid var(--thread); font-weight: 700;
}}
.st-key-lnb_new .stButton > button p {{ text-align: left !important; }}
.st-key-lnb_recent {{ border-bottom-color: #C5CEC0; }}
.st-key-lnb_recent .stButton > button[kind="primary"],
.st-key-lnb_tools .stButton > button[kind="primary"] {{
  background: rgba(255,253,248,.72); border-left-color: var(--thread); color: #344232;
}}
.st-key-lnb_tools .stButton > button {{ color: #536050; }}
.system-status {{ color: #667262; }}
.lnb-knit-strip {{
  height: 46px; margin: 0 -.8rem -.1rem; opacity: .32; color: #64735F;
  background-image:
    linear-gradient(135deg, transparent 42%, currentColor 43% 48%, transparent 49%),
    linear-gradient(45deg, transparent 42%, currentColor 43% 48%, transparent 49%);
  background-size: 20px 20px; border-top: 1px solid #C5CEC0;
}}

/* Compact LNB: history is a quiet text list; libraries remain tactile blocks. */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{ padding: .82rem .7rem; }}
.lnb-label {{ margin: .48rem 0 .18rem !important; font-size: .7rem !important; }}
.st-key-lnb_new {{ margin-bottom: .22rem; }}
.st-key-lnb_new .stButton > button {{ min-height: 2.35rem; padding: .4rem .58rem; }}
.st-key-lnb_recent {{ margin: 0; padding: 0 0 .42rem; border-bottom: 1px solid #C5CEC0; }}
.st-key-lnb_recent [data-testid="stVerticalBlock"] {{ gap: .02rem; }}
.st-key-lnb_recent .stButton > button {{
  min-height: 1.85rem; padding: .2rem .28rem; border: 0 !important;
  border-radius: 3px; background: transparent; color: #596457;
  justify-content: flex-start; text-align: left; box-shadow: none;
}}
.st-key-lnb_recent .stButton > button p {{ text-align: left !important; }}
.st-key-lnb_recent .stButton > button[kind="primary"] {{
  background: transparent; color: #A9573E; font-weight: 760;
}}
.st-key-lnb_recent .stButton > button[kind="primary"]::after {{
  content: '›'; margin-left: auto; color: #A9573E; font-size: 1rem; line-height: 1;
}}
.st-key-lnb_recent .stButton > button:hover {{ background: rgba(255,253,248,.42); color: #344232; }}
.st-key-lnb_learning_path {{ margin: .18rem 0 .12rem; }}
.st-key-lnb_learning_path [data-testid="stVerticalBlock"] {{ gap: .24rem; }}
.st-key-lnb_tools {{ margin-top: .12rem; }}
.st-key-lnb_tools [data-testid="stVerticalBlock"] {{ gap: .28rem; }}
.st-key-lnb_tools .stButton > button {{
  min-height: 2.25rem; padding: .38rem .58rem; background: rgba(255,253,248,.62);
  border: 1px solid #C6CEC1; border-left: 3px solid #95A28F; border-radius: 6px;
  color: #465443; box-shadow: 0 1px 0 rgba(65,79,61,.04);
}}
.st-key-lnb_tools .stButton > button[kind="primary"] {{
  background: #FFFDF8; border-left-color: var(--thread); color: #A1533D;
}}
.sidebar-spacer {{ height: .55rem; }}

/* Current curated project workbench. */
.project-workbench-title {{ margin: .35rem 0 1.15rem; }}
.project-workbench-title span, .workbench-kicker {{
  display: inline-block; color: #6E5A2B; background: #F5E9C9; border-radius: 999px;
  padding: .2rem .55rem; font-size: .68rem; font-weight: 700;
}}
.project-workbench-title h2 {{ margin: .45rem 0 .12rem; font-size: 1.55rem; }}
.project-workbench-title p {{ margin: 0; color: var(--ink-soft); font-size: .8rem; }}
.project-workbench-title small {{
  display: block; margin-top: .45rem; color: #667260; font-size: .68rem;
}}
.project-phase-track {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  margin: 0 0 1.35rem; padding: .75rem 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);
}}
.project-phase {{ display: flex; gap: .55rem; min-width: 0; padding: .35rem .75rem; border-right: 1px solid var(--line); }}
.project-phase:last-child {{ border-right: 0; }}
.phase-marker {{
  display: grid; place-items: center; flex: 0 0 auto; width: 1.65rem; height: 1.65rem;
  border: 1px solid #C9C9C1; border-radius: 50%; color: #858981; font-size: .72rem;
}}
.project-phase.complete .phase-marker {{ background: #809278; border-color: #809278; color: #FFFDF8; }}
.project-phase.current .phase-marker {{ background: var(--thread); border-color: var(--thread); color: #FFFDF8; }}
.phase-copy {{ display: grid; min-width: 0; align-content: center; gap: .12rem; }}
.phase-copy strong {{ color: var(--ink); font-size: .76rem; }}
.phase-sub {{ color: var(--ink-soft); font-size: .64rem; white-space: normal; }}
.phase-bar {{ display: block; height: 3px; margin-top: .15rem; border-radius: 999px; background: #E4E1D8; overflow: hidden; }}
.phase-bar i {{ display: block; height: 100%; background: var(--thread); }}
.round-summary {{
  display: grid; gap: .28rem; margin: .9rem 0; padding: .7rem .8rem;
  border-left: 3px solid var(--moss); background: #F1F2EC; font-size: .76rem;
}}
.round-summary span {{ color: var(--ink-soft); }}
.chart-heading {{ display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; margin-bottom: .2rem; }}
.chart-heading span {{ color: var(--ink-soft); font-size: .65rem; text-align: right; }}
.project-chart {{ width: 100%; max-width: 38rem; margin: 0 auto; color: var(--ink); }}
.project-chart svg {{ display: block; width: 100%; height: auto; overflow: visible; }}
.project-chart path {{ fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
.project-chart .chart-guide {{ fill: none; stroke-width: 1; opacity: .2; }}
.project-chart .chart-branch {{ fill: none; stroke-width: 1.15; opacity: .5; }}
.project-chart .chart-complete {{ color: #7C9074; stroke: #7C9074; }}
.project-chart .chart-current {{ color: #D39A2E; stroke: #D39A2E; }}
.project-chart .chart-future {{ color: #A9AAA3; stroke: #A9AAA3; opacity: .58; }}
.project-chart .chart-center circle {{ fill: var(--paper); stroke: #3A4037; stroke-width: 1.5; }}
.project-chart .chart-center path {{ stroke: #3A4037; stroke-width: 1.25; }}
.project-chart text {{ fill: currentColor; stroke: none; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 9px; }}
.project-chart .chart-center text {{ fill: #3A4037; font-size: 10px; font-weight: 700; }}
.project-chart .chart-round-label circle {{ fill: var(--paper); stroke: currentColor; stroke-width: 1; }}
.project-chart .chart-marker circle {{ fill: var(--thread); stroke: var(--paper); stroke-width: 2; }}
.project-chart .chart-marker path {{ stroke: #6D746A; stroke-width: 1.5; }}
.mini-hat-chart {{ max-width: 42rem; }}
.mini-hat-chart .chart-round-labels text {{ font-size: 8px; font-weight: 650; }}
.mini-hat-chart .chart-section-line {{ stroke: #8B6F4D; stroke-width: 1.2; stroke-dasharray: 4 4; }}
.mini-hat-chart .chart-section-note {{ fill: #7C6348; font-size: 10px; font-weight: 700; }}
.chart-legend {{ display: flex; flex-wrap: wrap; gap: .45rem 1rem; padding-top: .5rem; border-top: 1px solid var(--line); color: var(--ink-soft); font-size: .68rem; }}
.chart-legend b {{ color: var(--ink); margin-right: .2rem; }}
.written-round {{
  display: grid; grid-template-columns: 3rem 1fr auto; gap: .7rem; align-items: start;
  padding: .48rem .55rem; border-bottom: 1px solid #E5E1D8; font-size: .75rem;
}}
.written-round.current {{ background: linear-gradient(90deg, #F7EBCB, transparent); border-left: 3px solid var(--thread); }}
.written-round span {{ color: var(--ink-soft); }}
.written-round em {{ color: #7E837A; font-style: normal; }}
.workbench-techniques {{ display: flex; align-items: center; flex-wrap: wrap; gap: .45rem; margin: .8rem 0; }}
.workbench-techniques span {{ color: var(--ink-soft); font-size: .72rem; margin-right: .2rem; }}
.workbench-techniques i {{ padding: .22rem .55rem; border: 1px solid #C9D0C4; border-radius: 999px; color: #50604C; background: #F7F8F3; font-size: .7rem; font-style: normal; }}

/* React to the usable main-column width, not only the browser viewport. */
@container knit-main (max-width: 900px) {{
  .workbench-welcome h1 {{ font-size: clamp(1.45rem, 5cqi, 1.9rem); }}
  .st-key-action_shelf div[data-testid="stHorizontalBlock"] {{ flex-wrap: wrap; }}
  .st-key-action_shelf div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
    flex: 1 1 calc(33.333% - .5rem) !important; width: auto !important; min-width: 8rem;
  }}
  div[data-testid="stHorizontalBlock"]:has(.workbench-kicker) {{ flex-direction: column; }}
  div[data-testid="stHorizontalBlock"]:has(.workbench-kicker) > div[data-testid="column"] {{
    width: 100% !important; flex: 1 1 auto !important;
  }}
  .chart-heading {{ align-items: flex-start; flex-direction: column; gap: .15rem; }}
  .chart-heading span {{ text-align: left; }}
  .workspace-heading {{ align-items: flex-start; flex-wrap: wrap; }}
  .project-workbench-title h2 {{ font-size: clamp(1.2rem, 4.2cqi, 1.5rem); }}
}}

@container knit-main (max-width: 620px) {{
  .st-key-action_shelf div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
    flex-basis: calc(50% - .4rem) !important; min-width: 7rem;
  }}
  div[data-testid="stHorizontalBlock"]:has([class*="st-key-compact_project_"]) {{ flex-direction: column; }}
  div[data-testid="stHorizontalBlock"]:has([class*="st-key-compact_project_"]) > div[data-testid="column"] {{
    width: 100% !important; flex: 1 1 auto !important;
  }}
  .journey-current {{ align-items: flex-start; flex-direction: column; gap: .1rem; }}
  .project-phase-track {{ grid-template-columns: 1fr; }}
  .project-phase {{ border-right: 0; border-bottom: 1px solid var(--line); }}
}}

@media (max-width: 760px) {{
  .block-container {{ padding: 1rem 1rem 8rem; }}
  .st-key-empty_stage {{ min-height: auto; align-items: flex-start; padding: .5rem 0 7rem; }}
  .st-key-empty_stage [data-testid="stHorizontalBlock"] {{ flex-direction: column; }}
  .st-key-empty_stage [data-testid="column"]:first-child,
  .st-key-empty_stage [data-testid="column"]:last-child {{ display: none; }}
  .st-key-empty_stage [data-testid="column"] {{ width: 100% !important; flex: 1 1 auto !important; }}
  .workbench-welcome h1 {{ font-size: 1.72rem; }}
  .journey-current {{ align-items: flex-start; flex-direction: column; gap: .12rem; }}
  .project-phase-track {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .project-phase {{ border-bottom: 1px solid var(--line); }}
  .written-round {{ grid-template-columns: 2.5rem 1fr; }}
  .written-round em {{ grid-column: 2; }}
  div[data-testid="stBottomBlockContainer"] {{ padding: 2.5rem 1rem .8rem; }}
  div[data-testid="stBottomBlockContainer"] > div {{ max-width: none; margin: 0; }}
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
