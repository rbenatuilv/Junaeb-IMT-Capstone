import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
import networkx as nx
import modules.parameters as p
from typing import Union


def find(u: int, parents: list) -> int:
    """
    Find the parent of a given node in the graph.
    """
    if u == parents[u]:
        return u
    parents[u] = find(parents[u], parents)
    return parents[u]


def union(u: int, v: int, parents: list[int], size: list[int]):
    """
    Unite two nodes in the graph, given their parents 
    and the size of each tree.
    """
    u = find(u, parents)
    v = find(v, parents)

    if u == v:
        return
    
    if size[u] >= size[v]:
        parents[v] = u
        size[u] += size[v]
    else:
        parents[u] = v
        size[v] += size[u]


def get_adj_list(points: np.array) -> list[list]:
    """
    Obtain the list of adjacent nodes for each node in the graph,
    given a set of points with coordinates.
    """
    n = len(points)
    tri = Delaunay(points)

    edges = [[] for _ in range(n)]

    for u in tri.simplices:
        if u[1] not in edges[u[0]]:
            edges[u[0]].append(u[1])
        if u[2] not in edges[u[0]]:
            edges[u[0]].append(u[2])
        if u[0] not in edges[u[1]]:
            edges[u[1]].append(u[0])
        if u[2] not in edges[u[1]]:
            edges[u[1]].append(u[2])
        if u[0] not in edges[u[2]]:
            edges[u[2]].append(u[0])
        if u[1] not in edges[u[2]]:
            edges[u[2]].append(u[1])

    return edges


def get_edges(adj_list: list[list]) -> list[tuple]:
    """
    Obtain the list of edges in the graph, given the
    list of adjacent nodes for each node.
    """
    edges = []
    for i in range(len(adj_list)):
        for j in adj_list[i]:
            edges.append((i, j))
    return edges


def distance(u, v, mode='manhattan'):
    """
    Calculate the distance between two points in the graph.
    Modes: 'manhattan' or 'euclidean'.
    """
    if mode == 'manhattan':
        return np.abs(u[0] - v[0]) + np.abs(u[1] - v[1])
    elif mode == 'euclidean':
        return np.sqrt((u[0] - v[0])**2 + (u[1] - v[1])**2)


def MST(points: np.array) -> list[list]:
    """
    Compute the minimum spanning tree of a graph, 
    given a set of points with coordinates. Returns
    the list of adjacent nodes for each node in the graph.
    """
    n = len(points)
    padre = [i for i in range(n)]
    largo = [1 for _ in range(n)]
    aristas = []
    edges = [[] for _ in range(n)]

    adj_list = get_adj_list(points)

    for i in range(n):
        for j in adj_list[i]:
            aristas.append(
                [
                distance(points[i], points[j], mode='manhattan'), i, j
                ]
            )

    aristas.sort(key=lambda x: x[0])

    for u in aristas:
        if find(u[1], padre) != find(u[2], padre):
            union(u[1], u[2], padre, largo)
            edges[u[1]].append(u[2])
            edges[u[2]].append(u[1])

    return edges


def plot_graph(edges: list[int], 
               pos: dict, 
               ax: plt.Axes = None, 
               reg_number: Union[int, list] = None, 
               options=None, 
               figsize: tuple = (8, 8), **args) -> plt.Axes:
    """
    Plot a graph, given the list of edges, the position of each node,
    and the number of the region to plot, if any.
    """
    graph = nx.Graph(edges)

    if options is None:
        options = {
            'node_color': 'darkblue',
            'node_size': 10,
            'edge_color': 'black',
            'width': 0.5
        }

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    nx.draw_networkx(graph, pos, ax=ax, with_labels=False, **options)

    if reg_number is not None:
        regs = p.REGS_CONT

        if isinstance(reg_number, int):
            reg_number = [reg_number]
        reg = regs[regs['codregion'].isin(reg_number)].geometry.boundary

        reg.plot(ax=ax, color='k', **args)
        plt.xlim(float(reg.bounds['minx']), float(reg.bounds['maxx']))
        plt.ylim(float(reg.bounds['miny']), float(reg.bounds['maxy']))

    return ax


def get_subtree_metrics(node: int, parent: int, edges: list[list], 
        profit: list, subval: list[int], subsize: list[int]):
    """
    Obtains the subtree value and size for each node in the graph, 
    using recursive DFS.
    """
    subval[node] = profit[node]
    subsize[node] = 1
    for child in edges[node]:
        if child == parent:
            continue
        get_subtree_metrics(child, node, edges, profit, subval, subsize)
        subval[node] += subval[child]
        subsize[node] += subsize[child]
    return


def find_best_split(node: int, parent: int, 
         edges: list, subval: list, subsize: list, 
         totalval: int, best: list, MINSZ: int = p.MINSZ) -> list:
    """
    Obtains the best pair of nodes to split the graph, using recursive DFS.
    """

    if subsize[node] < MINSZ or len(edges[node]) == 0:
        return
    
    for child in edges[node]:
        if child == parent:
            continue
        if abs((totalval - subval[child]) - subval[child]) < best[0]:
            best[0] = abs((totalval - subval[child]) - subval[child])
            best[1] = node
            best[2] = child
        find_best_split(child, node, edges, subval, subsize, totalval, best)

    return best


def assign_ut_to_nodes(node: int, parent: int, edges: list[int], 
         uts: list[int], current_ut: int):
    """
    Assings the UT value to each node in the graph, using recursive DFS.
    """
    uts[node] = current_ut
    for child in edges[node]:
        if child == parent:
            continue
        assign_ut_to_nodes(child, node, edges, uts, current_ut)
