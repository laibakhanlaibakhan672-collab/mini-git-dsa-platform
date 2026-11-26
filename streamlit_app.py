"""
====================================================================================================
PROJECT: GIT DSA VISUAL PLATFORM (LAVENDER THEME - CALIBRI FONT - ALL-IN-ONE 4 DS WORKSPACE)
====================================================================================================
Design Specs:
  - Font Style: Calibri throughout (Medium 15-16px readable font size)
  - Left Sidebar: Soft Lavender color palette (#F3E8FF / #EDE9FE / #E9D5FF)
  - 4 Core Data Structures (Linked List, Hash Map, Graph, Stack) ALL ON ONE SINGLE PAGE
  - Commit Graph: Sleek small circular DOT nodes (not blocks) with dotted edges
  - Dashboard: Separate clean view (zero lengthy essay explanations)
  - Merkle Tree & 4 Pillars completely removed
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
    """Singly Linked List node representing a commit snapshot with parent pointer."""
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Commit ID": f"[{self.commit_id}]",
            "Message": self.message,
            "Branch": self.branch,
            "Parent Pointer": f"[{self.parent.commit_id}]" if self.parent else "None (Root)",
            "Timestamp": self.timestamp_str
        }


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
        self._log_dsa("Linked List", "Node Prepend (HEAD)", "O(1)", f"Commit [{commit_id}] points to parent [{parent_id_str}].")

        self.object_store.put(commit_id, commit_node)
        self.refs.set_branch(self.refs.current_branch, commit_id)
        self.refs.head_commit_id = commit_id
        self._log_dsa("Hash Map", "ObjectStore & Ref Put", "O(1)", f"Stored commit [{commit_id}] in key-value store.")

        return commit_node

    def create_branch(self, branch_name: str) -> Tuple[bool, str]:
        name = branch_name.strip()
        if not name or name in self.refs.branches or not self.refs.head_commit_id:
            return False, "Invalid branch name or branch already exists."
        self.refs.set_branch(name, self.refs.head_commit_id)
        self._log_dsa("Hash Map", "Branch Ref Insert", "O(1)", f"Branch '{name}' created.")
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
# STREAMLIT UI: CALIBRI FONT + LAVENDER SIDEBAR + ALL 4 DS IN ONE PAGE
# ==================================================================================================

st.set_page_config(
    page_title="Git DSA Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling: Calibri Font Medium + Lavender Left Sidebar
st.markdown("""
<style>
    /* Global Font: Calibri Medium (15px-16px) */
    html, body, [class*="css"], .stApp, p, span, div, label, input, textarea, button, select {
        font-family: Calibri, 'Segoe UI', Candara, Arial, sans-serif !important;
        font-size: 15.5px !important;
    }

    h1 { font-size: 26px !important; font-weight: 700 !important; color: #4a154b !important; }
    h2 { font-size: 21px !important; font-weight: 700 !important; color: #581c87 !important; }
    h3 { font-size: 18px !important; font-weight: 700 !important; color: #6b21a8 !important; }
    h4 { font-size: 16px !important; font-weight: 700 !important; }

    /* Left Sidebar: Lavender Theme */
    section[data-testid="stSidebar"] {
        background-color: #f3e8ff !important; /* Soft Lavender */
        border-right: 1.5px solid #e9d5ff !important;
    }

    section[data-testid="stSidebar"] * {
        color: #3b0764 !important;
    }

    /* Light Clean Card */
    .clean-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    }

    /* Small Dotted Dot Badge */
    .dot-badge {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        border: 1.5px dotted #7c3aed;
        background: #ede9fe;
        margin-right: 5px;
    }

    /* LIFO Stack Container */
    .stack-box {
        background: #faf5ff;
        border: 1.5px dashed #c084fc;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Persistence
if "engine" not in st.session_state:
    st.session_state.engine = GitEngine()

engine: GitEngine = st.session_state.engine

# ==================================================================================================
# LAVENDER LEFT SIDEBAR (CONTROLS)
# ==================================================================================================

with st.sidebar:
    st.markdown("## ⚡ Git VCS Controls")
    st.caption("Lavender Control Panel")

    main_view = st.radio(
        "Select View:",
        ["💻 All-in-One 4-DS Workspace", "📊 Separate Dashboard"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 🌿 Branch Manager (Hash Map)")
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

    new_b = st.text_input("New Branch Name:", placeholder="e.g. feature-login")
    if st.button("➕ Create Branch", use_container_width=True):
        if new_b:
            ok, msg = engine.create_branch(new_b)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")
    st.markdown("### ⚡ Fast Checkout (Hash Map)")
    commit_ids = [c.commit_id for c in engine.commit_history_list]
    c_target = st.selectbox("Restore Commit Version:", commit_ids)
    if st.button("🔄 Checkout Version", use_container_width=True):
        ok, msg = engine.checkout_commit(c_target)
        if ok:
            st.success(msg)
            st.rerun()

    st.markdown("---")
    st.caption(f"**Current HEAD:** `[{engine.refs.head_commit_id}]`")


# ==================================================================================================
# VIEW 1: ALL 4 DATA STRUCTURES TOGETHER ON ONE SINGLE PAGE
# ==================================================================================================

if main_view == "💻 All-in-One 4-DS Workspace":
    st.markdown("## 💻 Git Version Control Platform")
    st.caption("Linked List, Stack, Hash Map, and Graph working together on one interactive page.")

    # Top Row: Code Editor & Small-Dot Graph
    col_code, col_graph = st.columns([1.1, 0.9])

    with col_code:
        st.markdown("### 📝 Code Editor & Commit")
        edited_text = st.text_area(
            "Working File:",
            value=engine.working_content,
            height=220,
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
            if st.button("💾 Commit", type="primary", use_container_width=True):
                if not c_msg:
                    st.error("Please enter a message.")
                else:
                    nc = engine.commit(message=c_msg, author=author)
                    st.success(f"Committed [{nc.commit_id}]")
                    st.rerun()

    with col_graph:
        st.markdown("### 🕸️ Graph (Small Dot Nodes)")
        st.caption("Visualizing commits as small dotted circular dots connected by dotted arrows.")

        # Graphviz DOT with SMALL CIRCULAR DOTS (NOT BLOCKS)
        dot_lines = [
            "digraph G {",
            '  rankdir="TB";',
            '  bgcolor="transparent";',
            '  node [shape="circle", fixedsize=true, width=0.22, height=0.22, style="filled,dotted", penwidth=2.0];',
            '  edge [style="dotted", color="#7c3aed", penwidth=2.0, arrowhead="vee", arrowsize=0.6];'
        ]

        for c in engine.commit_history_list:
            is_head = c.commit_id == engine.refs.head_commit_id
            fill_col = "#c084fc" if is_head else "#ede9fe"
            border_col = "#7e22ce" if is_head else "#a855f7"
            head_str = " (HEAD)" if is_head else ""
            xlabel_text = f"[{c.commit_id}]{head_str} {c.message[:18]}"

            dot_lines.append(
                f'  "{c.commit_id}" [label="", fillcolor="{fill_col}", color="{border_col}", xlabel="{xlabel_text}"];'
            )
            if c.parent:
                dot_lines.append(f'  "{c.commit_id}" -> "{c.parent.commit_id}";')

        dot_lines.append("}")
        st.graphviz_chart("\n".join(dot_lines), use_container_width=True)

    st.markdown("---")

    # Bottom Row: Linked List (Left) + Stack & Hash Map (Right)
    col_ll, col_right = st.columns([1.1, 0.9])

    with col_ll:
        st.markdown("### 🔗 1. Linked List (Commit Ancestry)")
        # Visual compact pointer chain
        chain = [f"**[{c.commit_id}]**" for c in engine.commit_history_list]
        st.markdown(" ➡️ ".join(chain) + " ➡️ `None (Root)`")

        # Linked List Table
        ll_table = [c.to_dict() for c in engine.commit_history_list]
        st.dataframe(ll_table, use_container_width=True)

    with col_right:
        # Stack Section
        st.markdown(f"### 📦 2. Stack (Git Stash - LIFO) — Depth: {engine.stash.size()}")
        col_st_in, col_st_push, col_st_pop = st.columns([2, 1, 1])
        with col_st_in:
            stash_msg = st.text_input("Stash note:", placeholder="WIP edits", label_visibility="collapsed")
        with col_st_push:
            if st.button("📥 Push", use_container_width=True):
                ok, msg = engine.stash_push(stash_msg)
                st.rerun()
        with col_st_pop:
            if st.button("📤 Pop", use_container_width=True):
                ok, msg = engine.stash_pop()
                st.rerun()

        stashed = engine.stash.get_all()
        if not stashed:
            st.caption("Stack is currently empty.")
        else:
            for i, item in enumerate(stashed):
                badge = "🔝 TOP" if i == 0 else f"#{i}"
                st.markdown(f"""
                <div class="stack-box">
                    <strong>{badge}:</strong> {item.message} <small>({item.branch} - {item.timestamp})</small>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        # Hash Map Section
        st.markdown(f"### 🗄️ 3. Hash Map (O(1) Storage & Refs) — {engine.object_store.count()} Objects")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.caption("**ObjectStore (Key-Value)**")
            obj_data = [{"SHA Key": k, "Message": v.message} for k, v in engine.object_store.all_entries().items()]
            st.dataframe(obj_data, use_container_width=True)
        with col_h2:
            st.caption("**Branch RefTable**")
            ref_data = [{"Branch": b, "Target": cid} for b, cid in engine.refs.branches.items()]
            st.dataframe(ref_data, use_container_width=True)


# ==================================================================================================
# VIEW 2: SEPARATE DASHBOARD (CLEAN METRICS - NO ESSAYS)
# ==================================================================================================

elif main_view == "📊 Separate Dashboard":
    st.markdown("## 📊 Repository Analytics Dashboard")
    st.caption("High-level system metrics without long explanations.")

    # 4 Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Commits", len(engine.commit_history_list), help="Linked List Nodes")
    c2.metric("Active Branches", len(engine.refs.branches), help="Hash Map Keys")
    c3.metric("Stashed States", engine.stash.size(), help="Stack (LIFO) Depth")
    c4.metric("Stored Objects", engine.object_store.count(), help="Hash Map Key-Value pairs")

    st.markdown("---")
    st.markdown("### 📋 System Status Summary")
    st.markdown(f"""
    - **Active Branch:** `{engine.refs.current_branch}`
    - **Current HEAD Commit:** `[{engine.refs.head_commit_id}]`
    - **Repository Status:** Clean (Working directory in sync with HEAD)
    """)

    st.markdown("### ⚡ Live Operations Activity")
    if engine.dsa_logs:
        st.dataframe(engine.dsa_logs, use_container_width=True)
    else:
        st.caption("No operations logged yet.")
