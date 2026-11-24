"""
====================================================================================================
PROJECT: GIT 4-DSA VISUAL PLATFORM (STREAMLIT COMMUNITY CLOUD EDITION)
====================================================================================================
4 Core Data Structures Implemented:
  1. LINKED LIST: Singly Linked List for commit ancestry (CommitNode.parent)
  2. HASH MAP: Content-Addressable Object Database & Branch Ref Table (O(1) lookups)
  3. MERKLE TREE: Recursive directory rollup hashing & file hierarchy
  4. STACK (LIFO): 'git stash' engine (push, pop, peek for uncommitted changes)

Deploy to Streamlit Cloud (share.streamlit.io):
  1. Upload this file (streamlit_app.py) & requirements.txt to GitHub
  2. Connect GitHub to Streamlit Cloud
  3. Click 'Deploy' -> Instant free public URL!
====================================================================================================
"""

import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
import streamlit as st

# ==================================================================================================
# 1. DATA STRUCTURE: LINKED LIST (COMMIT HISTORY)
# ==================================================================================================

class CommitNode:
    """Singly Linked List node representing a commit snapshot with parent pointer."""
    def __init__(
        self,
        commit_id: str,
        message: str,
        tree_hash: str,
        author: str = "Developer",
        parent: Optional["CommitNode"] = None,
        branch: str = "main",
        timestamp: Optional[float] = None
    ):
        self.commit_id = commit_id
        self.message = message
        self.tree_hash = tree_hash
        self.author = author
        self.parent = parent  # Singly Linked List pointer
        self.branch = branch
        self.time_val = timestamp if timestamp is not None else time.time()
        self.timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.time_val))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commit_id": self.commit_id,
            "message": self.message,
            "tree_hash": self.tree_hash,
            "author": self.author,
            "branch": self.branch,
            "timestamp": self.timestamp_str,
            "parent_id": self.parent.commit_id if self.parent else "ROOT",
        }


# ==================================================================================================
# 2. DATA STRUCTURE: HASH MAP (OBJECT STORE & REFS)
# ==================================================================================================

class ObjectStore:
    """Content-Addressable Object Database (.git/objects) providing O(1) lookups."""
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

    def count(self) -> int:
        return len(self._table)


class RefTable:
    """Hash Map storing branch names and current HEAD pointer."""
    def __init__(self, default_branch: str = "main"):
        self.branches: Dict[str, str] = {}
        self.current_branch: str = default_branch
        self.head_commit_id: Optional[str] = None

    def set_branch(self, branch_name: str, commit_id: str) -> None:
        self.branches[branch_name] = commit_id

    def get_branch_commit(self, branch_name: str) -> Optional[str]:
        return self.branches.get(branch_name)


# ==================================================================================================
# 3. DATA STRUCTURE: TREES & MERKLE TREES (FILE SYSTEM)
# ==================================================================================================

class BlobNode:
    """Leaf node representing a file and its SHA-256 hash."""
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content
        self.hash = hashlib.sha256(f"blob {len(content)}\0{content}".encode("utf-8")).hexdigest()[:8]


class TreeNode:
    """Directory node with children and deterministic Merkle rollup hash."""
    def __init__(self, dirname: str):
        self.dirname = dirname
        self.children: Dict[str, Union[BlobNode, "TreeNode"]] = {}
        self.hash = ""

    def add_child(self, name: str, child: Union[BlobNode, "TreeNode"]) -> None:
        self.children[name] = child

    def compute_merkle_hash(self) -> str:
        child_digests = []
        for name in sorted(self.children.keys()):
            child = self.children[name]
            if isinstance(child, TreeNode):
                child_digests.append(f"tree {child.compute_merkle_hash()} {name}")
            else:
                child_digests.append(f"blob {child.hash} {name}")
        self.hash = hashlib.sha256("\n".join(child_digests).encode("utf-8")).hexdigest()[:8]
        return self.hash


class MerkleTreeBuilder:
    @staticmethod
    def build_from_flat_files(files_dict: Dict[str, str]) -> TreeNode:
        root = TreeNode("root")
        for filepath, content in files_dict.items():
            parts = filepath.strip("/").split("/")
            curr_dir = root
            for part in parts[:-1]:
                if part not in curr_dir.children or not isinstance(curr_dir.children[part], TreeNode):
                    curr_dir.children[part] = TreeNode(part)
                curr_dir = curr_dir.children[part]  # type: ignore
            curr_dir.add_child(parts[-1], BlobNode(parts[-1], content))
        root.compute_merkle_hash()
        return root

    @staticmethod
    def extract_flat_files(tree_node: TreeNode, prefix: str = "") -> Dict[str, str]:
        flat = {}
        for name, child in tree_node.children.items():
            path = f"{prefix}/{name}" if prefix else name
            if isinstance(child, BlobNode):
                flat[path] = child.content
            elif isinstance(child, TreeNode):
                flat.update(MerkleTreeBuilder.extract_flat_files(child, path))
        return flat


