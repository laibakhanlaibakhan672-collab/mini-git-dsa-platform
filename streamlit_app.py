"""
====================================================================================================
PROJECT: GIT DSA VISUAL PLATFORM (LIGHT THEME - MODULAR 4-PAGE EDITION)
====================================================================================================
Data Structures Covered:
  1. LINKED LIST : Commit Lineage (CommitNode.parent pointer chain)
  2. STACK (LIFO): Git Stash Engine (push, pop, peek, stack depth)
  3. HASH MAP    : O(1) Object Store & Branch Reference Table
  4. GRAPH       : Commit Graph & DAG Relationships (with Dotted Nodes & Edges)

Features:
  - Clean Soft Light Theme (Pastels, White Cards, Subtle Grays)
  - Dedicated Separate Pages for Dashboard, Editor, Linked List, Stack, Hash Map, Graph
  - Graph with Dotted Node and Edge styling
  - Merkle Tree & 4 Pillars removed as requested
====================================================================================================
"""

import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
import streamlit as st

# ==================================================================================================
# 1. CORE DATA STRUCTURES: LINKED LIST, STACK, HASH MAP
# ==================================================================================================

class CommitNode:
    """
    Singly Linked List node representing a commit snapshot.
    Contains an explicit pointer to its parent commit (self.parent).
    """
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
            "commit_id": self.commit_id,
            "message": self.message,
            "author": self.author,
            "branch": self.branch,
            "timestamp": self.timestamp_str,
            "parent_id": self.parent.commit_id if self.parent else "None (Root)",
        }


class ObjectStore:
    """Hash Map (.git/objects) providing O(1) content-addressable storage."""
    def __init__(self):
        self._table: Dict[str, Any] = {}
        self.total_writes = 0
        self.total_reads = 0

    def put(self, hash_key: str, data: Any) -> None:
        self._table[hash_key] = data
        self.total_writes += 1

    def get(self, hash_key: str) -> Optional[Any]:
        self.total_reads += 1
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
    """Represents a stashed snapshot of file content."""
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

    def peek(self) -> Optional[StashItem]:
        return self._items[-1] if self._items else None

    def size(self) -> int:
        return len(self._items)

    def get_all(self) -> List[StashItem]:
        return list(reversed(self._items))


# ==================================================================================================
# UNIFIED GIT ENGINE (LINKED LIST, STACK, HASH MAP, GRAPH)
# ==================================================================================================

