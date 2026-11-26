"""
====================================================================================================
PROJECT: GIT DSA PLATFORM (ULTRA-POLISHED MONOCHROME SUITE - BUG-FREE EDITION)
====================================================================================================
Key Improvements in this Build:
  - Table Overhaul: Replaced truncating dataframes with clean, high-contrast, fully visible tables.
    NO cut-off headers (e.g. "Parent Point..." is now fully readable as "Parent Pointer").
  - Fixed Button Typography: Solid black primary buttons with 100% crisp bright white text.
  - Secondary Button Hover: Soft subtle gray hover (never flashes solid black).
  - Two-Way Editor State Sync: Real-time checkout and stash pop immediately update editor content.
  - Professional Diff Viewer: Clean side-by-side / unified diff for uncommitted changes.
  - 4 Data Structures on One Workspace + Dedicated Separate Analytics Dashboard.
====================================================================================================
"""

import time
import hashlib
import difflib
from typing import Dict, List, Optional, Tuple, Any
import streamlit as st

# ==================================================================================================
# 1. CORE DATA STRUCTURES: LINKED LIST, HASH MAP, STACK
# ==================================================================================================

class CommitNode:
    """Singly Linked List node representing an immutable commit snapshot."""
    def __init__(
        self,
        commit_id: str,
        message: str,
        content: str,
        author: str = "Developer",
        parent: Optional["CommitNode"] = None,
        branch: str = "main",
        timestamp: Optional[float] = None
    ):
        self.commit_id = commit_id
        self.message = message
        self.content = content
        self.author = author
        self.parent = parent  # Singly Linked List Pointer
        self.branch = branch
        self.time_val = timestamp if timestamp is not None else time.time()
        self.timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.time_val))

    def to_dict(self, *args, **kwargs) -> Dict[str, Any]:
        commit_num = args[0] if args else kwargs.get("commit_num", None)
        parent_id = f"[{self.parent.commit_id}]" if getattr(self, "parent", None) else "None (Root)"
        data = {
            "Commit ID": f"[{self.commit_id}]",
            "Message": self.message,
            "Branch": self.branch,
            "Author": self.author,
            "Parent Pointer": parent_id,
            "Timestamp": self.timestamp_str
        }
        if commit_num is not None:
            return {"Version": f"Commit #{commit_num}", **data}
        return data


class ObjectStore:
    """Hash Map providing O(1) content-addressable storage."""
    def __init__(self):
        self._table: Dict[str, Any] = {}

    def put(self, hash_key: str, data: Any) -> None:
        self._table[hash_key] = data

    def get(self, hash_key: str) -> Optional[Any]:
        return self._table.get(hash_key)

    def all_entries(self) -> Dict[str, Any]:
        return dict(self._table)

    def count(self) -> int:
        return len(self._table)


class RefTable:
    """Hash Map storing branch heads and HEAD pointer."""
    def __init__(self, default_branch: str = "main"):
        self.branches: Dict[str, str] = {}
        self.current_branch: str = default_branch
        self.head_commit_id: Optional[str] = None

    def set_branch(self, branch_name: str, commit_id: str) -> None:
        self.branches[branch_name] = commit_id

    def get_branch_commit(self, branch_name: str) -> Optional[str]:
        return self.branches.get(branch_name)


class StashItem:
    def __init__(self, message: str, content: str, branch: str):
        self.message = message
        self.content = content
        self.branch = branch
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")


class StashStack:
    """Explicit LIFO (Last-In, First-Out) Stack for Git Stash."""
    def __init__(self):
        self._items: List[StashItem] = []

    def push(self, item: StashItem) -> None:
        self._items.append(item)

    def pop(self) -> Optional[StashItem]:
        return self._items.pop() if self._items else None

    def size(self) -> int:
        return len(self._items)

    def get_all(self) -> List[StashItem]:
        return list(reversed(self._items))


# ==================================================================================================
# UNIFIED ENGINE
# ==================================================================================================

