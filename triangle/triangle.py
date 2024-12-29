from copy import deepcopy
from collections import deque
from itertools import zip_longest
import heapq


def generate_triangle_reflections(N):
    next_vertex = 0
    g = Graph()
    f = Field(next_vertex)
    next_vertex +=1 

    work = deque()
    work.appendleft(f.root)
    g.vertices.append(f.root)

    while len(work) != 0:
        vertex = work.pop()

        length = g.shortest_path_to_root(vertex)
        if length is None:
            breakpoint()
        if length >= N:
            continue

        next_vertex, added = f.add_neighbors(vertex, next_vertex)
        g.vertices.extend(added)
        work.extendleft(added)

    return g


def analyze(graph):
    max_connections_per_vertex = max([v.connections_count() for v in graph.vertices])
    y_axis = len(graph.vertices)
    x_axis = max([len(v.edges()) for v in graph.vertices])

    print(f"{max_connections_per_vertex=}")
    print(f"{x_axis=}")
    print(f"{y_axis=}")


class Q:
    def __init__(self):
        self.__heap = []
        heapq.heapify(self.__heap)

    def push(self, priority, v):
        heapq.heappush(self.__heap, (priority, v))

    def pop(self):
        if len(self.__heap) == 0:
            return None

        (_priority, value) = heapq.heappop(self.__heap)
        return value


class Vertex:
    def __init__(self, idx, edges=[]):
        self.__edges = deepcopy(edges)
        self.__idx = idx

    def __lt__(self, other):
        return self.__idx < other.__idx

    def __eq__(self, other):
        if other is None:
            return False

        if len(self.__edges) == len(other.__edges):
            return self.__edges == other.__edges

        for left, right in zip_longest(self.__edges, other.__edges, fillvalue=False):
            if left != right:
                return False

        return True

    def __str__(self):
        edges = ", ".join(map(str, self.__edges))
        idx = self.__idx
        return f"Vertex: \n\tedges: [{edges}],\n\tidx: {idx}\n"

    def display(self, max_length):
        edges = " ".join(["1" if bit else "0" for bit in self.__edges])
        edges += " 0" * (max_length - len(self.__edges))
        return f"{edges}"

    def _idx(self):
        return self.__idx

    def _is_connected_to(self, other):
        if other._idx() < len(self.__edges):
            return self.__edges[other._idx()]

        return False

    def _connect_to(self, other):
        if len(self.__edges) > other._idx():
            if self.__edges[other._idx()]:
                return
            else:
                self.__edges[other._idx()] = True
                other._connect_to(self)
        else:
            filler = [False for _ in range(len(self.__edges), other._idx() + 1)]
            self.__edges.extend(filler)
            self.__edges[other._idx()] = True
            other._connect_to(self)

    def duplicate_as(self, new_idx):
        copy = Vertex(new_idx)
        copy.__edges = deepcopy(self.__edges)
        return copy

    def edges(self):
        return self.__edges

    def connections_count(self):
        return self.__edges.count(True)


class Field:
    def __init__(self, starting_index=0):
        self.root = Vertex(starting_index)
        self.field = [[self.root]]

    def locate(self, lookup):
        for r, row in enumerate(self.field):
            for c, vertex in enumerate(row):
                if vertex is None:
                    continue
                if vertex._idx() == lookup._idx():
                    return (r, c)

    def add_neighbors(self, start_point, next_idx):
        r, c = self.locate(start_point)
        if r - 1 < 0:
            new_row = [None for _ in range(0, len(self.field[0]))]
            self.field.insert(0, new_row)

        r, c = self.locate(start_point)
        if r + 1 >= len(self.field) - 1:
            new_row = [None for _ in range(0, len(self.field[0]))]
            self.field.append(new_row)

        r, c = self.locate(start_point)
        if c - 1 < 0:
            for row in self.field:
                row.insert(0, None)
        r, c = self.locate(start_point)
        if c + 1 >= len(self.field[0]) - 1:
            for row in self.field:
                row.append(None)

        if (
            self.field[r + 1][c] is not None
            or self.field[r - 1][c - 1] is not None
            or self.field[r - 1][c + 1] is not None
        ):
            return self.upside_down_y_around(start_point, next_idx)
        else:
            return self.upright_y_around(start_point, next_idx)

    def upside_down_y_around(self, vertex, next_idx):
        allocated = []
        r, c = self.locate(vertex)
        if self.field[r+1][c] is None:
            v = Vertex(next_idx)
            next_idx += 1
            self.field[r][c]._connect_to(v)
            self.field[r+1][c] = v
            allocated.append(v)

        if self.field[r-1][c-1] is None:
            v = Vertex(next_idx)
            next_idx += 1
            self.field[r][c]._connect_to(v)
            self.field[r-1][c-1] = v
            allocated.append(v)

        if self.field[r-1][c+1] is None:
            v = Vertex(next_idx)
            next_idx += 1
            self.field[r][c]._connect_to(v)
            self.field[r-1][c+1] = v
            allocated.append(v)

        return (next_idx, allocated)

    def upright_y_around(self, vertex, next_idx):
        allocated = []
        r, c = self.locate(vertex)
        if self.field[r-1][c] is None:
            v = Vertex(next_idx)
            next_idx += 1
            self.field[r][c]._connect_to(v)
            self.field[r-1][c] = v
            allocated.append(v)

        if self.field[r+1][c+1] is None:
            v = Vertex(next_idx)
            next_idx += 1
            self.field[r][c]._connect_to(v)
            self.field[r+1][c+1] = v
            allocated.append(v)

        if self.field[r+1][c-1] is None:
            v = Vertex(next_idx)
            next_idx += 1
            self.field[r][c]._connect_to(v)
            self.field[r+1][c-1] = v
            allocated.append(v)

        return (next_idx, allocated)

class Graph:
    def __init__(self):
        self.vertices = []

    def nodes_are_connected(self, idx1, idx2):
        return self.vertices[idx1]._is_connected_to(self.vertices[idx2])

    def shortest_path_to_root(self, vertex):
        if vertex._idx() == 0:
            return 0

        if self.nodes_are_connected(0, vertex._idx()):
            return 1

        q = Q()

        # if all the nodes were in a straight line
        max_distance = len(self.vertices) + 1
        dist = {}
        q.push(0, vertex)

        for v in self.vertices:
            dist[v._idx()] = max_distance

        dist[vertex._idx()] = 0

        while (node_to_check := q.pop()) != None:
            if node_to_check._idx() == 0:
                return dist[node_to_check._idx()]
            for idx, edge in enumerate(node_to_check.edges()):
                if not edge:
                    continue
                alt = dist[node_to_check._idx()] + 1
                if alt < dist[idx]:
                    dist[idx] = alt
                    q.push(alt, self.vertices[idx])

        return None

    def display(self):
        max_length = max([len(v.edges()) for v in self.vertices])
        return "\n".join([v.display(max_length) for v in self.vertices])