# ==================================================================================================
# 4. DATA STRUCTURE: STACK (LIFO - GIT STASH)
# ==================================================================================================

class StashItem:
    def __init__(self, message: str, files_snapshot: Dict[str, str], branch: str):
        self.message = message
        self.files_snapshot = dict(files_snapshot)
        self.branch = branch
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")


class StashStack:
    """LIFO Stack for Git Stash."""
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

        self.working_files: Dict[str, str] = {
            "src/app.py": (
                "# Core Application Logic\n"
                "def calculate_total(prices):\n"
                "    return sum(prices)\n\n"
                "print('Total:', calculate_total([10, 20, 30]))\n"
            ),
            "src/utils.py": (
                "# Helper utilities\n"
                "def format_currency(val):\n"
                "    return f'${val:.2f}'\n"
            ),
            "README.md": (
                "# Git 4-DSA Visual Platform\n"
                "Live demonstration of Linked List, Hash Map, Merkle Tree, and Stack.\n"
            )
        }
        self.dsa_logs: List[Dict[str, Any]] = []
        self.commit(message="Initial project commit with starter files", author="System")

    def _log_dsa(self, ds_type: str, op: str, comp: str, detail: str) -> None:
        self.dsa_logs.insert(0, {
            "time": time.strftime("%H:%M:%S"),
            "ds": ds_type,
            "operation": op,
            "complexity": comp,
            "detail": detail
        })
        if len(self.dsa_logs) > 40:
            self.dsa_logs.pop()

    def commit(self, message: str, author: str = "Developer") -> CommitNode:
        root_tree = MerkleTreeBuilder.build_from_flat_files(self.working_files)
        tree_hash = root_tree.hash
        self.object_store.put(f"tree:{tree_hash}", root_tree)
        self._log_dsa("Merkle Tree", "Root Rollup", "O(N log N)", f"Merkle Root '{tree_hash}' computed.")

        parent_node = self.head_node
        parent_id_str = parent_node.commit_id if parent_node else "ROOT"
        curr_time = time.time()
        raw_payload = f"{tree_hash}:{message}:{author}:{parent_id_str}:{curr_time}"
        commit_id = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()[:7]

        commit_node = CommitNode(
            commit_id=commit_id,
            message=message,
            tree_hash=tree_hash,
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
        self._log_dsa("Hash Map", "Ref & Store Put", "O(1)", f"Registered [{commit_id}] in Hash Map.")

        return commit_node

    def create_branch(self, branch_name: str) -> Tuple[bool, str]:
        name = branch_name.strip()
        if not name or name in self.refs.branches or not self.refs.head_commit_id:
            return False, "Invalid branch name or branch already exists."
        self.refs.set_branch(name, self.refs.head_commit_id)
        self._log_dsa("Hash Map", "Branch Insert", "O(1)", f"Branch '{name}' created in Hash Map.")
        return True, f"Branch '{name}' created."

    def switch_branch(self, branch_name: str) -> Tuple[bool, str]:
        if branch_name not in self.refs.branches:
            return False, "Branch not found."
        target_id = self.refs.branches[branch_name]
        commit = self.object_store.get(target_id)
        if isinstance(commit, CommitNode):
            tree_obj = self.object_store.get(f"tree:{commit.tree_hash}")
            if isinstance(tree_obj, TreeNode):
                self.working_files = MerkleTreeBuilder.extract_flat_files(tree_obj)
            self.head_node = commit
        self.refs.current_branch = branch_name
        self.refs.head_commit_id = target_id
        self._log_dsa("Hash Map & Merkle", "Branch Switch", "O(Files)", f"Switched to '{branch_name}'.")
        return True, f"Switched to '{branch_name}'."

    def checkout_commit(self, commit_id: str) -> Tuple[bool, str]:
        commit = self.object_store.get(commit_id.strip())
        if not isinstance(commit, CommitNode):
            return False, f"Commit [{commit_id}] not found in Hash Map."
        tree_obj = self.object_store.get(f"tree:{commit.tree_hash}")
        if isinstance(tree_obj, TreeNode):
            self.working_files = MerkleTreeBuilder.extract_flat_files(tree_obj)
        self.head_node = commit
        self.refs.head_commit_id = commit_id
        self._log_dsa("Hash Map", "Commit Lookup", "O(1)", f"Checked out [{commit_id}] via Hash Map.")
        return True, f"Checked out [{commit_id}]."

    def stash_push(self, msg: str = "") -> Tuple[bool, str]:
        text = msg.strip() or f"WIP on {self.refs.current_branch}"
        self.stash.push(StashItem(text, self.working_files, self.refs.current_branch))
        if self.head_node:
            tree_obj = self.object_store.get(f"tree:{self.head_node.tree_hash}")
            if isinstance(tree_obj, TreeNode):
                self.working_files = MerkleTreeBuilder.extract_flat_files(tree_obj)
        self._log_dsa("Stack (LIFO)", "stash push", "O(1)", f"Pushed to Stash Stack. Size: {self.stash.size()}.")
        return True, "Saved to Stash Stack."

    def stash_pop(self) -> Tuple[bool, str]:
        item = self.stash.pop()
        if not item:
            return False, "Stash stack is empty."
        self.working_files = dict(item.files_snapshot)
        self._log_dsa("Stack (LIFO)", "stash pop", "O(1)", f"Popped state '{item.message}'.")
        return True, f"Restored stash: '{item.message}'."


# ==================================================================================================
# STREAMLIT USER INTERFACE
# ==================================================================================================

st.set_page_config(
    page_title="Git 4-DSA Visual Platform",
    page_icon="⚡",
    layout="wide"
)

# Persistent Session State
if "engine" not in st.session_state:
    st.session_state.engine = GitEngine()
if "active_file" not in st.session_state:
    st.session_state.active_file = "README.md"

engine: GitEngine = st.session_state.engine

# Top Header
st.title("⚡ Git 4-DSA Visual Platform & Analytics Dashboard")
st.caption("Demonstrating **Linked List**, **Hash Map**, **Merkle Tree**, and **Stack (LIFO)** in a Version Control System.")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🌿 Branch Manager (Hash Map)")
    branches = list(engine.refs.branches.keys())
    curr_branch = engine.refs.current_branch
    selected_branch = st.selectbox(
        "Current Active Branch:",
        branches,
        index=branches.index(curr_branch) if curr_branch in branches else 0
    )
    if selected_branch != curr_branch:
        ok, msg = engine.switch_branch(selected_branch)
        if ok:
            st.success(msg)
            st.rerun()

    # Create Branch
    new_branch_name = st.text_input("New Branch Name:", placeholder="e.g. dev, feature-ui")
    if st.button("➕ Create Branch", use_container_width=True):
        if new_branch_name:
            ok, msg = engine.create_branch(new_branch_name)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")
    st.header("📦 Git Stash (Stack - LIFO)")
    st.write(f"**Stack Depth:** `{engine.stash.size()}` items")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("📥 Stash Push", use_container_width=True):
            ok, msg = engine.stash_push("WIP changes")
            st.info(msg)
            st.rerun()
    with col_s2:
        if st.button("📤 Stash Pop", use_container_width=True):
            ok, msg = engine.stash_pop()
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)

    st.markdown("---")
    st.header("📁 Merkle Files")
    files_list = sorted(list(engine.working_files.keys()))
    st.session_state.active_file = st.selectbox("Open File:", files_list)

    new_file_input = st.text_input("Add New File Path:", placeholder="e.g. src/login.py")
    if st.button("📄 Add File", use_container_width=True):
        if new_file_input and new_file_input not in engine.working_files:
            engine.working_files[new_file_input] = ""
            st.session_state.active_file = new_file_input
            st.rerun()