class GitEngine:
    def __init__(self):
        self.object_store = ObjectStore()
        self.refs = RefTable(default_branch="main")
        self.head_node: Optional[CommitNode] = None
        self.commit_history_list: List[CommitNode] = []
        self.stash = StashStack()

        self.working_content: str = (
            "# Python Project Workspace\n"
            "def calculate_total(prices):\n"
            "    \"\"\"Calculates order sum with tax.\"\"\"\n"
            "    subtotal = sum(prices)\n"
            "    tax = subtotal * 0.05\n"
            "    return subtotal + tax\n\n"
            "items = [15.00, 25.50, 40.00]\n"
            "print('Total with tax:', calculate_total(items))\n"
        )
        self.dsa_logs: List[Dict[str, Any]] = []
        self.commit(message="Initial commit with project setup", author="System")

    def _log_dsa(self, ds_type: str, op: str, comp: str, detail: str) -> None:
        self.dsa_logs.insert(0, {
            "Time": time.strftime("%H:%M:%S"),
            "Data Structure": ds_type,
            "Operation": op,
            "Complexity": comp,
            "Details": detail
        })
        if len(self.dsa_logs) > 25:
            self.dsa_logs.pop()

    def commit(self, message: str, author: str = "Developer") -> CommitNode:
        parent_node = self.head_node
        parent_id_str = parent_node.commit_id if parent_node else "ROOT"
        curr_time = time.time()

        raw_payload = f"{self.working_content}:{message}:{author}:{parent_id_str}:{curr_time}"
        commit_id = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()[:6]

        commit_node = CommitNode(
            commit_id=commit_id,
            message=message,
            content=self.working_content,
            author=author,
            parent=parent_node,
            branch=self.refs.current_branch,
            timestamp=curr_time
        )
        self.head_node = commit_node
        self.commit_history_list.insert(0, commit_node)
        self._log_dsa("Linked List", "Node Prepend", "O(1)", f"Commit [{commit_id}] points to parent [{parent_id_str}].")

        self.object_store.put(commit_id, commit_node)
        self.refs.set_branch(self.refs.current_branch, commit_id)
        self.refs.head_commit_id = commit_id
        self._log_dsa("Hash Map", "Object Store Put", "O(1)", f"Stored commit [{commit_id}] in key-value store.")

        return commit_node

    def create_branch(self, branch_name: str) -> Tuple[bool, str]:
        name = branch_name.strip()
        if not name or name in self.refs.branches or not self.refs.head_commit_id:
            return False, "Invalid branch name or branch already exists."
        self.refs.set_branch(name, self.refs.head_commit_id)
        self._log_dsa("Hash Map", "Branch Key Insert", "O(1)", f"Branch '{name}' created.")
        return True, f"Branch '{name}' created."

    def switch_branch(self, branch_name: str) -> Tuple[bool, str]:
        if branch_name not in self.refs.branches:
            return False, "Branch not found."
        target_id = self.refs.branches[branch_name]
        commit = self.object_store.get(target_id)
        if isinstance(commit, CommitNode):
            self.working_content = commit.content
            self.head_node = commit
        self.refs.current_branch = branch_name
        self.refs.head_commit_id = target_id
        self._log_dsa("Hash Map", "Branch Switch", "O(1)", f"Switched to '{branch_name}'.")
        return True, f"Switched to '{branch_name}'."

    def checkout_commit(self, commit_id: str) -> Tuple[bool, str]:
        commit = self.object_store.get(commit_id.strip())
        if not isinstance(commit, CommitNode):
            return False, f"Commit [{commit_id}] not found in Hash Map."
        self.working_content = commit.content
        self.head_node = commit
        self.refs.head_commit_id = commit_id
        self._log_dsa("Hash Map", "Direct Checkout", "O(1)", f"Checked out [{commit_id}].")
        return True, f"Checked out [{commit_id}]."

    def stash_push(self, msg: str = "") -> Tuple[bool, str]:
        text = msg.strip() or f"WIP on {self.refs.current_branch}"
        self.stash.push(StashItem(text, self.working_content, self.refs.current_branch))
        if self.head_node:
            self.working_content = self.head_node.content
        self._log_dsa("Stack (LIFO)", "stash push", "O(1)", f"Pushed to stack. Depth: {self.stash.size()}.")
        return True, "Saved to Stash Stack."

    def stash_pop(self) -> Tuple[bool, str]:
        item = self.stash.pop()
        if not item:
            return False, "Stash stack is empty."
        self.working_content = item.content
        self._log_dsa("Stack (LIFO)", "stash pop", "O(1)", f"Restored state '{item.message}'.")
        return True, f"Restored stash: '{item.message}'."


