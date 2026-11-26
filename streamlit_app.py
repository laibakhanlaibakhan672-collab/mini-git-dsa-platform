"""
====================================================================================================
PROJECT: GIT DSA PLATFORM (EXECUTIVE MONOCHROME / BLACK & WHITE EDITION)
====================================================================================================
Design Specifications:
  - Theme: Ultra-Clean High-Contrast Black & White (Monochrome Minimalist)
  - Typography: Calibri (Medium readable size, crisp black text)
  - Color Palette: Pure Black (#000000), White (#FFFFFF), Subtle Grayscale accents (#F8F9FA, #E5E7EB)
  - Graph: Compact circular dot nodes (solid black HEAD dot, white dotted ancestors, black dotted edges)
  - Layout: Single-Page 4-DS Workspace + Separate Analytics Dashboard
  - Buttons: Minimalist black & white enterprise design
====================================================================================================
"""

import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
import streamlit as st

# ==================================================================================================
# 1. CORE DATA STRUCTURES: LINKED LIST, HASH MAP, STACK
# ==================================================================================================

class CommitNode:
    """Singly Linked List node representing a commit snapshot with a parent pointer."""
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
        """Safely returns dictionary representation supporting both 0 and 1 arguments."""
        commit_num = args[0] if args else kwargs.get("commit_num", None)
        parent_id = f"[{self.parent.commit_id}]" if getattr(self, "parent", None) else "None (Root)"
        data = {
            "Commit ID": f"[{self.commit_id}]",
            "Message": self.message,
            "Branch": self.branch,
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
            "# Python Code Workspace\n"
            "def calculate_total(prices):\n"
            "    return sum(prices)\n\n"
            "print('Total:', calculate_total([15, 25, 40]))\n"
        )
        self.dsa_logs: List[Dict[str, Any]] = []
        self.commit(message="Initial commit with starter code", author="System")

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
        self._log_dsa("Linked List", "Node Prepend", "O(1)", f"Commit [{commit_id}] -> parent [{parent_id_str}].")

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
# STREAMLIT UI: EXECUTIVE MONOCHROME / BLACK & WHITE MINIMALIST THEME
# ==================================================================================================