# --- MAIN TABS ---
tab_workbench, tab_dashboard, tab_telemetry = st.tabs([
    "💻 Code & Graph Workspace",
    "📊 Analytics Dashboard",
    "⚡ Real-Time DSA Telemetry"
])

# 1. TAB: WORKBENCH
with tab_workbench:
    col_editor, col_graph = st.columns([1.1, 0.9])

    with col_editor:
        st.subheader(f"📝 Working Editor: `{st.session_state.active_file}`")
        curr_content = engine.working_files.get(st.session_state.active_file, "")
        edited_content = st.text_area(
            "File Content:",
            value=curr_content,
            height=260,
            label_visibility="collapsed"
        )
        if edited_content != curr_content:
            engine.working_files[st.session_state.active_file] = edited_content

        st.markdown("#### 💾 Create Commit")
        commit_msg = st.text_input("Commit Message:", placeholder="Describe changes...")
        author_name = st.text_input("Author:", value="Developer")
        if st.button("🚀 Commit to Branch", type="primary", use_container_width=True):
            if not commit_msg:
                st.error("Please enter a commit message.")
            else:
                new_commit = engine.commit(commit_msg, author=author_name)
                st.success(f"✓ Commit created: [{new_commit.commit_id}] '{new_commit.message}'")
                st.rerun()

    with col_graph:
        st.subheader("🔗 Commit Lineage (Linked List)")
        root_tree = MerkleTreeBuilder.build_from_flat_files(engine.working_files)
        st.caption(f"**Root Merkle Hash:** `{root_tree.hash}` | **HEAD:** `[{engine.refs.head_commit_id}]`")

        # Build Graphviz DOT string for Linked List Visualization
        dot_lines = [
            "digraph LinkedList {",
            '  rankdir="TB";',
            '  node [shape="box", style="rounded,filled", fontname="Courier", fontsize=10];',
            '  edge [color="#6c757d", arrowhead="vee", penwidth=1.5];'
        ]

        for c in engine.commit_history_list:
            is_head = c.commit_id == engine.refs.head_commit_id
            fill_color = "#39c5cf" if is_head else "#e7f5ff"
            font_color = "#ffffff" if is_head else "#1c7ed6"
            label = f"[{c.commit_id}]\\n{c.message[:22]}\\n(Branch: {c.branch})"
            dot_lines.append(f'  "{c.commit_id}" [label="{label}", fillcolor="{fill_color}", fontcolor="{font_color}"];')
            if c.parent:
                dot_lines.append(f'  "{c.commit_id}" -> "{c.parent.commit_id}" [label="parent"];')

        dot_lines.append("}")
        st.graphviz_chart("\n".join(dot_lines))

        # Checkout Selector
        st.markdown("#### ⚡ Checkout Commit (Hash Map O(1))")
        commit_ids = [c.commit_id for c in engine.commit_history_list]
        selected_cid = st.selectbox("Select historical version:", commit_ids)
        if st.button("🔄 Checkout Version", use_container_width=True):
            ok, msg = engine.checkout_commit(selected_cid)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# 2. TAB: DASHBOARD