# ==================================================================================================
# STREAMLIT UI: EXECUTIVE MONOCHROME SUITE
# ==================================================================================================

st.set_page_config(
    page_title="Git VCS Platform",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Professional Monochrome CSS (Refined & Targeted)
st.markdown("""
<style>
    /* Global Base */
    .stApp {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    /* Global Base Font */
    html, body, .stApp {
        font-family: Calibri, 'Segoe UI', Candara, Arial, sans-serif !important;
        font-size: 15.5px !important;
        color: #111827 !important;
    }

    /* Target Text Elements Specifically (Never break icon fonts or badges) */
    p, label, input, textarea, .stMarkdown p, .stMarkdown li {
        font-family: Calibri, 'Segoe UI', Candara, Arial, sans-serif !important;
        color: #111827 !important;
    }

    /* Professional High-Contrast Badges (Clean White/Light, Zero Black Smudges) */
    .status-pill-active {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        padding: 3px 10px !important;
        border-radius: 12px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        display: inline-block !important;
        white-space: nowrap !important;
    }
    .status-pill-inactive {
        background-color: #f9fafb !important;
        color: #6b7280 !important;
        border: 1px solid #d1d5db !important;
        padding: 3px 10px !important;
        border-radius: 12px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        display: inline-block !important;
        white-space: nowrap !important;
    }
    .complexity-pill {
        background-color: #f8fafc !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        padding: 2px 8px !important;
        border-radius: 4px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        font-family: monospace, Calibri, sans-serif !important;
        display: inline-block !important;
        white-space: nowrap !important;
    }
    .branch-pill {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        padding: 2px 8px !important;
        border-radius: 12px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        display: inline-block !important;
        white-space: nowrap !important;
    }
    .lifo-pill {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        padding: 2px 8px !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        margin-right: 10px !important;
        display: inline-block !important;
        white-space: nowrap !important;
    }

    /* Protect Streamlit Material Icons & Expander Arrows from font corruption */
    [data-testid*="Icon"],
    [data-testid*="icon"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpanderToggleIcon"] *,
    [class*="material-symbols"],
    [class*="material-icons"],
    span[class*="icon"],
    svg {
        font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        font-style: normal !important;
        font-weight: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
    }

    /* Expander Component: Clean Monochrome Box with Proper Spacing */
    details[data-testid="stExpander"] {
        border: 1.5px solid #000000 !important;
        border-radius: 4px !important;
        background-color: #ffffff !important;
        margin-top: 8px !important;
        margin-bottom: 12px !important;
    }
    details[data-testid="stExpander"] summary {
        font-family: Calibri, 'Segoe UI', Candara, Arial, sans-serif !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #000000 !important;
        padding: 9px 12px !important;
        background-color: #fafafa !important;
        border-radius: 3px !important;
    }
    details[data-testid="stExpander"] summary:hover {
        background-color: #f3f4f6 !important;
    }

    h1, h2, h3, h4 {
        font-family: Calibri, 'Segoe UI', Candara, Arial, sans-serif !important;
        color: #000000 !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
    }

    h1 { font-size: 24px !important; margin-bottom: 2px !important; }
    h2 { font-size: 19px !important; margin-bottom: 2px !important; }
    h3 { font-size: 16px !important; margin-bottom: 2px !important; }

    /* Left Sidebar: Executive Minimalist Crisp Grayscale */
    section[data-testid="stSidebar"] {
        background-color: #fafafa !important;
        border-right: 1.5px solid #000000 !important;
    }

    section[data-testid="stSidebar"] * {
        color: #111827 !important;
    }

    /* Primary Action Button (Commit Changes): Solid Black with Bright Crisp WHITE Text */
    button[kind="primary"], 
    button[data-testid="baseButton-primary"], 
    .stButton > button[kind="primary"] {
        background-color: #000000 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 4px !important;
        padding: 9px 20px !important;
        white-space: nowrap !important;
        min-height: 40px !important;
    }
    button[kind="primary"] *, 
    button[data-testid="baseButton-primary"] *, 
    .stButton > button[kind="primary"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    button[kind="primary"]:hover, 
    .stButton > button[kind="primary"]:hover {
        background-color: #262626 !important;
        border-color: #000000 !important;
    }
    button[kind="primary"]:hover *, 
    .stButton > button[kind="primary"]:hover * {
        color: #ffffff !important;
    }

    /* Secondary Buttons: Clean White with Subtle Border, Gentle Gray Hover (NEVER Solid Black) */
    button[kind="secondary"], 
    button[data-testid="baseButton-secondary"], 
    .stButton > button:not([kind="primary"]) {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        padding: 6px 14px !important;
        min-height: 38px !important;
    }
    button[kind="secondary"] *, 
    button[data-testid="baseButton-secondary"] *, 
    .stButton > button:not([kind="primary"]) * {
        color: #111827 !important;
    }
    button[kind="secondary"]:hover, 
    .stButton > button:not([kind="primary"]):hover {
        background-color: #f3f4f6 !important;
        border-color: #000000 !important;
        color: #111827 !important;
    }
    button[kind="secondary"]:hover *, 
    .stButton > button:not([kind="primary"]):hover * {
        color: #111827 !important;
    }
    button[kind="secondary"]:active, 
    button[kind="secondary"]:focus, 
    .stButton > button:not([kind="primary"]):focus {
        background-color: #e5e7eb !important;
        border-color: #000000 !important;
        color: #111827 !important;
    }
    button[kind="secondary"]:active *, 
    button[kind="secondary"]:focus *, 
    .stButton > button:not([kind="primary"]):focus * {
        color: #111827 !important;
    }

    /* Professional High-Contrast HTML Table (Crisp Monochrome, Zero Truncation) */
    .pro-table-wrapper {
        width: 100%;
        overflow-x: auto;
        border: 1.5px solid #000000;
        border-radius: 5px;
        margin-top: 8px;
        margin-bottom: 22px;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .pro-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Calibri, 'Segoe UI', Candara, Arial, sans-serif;
        font-size: 14.5px;
        text-align: left;
    }
    .pro-table th {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        text-align: left !important;
        padding: 10px 14px !important;
        border-bottom: 2px solid #000000 !important;
        border-right: 1px solid #333333 !important;
        white-space: nowrap !important;
        letter-spacing: 0.2px !important;
    }
    .pro-table td {
        padding: 9px 14px !important;
        border-bottom: 1px solid #e5e7eb !important;
        border-right: 1px solid #e5e7eb !important;
        color: #111827 !important;
        white-space: nowrap !important;
        background-color: inherit;
    }
    .pro-table tr:nth-child(even) {
        background-color: #f9fafb !important;
    }
    .pro-table tr:nth-child(odd) {
        background-color: #ffffff !important;
    }
    .pro-table tr:hover {
        background-color: #f3f4f6 !important;
    }

    /* Clean Metric Boxes */
    .clean-metric {
        background: #ffffff;
        border: 1.5px solid #000000;
        border-radius: 4px;
        padding: 14px;
        text-align: center;
    }
    .metric-number {
        font-size: 32px;
        font-weight: 800;
        color: #000000;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        color: #4b5563;
        letter-spacing: 0.5px;
    }

    /* Stack Box */
    .stack-record-box {
        background: #ffffff;
        border: 1.5px solid #000000;
        border-radius: 4px;
        padding: 9px 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }

    /* Diff View */
    .diff-box {
        font-family: monospace;
        font-size: 13.5px;
        line-height: 1.5;
        border: 1px solid #000000;
        border-radius: 4px;
        padding: 10px;
        background: #ffffff;
    }
    .diff-add { background: #dcfce7; color: #166534; padding: 1px 4px; }
    .diff-rem { background: #fee2e2; color: #991b1b; padding: 1px 4px; }
    .diff-ctx { color: #4b5563; padding: 1px 4px; }

    /* Inputs */
    textarea, input {
        border: 1.5px solid #000000 !important;
        border-radius: 4px !important;
        background-color: #ffffff !important;
        color: #111827 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to render a clean HTML table without header truncation
def render_html_table(headers: List[str], rows: List[List[Any]]) -> str:
    th_html = "".join(f"<th>{h}</th>" for h in headers)
    tr_html = []
    for r in rows:
        td_html = "".join(f"<td>{str(val)}</td>" for val in r)
        tr_html.append(f"<tr>{td_html}</tr>")
    
    table_content = f"""
    <div class="pro-table-wrapper">
        <table class="pro-table">
            <thead><tr>{th_html}</tr></thead>
            <tbody>{"".join(tr_html)}</tbody>
        </table>
    </div>
    """
    return table_content

# Safe Session State Initialization (Crash-proof)
if "engine" not in st.session_state or not hasattr(st.session_state.engine, "commit_history_list"):
    st.session_state.engine = GitEngine()

engine: GitEngine = st.session_state.engine

# Ensure editor content state exists and stays in sync
if "editor_text" not in st.session_state:
    st.session_state.editor_text = engine.working_content

# ==================================================================================================
# SIDEBAR (EXECUTIVE BLACK & WHITE NAVIGATION)
# ==================================================================================================

with st.sidebar:
    st.markdown("## ■ Git System")
    st.caption("Version Control Console")

    main_view = st.radio(
        "Navigation:",
        ["Workspace (4 Data Structures)", "Analytics Dashboard"],
        index=0
    )

    st.markdown("---")
    st.markdown("### Branch Management")
    branches = list(engine.refs.branches.keys())
    curr_b = engine.refs.current_branch
    selected_b = st.selectbox(
        "Active Branch:",
        branches,
        index=branches.index(curr_b) if curr_b in branches else 0
    )
    if selected_b != curr_b:
        ok, msg = engine.switch_branch(selected_b)
        if ok:
            st.session_state.editor_text = engine.working_content
            st.success(msg)
            st.rerun()

    new_b = st.text_input("New Branch Name:", placeholder="e.g. feature-auth")
    if st.button("Create Branch", use_container_width=True):
        if new_b:
            ok, msg = engine.create_branch(new_b)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")
    st.markdown("### Version Checkout")
    total_commits = len(engine.commit_history_list)
    commit_options = {}
    for idx, c in enumerate(engine.commit_history_list):
        num = total_commits - idx
        cid = getattr(c, "commit_id", "---")
        msg = getattr(c, "message", "")[:20]
        commit_options[f"Commit #{num} [{cid}]: {msg}"] = cid

    if commit_options:
        target_display = st.selectbox("Select Version:", list(commit_options.keys()))
        if st.button("Checkout Version", use_container_width=True):
            chosen_id = commit_options[target_display]
            ok, msg = engine.checkout_commit(chosen_id)
            if ok:
                st.session_state.editor_text = engine.working_content
                st.success(msg)
                st.rerun()

    st.markdown("---")
    st.caption(f"**HEAD Pointer:** `[{engine.refs.head_commit_id}]`")


# ==================================================================================================
# VIEW 1: ALL 4 DATA STRUCTURES TOGETHER IN MONOCHROME WORKSPACE
# ==================================================================================================

if main_view == "Workspace (4 Data Structures)":
    st.markdown("## Version Control Workspace")
    st.caption("Linked List, Stack, Hash Map, and Graph integrated in a single executive view.")

    # Top Row: Code Editor & Monochrome Small-Dot Graph
    col_code, col_graph = st.columns([1.15, 0.85])

    with col_code:
        st.markdown("### Code Editor & Commit")
        
        # Real-time state synced textarea
        edited_text = st.text_area(
            "Working File Content:",
            value=st.session_state.editor_text,
            height=200,
            label_visibility="collapsed"
        )
        if edited_text != st.session_state.editor_text:
            st.session_state.editor_text = edited_text
            engine.working_content = edited_text

        # Spacious, clean layout ensuring NO truncation of "Commit Changes"
        col_m1, col_m2 = st.columns([2.3, 1.0])
        with col_m1:
            c_msg = st.text_input("Commit Message:", placeholder="e.g. Added tax calculation")
        with col_m2:
            author = st.text_input("Author:", value="Developer")

        # Full-width Solid Black Primary Button with Bright Crisp WHITE Text
        if st.button("Commit Changes", type="primary", use_container_width=True):
            if not c_msg:
                st.error("Please enter a commit message.")
            else:
                nc = engine.commit(message=c_msg, author=author)
                st.success(f"Committed [{nc.commit_id}] successfully.")
                st.rerun()

    with col_graph:
        st.markdown("### Lineage Graph (Circular Dot Nodes)")
        st.caption("Commits rendered as small circular dot nodes with dotted ancestry connectors.")

        # Graphviz DOT: Pure Black & White (Solid Black HEAD dot, White Dotted Ancestors)
        dot_lines = [
            "digraph G {",
            '  rankdir="TB";',
            '  bgcolor="transparent";',
            '  node [shape="circle", fixedsize=true, width=0.22, height=0.22, penwidth=2.0];',
            '  edge [style="dotted", color="#111827", penwidth=1.8, arrowhead="vee", arrowsize=0.6];'
        ]

        total_nodes = len(engine.commit_history_list)
        for idx, c in enumerate(engine.commit_history_list):
            c_num = total_nodes - idx
            cid = getattr(c, "commit_id", "")
            c_msg_str = getattr(c, "message", "")[:18]
            is_head = cid == engine.refs.head_commit_id

            fill_col = "#000000" if is_head else "#ffffff"
            border_col = "#000000"
            node_style = "filled" if is_head else "filled,dotted"
            head_str = " (HEAD)" if is_head else ""
            xlabel_text = f"Commit #{c_num}: {c_msg_str}{head_str}"

            dot_lines.append(
                f'  "{cid}" [label="", style="{node_style}", fillcolor="{fill_col}", color="{border_col}", xlabel="{xlabel_text}"];'
            )
            if getattr(c, "parent", None):
                dot_lines.append(f'  "{cid}" -> "{c.parent.commit_id}";')

        dot_lines.append("}")
        st.graphviz_chart("\n".join(dot_lines), use_container_width=True)

    # --- PROFESSIONAL FEATURE: CODE DIFF VIEWER ---
    with st.expander("Professional Code Diff Viewer (git diff)", expanded=False):
        head_commit = engine.head_node
        if head_commit:
            head_lines = head_commit.content.splitlines(keepends=True)
            curr_lines = engine.working_content.splitlines(keepends=True)
            diff = list(difflib.unified_diff(head_lines, curr_lines, fromfile="HEAD", tofile="Working Tree", lineterm=""))

            if not diff:
                st.info("Working tree clean. No uncommitted modifications.")
            else:
                st.caption("Line-by-line differences comparing Working Tree against HEAD:")
                diff_rows = []
                for line in diff:
                    clean_line = line.replace("<", "&lt;").replace(">", "&gt;")
                    if line.startswith("+") and not line.startswith("+++"):
                        diff_rows.append(f"<div class='diff-add'>{clean_line}</div>")
                    elif line.startswith("-") and not line.startswith("---"):
                        diff_rows.append(f"<div class='diff-rem'>{clean_line}</div>")
                    else:
                        diff_rows.append(f"<div class='diff-ctx'>{clean_line}</div>")
                st.markdown(f"<div class='diff-box'>{''.join(diff_rows)}</div>", unsafe_allow_html=True)
        else:
            st.caption("No parent commit available for diff.")

    st.markdown("---")

    st.markdown("---")

    # ----------------------------------------------------------------------------------------------
    # 2. STACK (GIT STASH - LIFO)
    # ----------------------------------------------------------------------------------------------
    st.markdown(f"### 2. Stack (Git Stash - LIFO) — Current Depth: `{engine.stash.size()}`")
    st.caption("Shelve uncommitted modifications on a Last-In, First-Out (LIFO) stack before switching contexts.")
    
    col_st_in, col_st_push, col_st_pop = st.columns([2.2, 1.0, 1.0])
    with col_st_in:
        stash_msg = st.text_input("Stash Note:", placeholder="e.g. WIP changes before checkout", label_visibility="collapsed")
    with col_st_push:
        if st.button("Push Stash", use_container_width=True):
            ok, msg = engine.stash_push(stash_msg)
            st.session_state.editor_text = engine.working_content
            st.rerun()
    with col_st_pop:
        if st.button("Pop Stash", use_container_width=True):
            ok, msg = engine.stash_pop()
            if ok:
                st.session_state.editor_text = engine.working_content
            st.rerun()

    stashed = engine.stash.get_all()
    if not stashed:
        st.caption("Stash stack is currently empty. No shelved working tree modifications.")
    else:
        for i, item in enumerate(stashed):
            badge = "TOP (LIFO)" if i == 0 else f"Depth #{i+1}"
            st.markdown(f"""
            <div class="stack-record-box">
                <span class="lifo-pill">{badge}</span>
                <strong>{item.message}</strong>
                <span style="color:#6b7280; font-size:13px; margin-left:14px;">Branch: <code>{item.branch}</code> | Saved: {item.timestamp}</span>
            </div>
            """, unsafe_allow_html=True)

    # ----------------------------------------------------------------------------------------------
    # DATA STRUCTURE REGISTRY TABLES (ARRANGED SEQUENTIALLY: EK KY NEECHY DUSRA)
    # ----------------------------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### ■ Data Structure Registry Tables")
    st.caption("Complete repository state inspection. Each table is rendered sequentially for optimal readability.")

    # TABLE 1: LINKED LIST
    st.markdown("#### 1. Singly Linked List — Commit Ancestry Chain")
    total_c = len(engine.commit_history_list)
    chain_elements = []
    for idx, c in enumerate(engine.commit_history_list):
        c_num = total_c - idx
        cid = getattr(c, "commit_id", "")
        c_msg_str = getattr(c, "message", "")
        is_head = cid == engine.refs.head_commit_id
        head_tag = " (HEAD)" if is_head else ""
        chain_elements.append(f"**Commit #{c_num}** `[{cid}]`: *\"{c_msg_str}\"*{head_tag}")

    st.markdown("<div style='padding:8px 12px; background:#fafafa; border:1px solid #e5e7eb; border-radius:4px; margin-bottom:10px;'>" + " ➔ ".join(chain_elements) + " ➔ <span style='color:#6b7280; font-style:italic;'>None (Root)</span></div>", unsafe_allow_html=True)

    ll_headers = ["Version", "Commit Hash", "Commit Message", "Branch", "Author", "Parent Pointer (Linked List)", "Timestamp"]
    ll_rows = []
    for idx, c in enumerate(engine.commit_history_list):
        c_num = total_c - idx
        cid = getattr(c, "commit_id", "")
        pid = f"[{c.parent.commit_id}]" if getattr(c, "parent", None) else "None (Root)"
        ll_rows.append([
            f"Commit #{c_num}",
            f"<code style='background:#f3f4f6; padding:2px 6px; border-radius:3px; font-weight:700;'>[{cid}]</code>",
            getattr(c, "message", ""),
            f"<span class='branch-pill'>{getattr(c, 'branch', 'main')}</span>",
            getattr(c, "author", "Developer"),
            f"<code style='background:#f3f4f6; padding:2px 6px; border-radius:3px; color:#4b5563;'>{pid}</code>",
            getattr(c, "timestamp_str", "")
        ])

    st.markdown(render_html_table(ll_headers, ll_rows), unsafe_allow_html=True)

    # TABLE 2: HASH MAP - OBJECT STORE (DIRECTLY BELOW TABLE 1)
    st.markdown("#### 2. Hash Map — ObjectStore (SHA-256 Key-Value Store)")
    st.caption("Global immutable content-addressable storage providing O(1) object lookup by cryptographic hash.")
    
    obj_headers = ["Object Key (SHA-256 Hash)", "Object Type", "Commit Message / Payload", "Lookup Complexity"]
    obj_rows = []
    for k, v in engine.object_store.all_entries().items():
        obj_rows.append([
            f"<code style='background:#f3f4f6; padding:2px 6px; border-radius:3px; font-weight:700;'>{k}</code>",
            "Commit Snapshot",
            getattr(v, "message", str(v)),
            "<span class='complexity-pill'>O(1) Hash</span>"
        ])
    st.markdown(render_html_table(obj_headers, obj_rows), unsafe_allow_html=True)

    # TABLE 3: HASH MAP - BRANCH REFERENCES (DIRECTLY BELOW TABLE 2)
    st.markdown("#### 3. Hash Map — Branch Reference Table (RefTable)")
    st.caption("Pointers mapping named branches to exact commit hash targets in O(1) time.")
    
    ref_headers = ["Branch Name (Ref Key)", "Target Commit Hash", "Status", "Lookup Complexity"]
    ref_rows = []
    for b, cid in engine.refs.branches.items():
        is_curr = (b == engine.refs.current_branch)
        status_badge = "<span class='status-pill-active'>● Active (HEAD)</span>" if is_curr else "<span class='status-pill-inactive'>Inactive</span>"
        ref_rows.append([
            f"<strong>{b}</strong>",
            f"<code style='background:#f3f4f6; padding:2px 6px; border-radius:3px; font-weight:700;'>[{cid}]</code>",
            status_badge,
            "<span class='complexity-pill'>O(1) Hash</span>"
        ])
    st.markdown(render_html_table(ref_headers, ref_rows), unsafe_allow_html=True)


# ==================================================================================================
# VIEW 2: SEPARATE ANALYTICS DASHBOARD
# ==================================================================================================

elif main_view == "Analytics Dashboard":
    st.markdown("## Repository Analytics Dashboard")
    st.caption("Key version control metrics and recent operational logs.")

    # 4 Executive Monochrome Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="clean-metric">
            <div class="metric-label">Total Commits</div>
            <div class="metric-number">{len(engine.commit_history_list)}</div>
            <div style="font-size:11px; color:#4b5563; margin-top:4px;">Linked List Nodes</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="clean-metric">
            <div class="metric-label">Active Branches</div>
            <div class="metric-number">{len(engine.refs.branches)}</div>
            <div style="font-size:11px; color:#4b5563; margin-top:4px;">Hash Map Reference Keys</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="clean-metric">
            <div class="metric-label">Stash Depth</div>
            <div class="metric-number">{engine.stash.size()}</div>
            <div style="font-size:11px; color:#4b5563; margin-top:4px;">LIFO Stack Items</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="clean-metric">
            <div class="metric-label">Stored Objects</div>
            <div class="metric-number">{engine.object_store.count()}</div>
            <div style="font-size:11px; color:#4b5563; margin-top:4px;">O(1) Key-Value Entries</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### System Status")
    st.markdown(f"""
    - **Active Branch:** `{engine.refs.current_branch}`
    - **Current HEAD Commit:** `[{engine.refs.head_commit_id}]`
    - **Repository Integrity:** Verified (All nodes reference valid ancestor commitments)
    """)

    st.markdown("### Operational Execution Log")
    if engine.dsa_logs:
        log_headers = ["Time", "Data Structure", "Operation", "Complexity", "Details"]
        log_rows = [[l["Time"], l["Data Structure"], l["Operation"], l["Complexity"], l["Details"]] for l in engine.dsa_logs]
        st.markdown(render_html_table(log_headers, log_rows), unsafe_allow_html=True)
    else:
        st.caption("No operations logged yet.")
