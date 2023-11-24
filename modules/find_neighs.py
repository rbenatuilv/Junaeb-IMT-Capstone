import modules.graph as g
import modules.geo as geo
from shapely.geometry import Point
import geopandas as gpd
import heapq


MAXD = geo.convert_to_degrees(200000)


def get_closest(points, adj_list, node, k, mode='manhattan'):
    """Returns the k closest nodes to the given node"""

    visited = dict()
    gen = set()
    gen.add(node)

    finished = False
    last = False
    
    while gen and not finished:
        if last:
            finished = True

        new_gen = set()

        for next in gen:
            visited[next] = g.distance(points[node], points[next], mode=mode)

        for next in gen:
            for neigh in adj_list[next]:
                if neigh not in visited:
                    d = g.distance(points[node], points[neigh], mode=mode)
                    if d <= MAXD:
                        new_gen.add(neigh)
        
        gen = new_gen

        if len(visited) >= k:
            last = True

    visited.pop(node)
    visited = list(visited.items())
    visited.sort(key=lambda x: x[1])
    visited = visited[:k]

    tot_prob = sum([1 / x[1] for x in visited])
    probs = [(1 / x[1]) / tot_prob for x in visited]
    visited = [x[0] for x in visited]

    return visited, probs


def get_closest_dijkstra(points, adj_list, node, k, mode='manhattan'):
    """Returns the k closest nodes to the given node using Dijkstra's algorithm"""

    visited = dict()
    heap = [(0, node)]

    while heap:
        dist, next = heapq.heappop(heap)
        if next in visited:
            continue
        visited[next] = dist

        for neigh in adj_list[next]:
            if neigh not in visited:
                d = g.distance(points[node], points[neigh], mode=mode)
                if d <= MAXD:
                    heapq.heappush(heap, (d, neigh))

        if len(visited) > k:
            break

    visited.pop(node)
    visited = list(visited.items())
    visited.sort(key=lambda x: x[1])
    visited = visited[:k]

    tot_prob = sum([1 / x[1] for x in visited])
    probs = [(1 / x[1]) / tot_prob for x in visited]
    visited = [x[0] for x in visited]

    return visited, probs


def get_closest_intersect(gpd, node, k, mode='manhattan'):
    p = (gpd['Longitud'][node], gpd['Latitud'][node])
    point = Point(p)
    buff = point.buffer(MAXD)
    neighs = gpd[gpd.intersects(buff)]
    neighs = neighs[neighs.index != node]

    distancias = []
    for i in neighs.index:
        point = (neighs['Longitud'][i], neighs['Latitud'][i])
        d = g.distance(p, point, mode=mode)
        if len(distancias) < k:
            heapq.heappush(distancias, (-d, i))
        else:
            heapq.heappushpop(distancias, (-d, i))

    return [i for d, i in sorted(distancias, reverse=True)]