with tab_dashboard:
    st.subheader("📊 Repository & Data Structures Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("1. Total Commits", len(engine.commit_history_list), help="Linked List Nodes")
    m2.metric("2. Active Branches", len(engine.refs.branches), help="Hash Map Keys")
    m3.metric("3. Tracked Files", len(engine.working_files), help="Merkle Tree Leaves")
    m4.metric("4. Stashed States", engine.stash.size(), help="Stack (LIFO) Depth")

    st.markdown("---")
    st.subheader("🧠 The 4 Core DSA Pillars in Action")

    p1, p2 = st.columns(2)
    with p1:
        st.info("""
        **1. 🔗 Singly Linked List (Commit History)**
        - **Role:** Every commit is a node containing `parent: Optional[CommitNode]`.
        - **Operation:** Committing points backward (`new.parent = HEAD`), appending in **O(1)** time.
        - **Traversal:** Traversing history moves along parent pointers backward from HEAD.
        """)
        st.success("""
        **2. 🗄️ Hash Map (Content-Addressable Object Database)**
        - **Role:** Simulates Git's `.git/objects` key-value store.
        - **Operation:** Commits, Trees, and Blobs are stored by SHA-256 hash.
        - **Complexity:** **O(1) average lookup** for instant version checkouts.
        """)

    with p2:
        st.warning("""
        **3. 🌳 Merkle Tree (Cryptographic File Hierarchy)**
        - **Role:** Directories are Tree nodes; files are leaf Blobs.
        - **Operation:** Directory hashes are calculated recursively from child hashes.
        - **Complexity:** Changing 1 file updates only the path to the root (**O(log N)**).
        """)
        st.error("""
        **4. 📦 Stack (Git Stash - LIFO)**
        - **Role:** Saves uncommitted working tree changes onto a Last-In, First-Out stack.
        - **Operation:** `stash_push` pushes snapshot in **O(1)**; `stash_pop` restores top snapshot in **O(1)**.
        """)

# 3. TAB: TELEMETRY
with tab_telemetry:
    st.subheader("⚡ Live Algorithmic Execution Traces")
    if engine.dsa_logs:
        st.table(engine.dsa_logs)
    else:
        st.write("No operations executed yet.")