class GitEngine:
    def __init__(self):
        self.object_store = ObjectStore()
        self.refs = RefTable(default_branch="main")
        self.head_node: Optional[CommitNode] = None
        self.commit_history_list: List[CommitNode] = []
        self.stash = StashStack()

        # In-Memory working file content
        self.working_content: str = (
            "# Welcome to Mini Git Platform!\n"
            "# ------------------------------------------------------------\n"
            "def calculate_fibonacci(n):\n"
            "    \"\"\"Calculates the nth Fibonacci number.\"\"\"\n"
            "    if n <= 1:\n"
            "        return n\n"
            "    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)\n\n"
            "print('Result:', calculate_fibonacci(6))\n"
        )
        self.dsa_logs: List[Dict[str, Any]] = []

        # Create Initial Root Commit
        self.commit(message="Initial project commit with starter code", author="System")

    def _log_dsa(self, ds_type: str, op: str, comp: str, detail: str) -> None:
        self.dsa_logs.insert(0, {
            "Time": time.strftime("%H:%M:%S"),
            "Data Structure": ds_type,
            "Operation": op,
            "Complexity": comp,
            "Details": detail
        })
        if len(self.dsa_logs) > 30:
            self.dsa_logs.pop()

    def commit(self, message: str, author: str = "Developer") -> CommitNode:
        parent_node = self.head_node
        parent_id_str = parent_node.commit_id if parent_node else "ROOT"
        curr_time = time.time()

        # SHA-256 Commit ID Hash
        raw_payload = f"{self.working_content}:{message}:{author}:{parent_id_str}:{curr_time}"
        commit_id = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()[:7]

        # 1. LINKED LIST: Instantiate node and point to previous HEAD
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

        # 2. HASH MAP: Store commit object & update branch ref
        self.object_store.put(commit_id, commit_node)
        self.refs.set_branch(self.refs.current_branch, commit_id)
        self.refs.head_commit_id = commit_id
        self._log_dsa("Hash Map", "ObjectStore Put", "O(1)", f"Saved commit [{commit_id}] in key-value store.")

        return commit_node

    def create_branch(self, branch_name: str) -> Tuple[bool, str]:
        name = branch_name.strip()
        if not name or name in self.refs.branches or not self.refs.head_commit_id:
            return False, "Invalid branch name or branch already exists."
        self.refs.set_branch(name, self.refs.head_commit_id)
        self._log_dsa("Hash Map", "Branch Ref Insert", "O(1)", f"Created branch '{name}' -> [{self.refs.head_commit_id}].")
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
        self._log_dsa("Hash Map", "Branch Lookup", "O(1)", f"Switched to branch '{branch_name}'.")
        return True, f"Switched to '{branch_name}'."

    def checkout_commit(self, commit_id: str) -> Tuple[bool, str]:
        commit = self.object_store.get(commit_id.strip())
        if not isinstance(commit, CommitNode):
            return False, f"Commit [{commit_id}] not found in Hash Map."
        self.working_content = commit.content
        self.head_node = commit
        self.refs.head_commit_id = commit_id
        self._log_dsa("Hash Map", "Direct Commit Checkout", "O(1)", f"Restored snapshot [{commit_id}].")
        return True, f"Checked out commit [{commit_id}]."

    def stash_push(self, msg: str = "") -> Tuple[bool, str]:
        text = msg.strip() or f"WIP on {self.refs.current_branch}"
        self.stash.push(StashItem(text, self.working_content, self.refs.current_branch))
        if self.head_node:
            self.working_content = self.head_node.content
        self._log_dsa("Stack (LIFO)", "stash push", "O(1)", f"Pushed state to Stash Stack. Stack depth: {self.stash.size()}.")
        return True, "Saved uncommitted changes to Stash Stack."

    def stash_pop(self) -> Tuple[bool, str]:
        item = self.stash.pop()
        if not item:
            return False, "Stash stack is empty."
        self.working_content = item.content
        self._log_dsa("Stack (LIFO)", "stash pop", "O(1)", f"Popped top state '{item.message}' from Stack.")
        return True, f"Restored stashed state: '{item.message}'."


# ==================================================================================================
# STREAMLIT UI CONFIGURATION & STYLING (CLEAN SOFT LIGHT THEME)
# ==================================================================================================

