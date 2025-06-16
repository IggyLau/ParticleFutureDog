import matplotlib.pyplot as plt
import networkx as nx

# --- Define the Nodes and Edges as per your prior data ---

nodes = [
    "StandIdle",    # 01_zhanlidaiji1
    "SitIdle",      # 02_zuoxiadaiji1
    "LieIdle",      # 03_paxiadaiji
    "WalkFwd",      # 10_qizou or 11_walk (choose one; let's use 11_walk)
    "Run",          # 14_run
    "Eat",          # 21_jinshi
    "Drink",        # 22_yinshui
    "Sleep1",       # 23_shuijiaoxunhuan1
    "Sleep2",       # 24_shuijiaoxunhuan2
    "Sleep3",       # 25_shuijiaoxunhuan3
    "Sleep4",       # 26_shuijiaoxunhuan4
    "Sleep5",       # 27_shuijiaoxunhuan5
    "SleepStart",   # 28_kaishishuijiao
    "WakeUp",       # 29_qichuang
]

# Edge format: (from_node, to_node, label)
edges = [
    ("StandIdle", "SitIdle", "04_zhanlizhuanzuoxia"),
    ("SitIdle", "StandIdle", "05_zuoxiazhuanzhanli"),
    ("StandIdle", "LieIdle", "06_zhanlizhuanpaxia"),
    ("LieIdle", "StandIdle", "07_paxiazhuanzhanli"),
    ("SitIdle", "LieIdle", "08_zuoxiazhuanpaxia"),
    ("LieIdle", "SitIdle", "09_paxiazhuanzuoxia"),
    ("StandIdle", "WalkFwd", "11_walk"),
    ("WalkFwd", "StandIdle", "12_zouting"),
    ("StandIdle", "Run", "13_qipao"),
    ("Run", "StandIdle", "15_paoting"),
    ("WalkFwd", "Run", "13_qipao"),
    ("Run", "WalkFwd", "15_paoting"),
    ("StandIdle", "SleepStart", "28_kaishishuijiao"),
    ("SleepStart", "Sleep1", "23_shuijiaoxunhuan1"),
    ("Sleep1", "Sleep2", "24_shuijiaoxunhuan2"),
    ("Sleep2", "Sleep3", "25_shuijiaoxunhuan3"),
    ("Sleep3", "Sleep4", "26_shuijiaoxunhuan4"),
    ("Sleep4", "Sleep5", "27_shuijiaoxunhuan5"),
    ("Sleep1", "WakeUp", "29_qichuang"),
    ("WakeUp", "StandIdle", "01_zhanlidaiji1"),
    ("StandIdle", "Eat", "21_jinshi"),
    ("StandIdle", "Drink", "22_yinshui"),
]

# --- Build and visualize the graph ---

# Create a directed graph
G = nx.DiGraph()

# Add nodes
for n in nodes:
    G.add_node(n)

# Add edges
for from_node, to_node, label in edges:
    G.add_edge(from_node, to_node, label=label)

# Draw layout
plt.figure(figsize=(16, 10))
pos = nx.spring_layout(G, k=1.5, seed=42)  # Can also try nx.shell_layout(G) or nx.kamada_kawai_layout(G)

# Draw nodes and edges
nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="#88ccff")
nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=30, edge_color="#444444")

# Draw labels
nx.draw_networkx_labels(G, pos, font_size=12, font_color="black", font_weight="bold")

# Draw edge labels (animation files)
edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, bbox=dict(alpha=0.7))

plt.title("Dog Animation State Map (Nodes = Poses, Edges = Transitions)")
plt.axis("off")
plt.tight_layout()
plt.show()