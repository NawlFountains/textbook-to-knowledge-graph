import streamlit as st
import networkx as nx
from networkx.readwrite import json_graph
from pyvis.network import Network
import json
import streamlit.components.v1 as components

# ── Load data ──────────────────────────────────────────
@st.cache_resource
def load_graph():
    with open("assets/knowledge_graph.json", "r") as f:
        data = json.load(f)
    return json_graph.node_link_graph(data)

@st.cache_resource
def load_concepts():
    with open("assets/top_concepts.json", "r") as f:
        return json.load(f)

G = load_graph()
concepts = load_concepts()

# ── Pyvis helper ───────────────────────────────────────
def render_pyvis(subgraph, height="500px"):
    net = Network(height=height, width="100%", notebook=False)
    
    pagerank = nx.pagerank(subgraph, weight='weight')
    communities = list(nx.community.greedy_modularity_communities(subgraph))
    community_map = {n: i for i, c in enumerate(communities) for n in c}
    
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"]
    
    for node in subgraph.nodes():
        score = pagerank.get(node, 0.01)
        net.add_node(
            node,
            label=node,
            size=10 + score * 200,
            color=colors[community_map.get(node, 0) % len(colors)],
            title=f"{node}\nPageRank: {score:.4f}"
        )
    
    for u, v, data in subgraph.edges(data=True):
        net.add_edge(u, v,
                    value=data.get('pmi', 1),
                    title=f"PMI: {data.get('pmi', 0):.2f}")
    
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "springLength": 100
            },
            "solver": "forceAtlas2Based"
        }
    }
    """)
    
    path = "/tmp/graph.html"
    net.save_graph(path)
    return open(path, "r").read()

# ── UI ─────────────────────────────────────────────────
st.set_page_config(page_title="Textbook Knowledge Graph", layout="wide")

st.title("Textbook Knowledge Graph")
st.caption("Digital Systems — Chapters 1-3")

tab1, tab2, tab3 = st.tabs(["Full Graph", "Explore Concept", "Learning Path"])

# Tab 1 — Full graph
with tab1:
    st.subheader("Full Knowledge Graph")
    st.caption(f"{G.number_of_nodes()} concepts · {G.number_of_edges()} relationships")
    html = render_pyvis(G, height="600px")
    components.html(html, height=620)

# Tab 2 — Ego graph
with tab2:
    st.subheader("Explore a Concept")
    concept = st.selectbox("Select a concept", sorted(concepts))
    radius = st.slider("Neighborhood radius", 1, 3, 1)
    
    if concept:
        ego = nx.ego_graph(G, concept, radius=radius)
        st.caption(f"{ego.number_of_nodes()} related concepts found")
        html = render_pyvis(ego, height="500px")
        components.html(html, height=520)

# Tab 3 — Learning path
with tab3:
    st.subheader("Learning Path")
    col1, col2 = st.columns(2)
    with col1:
        start = st.selectbox("I know...", sorted(concepts), key="start")
    with col2:
        end = st.selectbox("I want to learn...", sorted(concepts), key="end")
    
    if st.button("Find Path"):
        try:
            path = nx.shortest_path(G, start, end)
            st.success(f"Path found — {len(path)} steps")
            st.write(" → ".join(path))
        except nx.NetworkXNoPath:
            st.warning("No direct path found — try different concepts")
        except nx.NodeNotFound as e:
            st.error(f"Concept not found: {e}")

with st.sidebar:
    st.markdown("### 📖 Source Material")
    st.markdown("""
    **Logic and Computer Design Fundamentals**  
    *M. Morris Mano & Charles R. Kime*  
    5th Edition, Pearson, 2016
    
    Chapters extracted:
    - Chapter 1: Digital Systems and Information
    - Chapter 2: Combinational Logic Circuits  
    - Chapter 3: Combinational Logic Design
    """)
    
    st.divider()
    
    st.markdown("### About")
    st.caption("""
    Knowledge graph built using spaCy noun chunk 
    extraction and PMI-filtered co-occurrence edges.
    """)