st.set_page_config(
    page_title="Git DSA Visual Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Light Theme CSS (Soft Pastels, White Cards, Crisp Borders)
st.markdown("""
<style>
    /* Global Light Clean Styles */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* Clean Soft Cards */
    .light-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        margin-bottom: 16px;
    }

    .metric-box {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    }
    
    .metric-val {
        font-size: 32px;
        font-weight: 800;
        color: #228be6;
        margin-top: 4px;
    }
    
    .metric-title {
        font-size: 13px;
        font-weight: 700;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Soft Stack Box */
    .stack-item {
        background: #f1f3f5;
        border: 1px dashed #adb5bd;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }

    /* Dotted Indicator */
    .dotted-badge {
        display: inline-block;
        border: 2px dotted #4dabf7;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        color: #1971c2;
        background: #e7f5ff;
    }
</style>
""", unsafe_allow_html=True)

# Session State Persistence
if "engine" not in st.session_state:
    st.session_state.engine = GitEngine()

engine: GitEngine = st.session_state.engine

# ==================================================================================================
# SIDEBAR NAVIGATION (DEDICATED SEPARATE PAGES)
# ==================================================================================================

with st.sidebar:
    st.markdown("### ⚡ Git DSA Platform")
    st.caption("Clean Light Theme Edition")

    page = st.radio(
        "Select Page / View:",
        [
            "📊 Analytics Dashboard",
            "📝 Code Workspace & Commit",
            "🔗 Linked List Lineage",
            "📦 Stack (Git Stash)",
            "🗄️ Hash Map (Objects & Refs)",
            "🕸️ Graph (Dotted Nodes)"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("#### 🌿 Active Branch (Hash Map)")
    branches = list(engine.refs.branches.keys())
    curr_b = engine.refs.current_branch
    selected_b = st.selectbox(
        "Current Branch:",
        branches,
        index=branches.index(curr_b) if curr_b in branches else 0,
        label_visibility="collapsed"
    )
    if selected_b != curr_b:
        ok, msg = engine.switch_branch(selected_b)
        if ok:
            st.success(msg)
            st.rerun()

    new_b = st.text_input("Create Branch:", placeholder="e.g. dev, feature-auth")
    if st.button("➕ Add Branch", use_container_width=True):
        if new_b:
            ok, msg = engine.create_branch(new_b)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")
    st.caption(f"**HEAD Commit:** `[{engine.refs.head_commit_id}]`")


# ==================================================================================================
# PAGE 1: 📊 SEPARATE ANALYTICS DASHBOARD (FOUR PILLARS REMOVED)
# ==================================================================================================

if page == "📊 Analytics Dashboard":
    st.title("📊 Repository Analytics Dashboard")
    st.caption("Real-time metrics for commits, active branches, stashed states, and key-value objects.")

    # Top KPI Metrics Cards (Clean Soft Light Styling)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">🔗 Total Commits</div>
            <div class="metric-val">{len(engine.commit_history_list)}</div>
            <div style="font-size:11px; color:#adb5bd; margin-top:4px;">Linked List Nodes</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">🌿 Active Branches</div>
            <div class="metric-val">{len(engine.refs.branches)}</div>
            <div style="font-size:11px; color:#adb5bd; margin-top:4px;">Hash Map Reference Keys</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">📦 Stash Depth</div>
            <div class="metric-val">{engine.stash.size()}</div>
            <div style="font-size:11px; color:#adb5bd; margin-top:4px;">LIFO Stack Items</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">🗄️ Stored Objects</div>
            <div class="metric-val">{engine.object_store.count()}</div>
            <div style="font-size:11px; color:#adb5bd; margin-top:4px;">O(1) Hash Map Entries</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Active System Summary Card
    st.subheader("📋 Active System Summary")
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.markdown(f"""
        <div class="light-card">
            <h4 style="margin-top:0; color:#228be6;">🌿 Active Branch Reference</h4>
            <p><strong>Current Branch:</strong> <code>{engine.refs.current_branch}</code></p>
            <p><strong>Current HEAD Commit ID:</strong> <code>[{engine.refs.head_commit_id}]</code></p>
            <p><strong>Total Branches Registered:</strong> {len(engine.refs.branches)}</p>
        </div>
        """, unsafe_allow_html=True)

    with sub_col2:
        st.markdown(f"""
        <div class="light-card">
            <h4 style="margin-top:0; color:#40c057;">⚡ Data Structures Summary</h4>
            <p>• <strong>Commit Lineage:</strong> Singly Linked List via <code>parent</code> pointers.</p>
            <p>• <strong>Version Storage:</strong> O(1) SHA-256 Hash Map key-value table.</p>
            <p>• <strong>Git Stash:</strong> LIFO (Last-In, First-Out) Stack.</p>
            <p>• <strong>Graph:</strong> Commit dependency relationships (Dotted Nodes).</p>
        </div>
        """, unsafe_allow_html=True)

    # Recent Operations Log
    st.subheader("⚡ Recent Operations History")
    if engine.dsa_logs:
        st.dataframe(engine.dsa_logs, use_container_width=True)
    else:
        st.info("No operations performed yet.")


# ==================================================================================================
# PAGE 2: 📝 CODE WORKSPACE & COMMIT
# ==================================================================================================

elif page == "📝 Code Workspace & Commit":
    st.title("📝 Code Workspace & Editor")
    st.caption("Write or modify your code, enter a commit message, and create a new commit node.")

    edited_code = st.text_area(
        "Working File Editor:",
        value=engine.working_content,
        height=320
    )
    if edited_code != engine.working_content:
        engine.working_content = edited_code

    st.markdown("#### 💾 Create New Commit")
    col_c1, col_c2 = st.columns([3, 1])
    with col_c1:
        commit_msg = st.text_input("Commit Message:", placeholder="Describe the change made...")
    with col_c2:
        author = st.text_input("Author:", value="Developer")

    if st.button("🚀 Commit to Branch", type="primary", use_container_width=True):
        if not commit_msg:
            st.error("Please enter a commit message.")
        else:
            new_c = engine.commit(message=commit_msg, author=author)
            st.success(f"✓ Commit created: [{new_c.commit_id}] '{new_c.message}'")
            st.rerun()


# ==================================================================================================
# PAGE 3: 🔗 SEPARATE LINKED LIST PAGE
# ==================================================================================================

elif page == "🔗 Linked List Lineage":
    st.title("🔗 Linked List (Commit Ancestry Chain)")
    st.caption("Each commit in Git is an immutable Node in a Singly Linked List pointing backwards to its parent.")

    st.markdown("""
    <div class="light-card">
        <h4 style="margin-top:0; color:#228be6;">Concept: How Linked List Works in Git</h4>
        <p>In this system, <code>HEAD</code> always points to the latest commit node. Each node contains a pointer <code>self.parent</code> 
        pointing to the previous commit node. Creating a new commit prepends a node to the head of the list in <strong>O(1)</strong> time.</p>
    </div>
    """, unsafe_allow_html=True)

    # Visual representation of the chain
    st.subheader("Visual Pointer Chain")
    chain_elements = []
    for c in engine.commit_history_list:
        is_head = c.commit_id == engine.refs.head_commit_id
        head_tag = " (HEAD)" if is_head else ""
        chain_elements.append(f"**[{c.commit_id}]**{head_tag} — *'{c.message}'*")

    st.markdown(" ➡️ ".join(chain_elements) + " ➡️ **None (Root)**")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Linked List Nodes Table")
    nodes_table = [c.to_dict() for c in engine.commit_history_list]
    st.table(nodes_table)


# ==================================================================================================
# PAGE 4: 📦 SEPARATE STACK (GIT STASH) PAGE
# ==================================================================================================

elif page == "📦 Stack (Git Stash)":
    st.title("📦 Stack Data Structure (Git Stash - LIFO)")
    st.caption("Git Stash operates on a strict Last-In, First-Out (LIFO) Stack.")

    st.markdown("""
    <div class="light-card">
        <h4 style="margin-top:0; color:#e67e22;">Concept: Last-In, First-Out (LIFO)</h4>
        <p>When you run <code>stash push</code>, uncommitted code changes are placed on <strong>TOP</strong> of the stack in <strong>O(1)</strong>. 
        When you run <code>stash pop</code>, the most recently stashed snapshot is removed from the top and restored in <strong>O(1)</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    # Stash Controls
    col_st1, col_st2, col_st3 = st.columns([2, 1, 1])
    with col_st1:
        stash_note = st.text_input("Stash Message / Note:", placeholder="e.g. Incomplete work on login")
    with col_st2:
        st.write("")
        st.write("")
        if st.button("📥 Stash Push (O(1))", use_container_width=True):
            ok, msg = engine.stash_push(stash_note)
            st.info(msg)
            st.rerun()
    with col_st3:
        st.write("")
        st.write("")
        if st.button("📤 Stash Pop (O(1))", use_container_width=True):
            ok, msg = engine.stash_pop()
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f"📦 Stash Stack Visualizer (Depth: {engine.stash.size()})")

    stashed_items = engine.stash.get_all()
    if not stashed_items:
        st.info("The Stash Stack is currently empty.")
    else:
        for idx, item in enumerate(stashed_items):
            top_badge = "🔝 TOP OF STACK (LIFO)" if idx == 0 else f"Stack Position: {idx}"
            st.markdown(f"""
            <div class="stack-item">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-weight:700; color:#e67e22;">stash@{{{idx}}} — {item.message}</span>
                    <span style="font-size:11px; font-weight:700; color:#495057;">{top_badge}</span>
                </div>
                <div style="font-size:12px; color:#868e96; margin-top:4px;">
                    Branch: <code>{item.branch}</code> | Timestamp: {item.timestamp}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==================================================================================================
# PAGE 5: 🗄️ SEPARATE HASH MAP PAGE
# ==================================================================================================

elif page == "🗄️ Hash Map (Objects & Refs)":
    st.title("🗄️ Hash Map (Content-Addressable Storage & Refs)")
    st.caption("Git uses Hash Maps (dictionaries) to guarantee instantaneous O(1) lookups by SHA-256 hash or branch name.")

    st.markdown("""
    <div class="light-card">
        <h4 style="margin-top:0; color:#40c057;">Concept: O(1) Fast Key-Value Retrieval</h4>
        <p>In Git, commit snapshots are stored in an <strong>ObjectStore</strong> where:
        <br><code>Key = 7-char SHA-256 Hash</code> ➡️ <code>Value = CommitNode Object</code>.
        <br>Branch references are stored in a <strong>RefTable</strong> where:
        <br><code>Key = Branch Name</code> ➡️ <code>Value = Commit Hash ID</code>.</p>
    </div>
    """, unsafe_allow_html=True)

    # Instant Lookup Test
    st.subheader("🔍 O(1) Direct Commit Lookup Test")
    col_h1, col_h2 = st.columns([3, 1])
    commit_ids = [c.commit_id for c in engine.commit_history_list]
    with col_h1:
        search_id = st.selectbox("Select Commit ID Key to look up:", commit_ids)
    with col_h2:
        st.write("")
        st.write("")
        if st.button("⚡ Checkout Version", use_container_width=True):
            ok, msg = engine.checkout_commit(search_id)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("<br>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.subheader("🗄️ ObjectStore Table (Hash Map)")
        obj_entries = []
        for k, v in engine.object_store.all_entries().items():
            msg = v.message if hasattr(v, "message") else str(v)
            obj_entries.append({"Key (SHA-256)": k, "Value (Commit Message)": msg})
        st.table(obj_entries)

    with col_t2:
        st.subheader("🌿 RefTable (Branch Map)")
        ref_entries = [{"Branch Key": b, "Target Commit Value": cid} for b, cid in engine.refs.branches.items()]
        st.table(ref_entries)


# ==================================================================================================
# PAGE 6: 🕸️ SEPARATE GRAPH PAGE (WITH DOTTED NODES & EDGES)
# ==================================================================================================

elif page == "🕸️ Graph (Dotted Nodes)":
    st.title("🕸️ Commit Graph & Relationships")
    st.caption("Visualizing the commit history as a graph with Dotted Nodes and Dotted Edges.")

    st.markdown("""
    <div class="light-card">
        <span class="dotted-badge">Dotted Graph View</span>
        <p style="margin-top:8px; font-size:13px; color:#495057;">
        The graph below represents commits as <strong>Dotted Nodes</strong> with <strong>Dotted Dependency Arrows</strong> 
        pointing from each child commit to its ancestor/parent commit.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Graphviz DOT with DOTTED NODES and DOTTED EDGES
    dot_lines = [
        "digraph CommitGraph {",
        '  rankdir="TB";',
        '  bgcolor="transparent";',
        '  node [style="dotted,rounded,filled", shape="box", penwidth=2.5, fontname="Courier", fontsize=11];',
        '  edge [style="dotted", color="#868e96", arrowhead="vee", penwidth=2.2];'
    ]

    for c in engine.commit_history_list:
        is_head = c.commit_id == engine.refs.head_commit_id
        # Light pastel coloring for nodes
        fill_color = "#d0ebff" if is_head else "#f8f9fa"
        border_color = "#1c7ed6" if is_head else "#adb5bd"
        font_color = "#1864ab" if is_head else "#212529"
        head_label = " [HEAD]" if is_head else ""

        label = f"[{c.commit_id}]{head_label}\\n{c.message[:22]}\\nBranch: {c.branch}"
        dot_lines.append(
            f'  "{c.commit_id}" [label="{label}", fillcolor="{fill_color}", color="{border_color}", fontcolor="{font_color}"];'
        )
        if c.parent:
            dot_lines.append(f'  "{c.commit_id}" -> "{c.parent.commit_id}" [label=" parent", style="dotted"];')

    dot_lines.append("}")

    st.graphviz_chart("\n".join(dot_lines), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Inspect / Checkout Commit Node")
    cid_select = st.selectbox("Select Node ID to Inspect:", [c.commit_id for c in engine.commit_history_list])
    selected_node = engine.object_store.get(cid_select)
    if isinstance(selected_node, CommitNode):
        st.markdown(f"""
        <div class="light-card">
            <h4 style="margin-top:0; color:#1c7ed6;">Commit [{selected_node.commit_id}]</h4>
            <p><strong>Message:</strong> {selected_node.message}</p>
            <p><strong>Branch:</strong> <code>{selected_node.branch}</code></p>
            <p><strong>Parent Node:</strong> <code>{selected_node.parent.commit_id if selected_node.parent else 'None (Root)'}</code></p>
            <p><strong>Timestamp:</strong> {selected_node.timestamp_str}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ Checkout This Version", use_container_width=True):
            ok, msg = engine.checkout_commit(selected_node.commit_id)
            if ok:
                st.success(msg)
                st.rerun()