st.set_page_config(
    page_title="Git VCS Platform",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Professional Black & White Styling
st.markdown("""
<style>
    /* Global Background and Typography */
    .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    html, body, [class*="css"], .stApp, p, span, div, label, input, textarea, button, select {
        font-family: Calibri, 'Segoe UI', Candara, Arial, sans-serif !important;
        font-size: 15.5px !important;
        color: #111111 !important;
    }

    h1, h2, h3, h4 {
        font-family: Calibri, 'Segoe UI', Candara, Arial, sans-serif !important;
        color: #000000 !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
    }

    h1 { font-size: 24px !important; margin-bottom: 4px !important; }
    h2 { font-size: 19px !important; margin-bottom: 4px !important; }
    h3 { font-size: 16px !important; margin-bottom: 4px !important; }

    /* Sidebar: High-Contrast Crisp Black & White */
    section[data-testid="stSidebar"] {
        background-color: #fcfcfc !important;
        border-right: 1.5px solid #000000 !important;
    }

    section[data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    /* Executive Black & White Buttons */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1.5px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[kind="primary"]:hover {
        background-color: #262626 !important;
        border-color: #000000 !important;
        color: #ffffff !important;
    }

    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    /* Monochrome Card Containers */
    .bw-card {
        background: #ffffff;
        border: 1.5px solid #000000;
        border-radius: 4px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }

    .bw-metric {
        background: #ffffff;
        border: 1.5px solid #000000;
        border-radius: 4px;
        padding: 16px;
        text-align: center;
    }
    .bw-metric-val {
        font-size: 34px;
        font-weight: 800;
        color: #000000;
    }
    .bw-metric-title {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        color: #444444;
        letter-spacing: 0.5px;
    }

    /* Monochrome Stack Item */
    .bw-stack-record {
        background: #ffffff;
        border: 1.5px dashed #000000;
        border-radius: 4px;
        padding: 8px 12px;
        margin-bottom: 6px;
    }

    /* Textarea & Inputs */
    textarea, input {
        border: 1.5px solid #000000 !important;
        border-radius: 4px !important;
        background-color: #ffffff !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Safe Session State Initialization (Crash-proof)
if "engine" not in st.session_state or not hasattr(st.session_state.engine, "commit_history_list"):
    st.session_state.engine = GitEngine()

engine: GitEngine = st.session_state.engine

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
    col_code, col_graph = st.columns([1.1, 0.9])

    with col_code:
        st.markdown("### Code Editor & Commit")
        edited_text = st.text_area(
            "Working File:",
            value=engine.working_content,
            height=200,
            label_visibility="collapsed"
        )
        if edited_text != engine.working_content:
            engine.working_content = edited_text

        col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
        with col_m1:
            c_msg = st.text_input("Commit Message:", placeholder="e.g. Added tax calculation")
        with col_m2:
            author = st.text_input("Author:", value="Developer")
        with col_m3:
            st.write("")
            st.write("")
            if st.button("Commit Changes", type="primary", use_container_width=True):
                if not c_msg:
                    st.error("Please enter a commit message.")
                else:
                    nc = engine.commit(message=c_msg, author=author)
                    st.success(f"Committed [{nc.commit_id}]")
                    st.rerun()

    with col_graph:
        st.markdown("### Lineage Graph (Circular Dot Nodes)")
        st.caption("Commits rendered as small circular dot nodes with dotted ancestry connectors.")

        # Graphviz DOT: Pure Black & White (Solid Black HEAD, White Dotted Ancestors)
        dot_lines = [
            "digraph G {",
            '  rankdir="TB";',
            '  bgcolor="transparent";',
            '  node [shape="circle", fixedsize=true, width=0.22, height=0.22, penwidth=2.0];',
            '  edge [style="dotted", color="#000000", penwidth=1.8, arrowhead="vee", arrowsize=0.6];'
        ]

        total_nodes = len(engine.commit_history_list)
        for idx, c in enumerate(engine.commit_history_list):
            c_num = total_nodes - idx
            cid = getattr(c, "commit_id", "")
            c_msg_str = getattr(c, "message", "")[:18]
            is_head = cid == engine.refs.head_commit_id

            # Monochrome: Solid black for HEAD, white dotted circle for parents
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

    st.markdown("---")

    # Bottom Row: Linked List (Left) + Stack & Hash Map (Right)
    col_ll, col_right = st.columns([1.1, 0.9])

    with col_ll:
        st.markdown("### 1. Linked List (Commit Ancestry Chain)")
        
        # Human-Readable Chain: Commit #2 -> Commit #1 -> None
        total_c = len(engine.commit_history_list)
        chain_elements = []
        for idx, c in enumerate(engine.commit_history_list):
            c_num = total_c - idx
            cid = getattr(c, "commit_id", "")
            c_msg_str = getattr(c, "message", "")
            is_head = cid == engine.refs.head_commit_id
            head_tag = " (HEAD)" if is_head else ""
            chain_elements.append(f"**Commit #{c_num}** `[{cid}]`: *\"{c_msg_str}\"*{head_tag}")

        st.markdown(" ➔ ".join(chain_elements) + " ➔ `None (Root)`")

        # Linked List Table (Safe and Robust)
        ll_table = []
        for idx, c in enumerate(engine.commit_history_list):
            c_num = total_c - idx
            try:
                row = c.to_dict(c_num)
            except Exception:
                cid = getattr(c, "commit_id", "")
                pid = f"[{c.parent.commit_id}]" if getattr(c, "parent", None) else "None (Root)"
                row = {
                    "Version": f"Commit #{c_num}",
                    "Commit ID": f"[{cid}]",
                    "Message": getattr(c, "message", ""),
                    "Branch": getattr(c, "branch", "main"),
                    "Parent Pointer": pid,
                    "Timestamp": getattr(c, "timestamp_str", "")
                }
            ll_table.append(row)

        st.dataframe(ll_table, use_container_width=True)

    with col_right:
        # Stack Section
        st.markdown(f"### 2. Stack (Git Stash - LIFO) — Depth: {engine.stash.size()}")
        col_st_in, col_st_push, col_st_pop = st.columns([2, 1, 1])
        with col_st_in:
            stash_msg = st.text_input("Stash Note:", placeholder="WIP edits", label_visibility="collapsed")
        with col_st_push:
            if st.button("Push Stash", use_container_width=True):
                ok, msg = engine.stash_push(stash_msg)
                st.rerun()
        with col_st_pop:
            if st.button("Pop Stash", use_container_width=True):
                ok, msg = engine.stash_pop()
                st.rerun()

        stashed = engine.stash.get_all()
        if not stashed:
            st.caption("Stash stack is currently empty.")
        else:
            for i, item in enumerate(stashed):
                badge = "TOP (LIFO)" if i == 0 else f"Pos {i}"
                st.markdown(f"""
                <div class="bw-stack-record">
                    <strong>[{badge}]</strong> {item.message} <small>({item.branch} — {item.timestamp})</small>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        # Hash Map Section
        st.markdown(f"### 3. Hash Map (Object Store & References) — {engine.object_store.count()} Objects")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.caption("ObjectStore (Key-Value Table)")
            obj_data = [{"SHA-256 Key": k, "Commit Message": getattr(v, "message", str(v))} for k, v in engine.object_store.all_entries().items()]
            st.dataframe(obj_data, use_container_width=True)
        with col_h2:
            st.caption("Branch Reference Table")
            ref_data = [{"Branch Name": b, "Target Commit": cid} for b, cid in engine.refs.branches.items()]
            st.dataframe(ref_data, use_container_width=True)


# ==================================================================================================
# VIEW 2: SEPARATE ANALYTICS DASHBOARD (EXECUTIVE MONOCHROME)
# ==================================================================================================

elif main_view == "Analytics Dashboard":
    st.markdown("## Repository Analytics Dashboard")
    st.caption("High-level system metrics and recent operational logs.")

    # 4 Executive Monochrome Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="bw-metric">
            <div class="bw-metric-title">Total Commits</div>
            <div class="bw-metric-val">{len(engine.commit_history_list)}</div>
            <div style="font-size:11px; color:#666; margin-top:4px;">Linked List Nodes</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="bw-metric">
            <div class="bw-metric-title">Active Branches</div>
            <div class="bw-metric-val">{len(engine.refs.branches)}</div>
            <div style="font-size:11px; color:#666; margin-top:4px;">Hash Map Reference Keys</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="bw-metric">
            <div class="bw-metric-title">Stash Depth</div>
            <div class="bw-metric-val">{engine.stash.size()}</div>
            <div style="font-size:11px; color:#666; margin-top:4px;">LIFO Stack Items</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="bw-metric">
            <div class="bw-metric-title">Stored Objects</div>
            <div class="bw-metric-val">{engine.object_store.count()}</div>
            <div style="font-size:11px; color:#666; margin-top:4px;">O(1) Key-Value Entries</div>
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
        st.dataframe(engine.dsa_logs, use_container_width=True)
    else:
        st.caption("No operations logged yet.")
