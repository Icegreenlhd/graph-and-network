from igraph import BoundingBox, Graph, palettes, plot
import os.path as osp


def draw_graph_color(g, save_path="./two_coloring/test.png", red_set=[], blue_set=[]):
    """
    draw the graph to visualize the coloring
    :param red_set:  edge to color read
    :param blue_set: edge to color blue
    :param save_path: path to save
    :param g: graph to be drawn
    :return:
    """
    visual_style = dict()
    visual_style["vertex_color"] = "red"
    visual_style["vertex_label"] = list(range(g.vcount()))
    visual_style["vertex_size"] = 20
    visual_style["layout"] = "circle"
    visual_style["margin"] = 30
    visual_style["edge_color"] = ["black" for _ in g.es]
    visual_style["edge_width"] = 4
    for index in red_set:
        visual_style["edge_color"][index] = "red"
    for index in blue_set:
        visual_style["edge_color"][index] = "blue"
    plot(g, save_path, **visual_style)
    return


def get_full_graph(n):
    full_graph = Graph.Full(n)
    return full_graph


class KFour:
    def __init__(self, num):
        self.vertex_num = num
        self.k_4 = self.create_k_4()

    def create_k_4(self):
        k_four = dict()
        for a in range(self.vertex_num):
            for b in range(a + 1, self.vertex_num):
                for c in range(b + 1, self.vertex_num):
                    for d in range(c + 1, self.vertex_num):
                        k_four["_".join([str(a), str(b), str(c), str(d)])] = 0
        return k_four

    def _get_edge_index(self, v_a, v_b):
        other_v = list(range(self.vertex_num))
        other_v.remove(v_a), other_v.remove(v_b)
        index = list()
        for i in range(len(other_v)):
            for j in range(i + 1, len(other_v)):
                k4list = [v_a, v_b, other_v[i], other_v[j]]
                k4list.sort()
                index.append("_".join([str(k) for k in k4list]))
        return index

    def count_color(self, v_a, v_b):
        import random
        import math
        color_choices = ["red", "blue"]
        all_index_ab = self._get_edge_index(v_a, v_b)
        weight = 0  #
        for index in all_index_ab:
            num = self.k_4[index]
            if num == 0 or math.isinf(num):
                continue
            else:
                weight += math.copysign(2 ** (-1 * (5 - abs(num) - 1)), num)  # add the color weight, + blue, - red
        if weight == 0:
            color = random.choice(color_choices)
        elif weight > 0:
            color = color_choices[0]  # more k4 color blue, choose red
        else:
            color = color_choices[1]
        self._color_edge(color, all_index_ab)
        return color

    def _color_edge(self, color, index):
        import math
        color_choices = {"red": -1, "blue": 1}
        for i in index:
            if math.isinf(self.k_4[i]):
                continue
            elif self.k_4[i] * color_choices[color] < 0:
                self.k_4[i] = float('inf')
            else:
                self.k_4[i] += color_choices[color]
        return

    def print_result(self, save_path):
        print("monochromatic K4 num: ", list(self.k_4.values()).count(6))
        with open(save_path[:-4]+'.txt', 'a') as file:
            file.write("monochromatic K4 num: "+str(list(self.k_4.values()).count(6))+'\n')
        return


def color_two(graph, save_path="./two_coloring/save_name.jpg", is_draw=True):
    """

    :param is_draw: (bool) whether draw
    :param graph: (igraph.Graph)
    :param save_path:
    :return:
    """
    red_set = list()
    blue_set = list()
    k_4 = KFour(graph.vcount())
    count = 0
    for es in graph.es:
        color = k_4.count_color(es.source, es.target)
        if color == 'red':
            red_set.append(es.index)
        else:
            blue_set.append(es.index)
        print(count+1, "color", es.source, es.target, color)
        with open(save_path[:-4]+'.txt', 'a') as file:
            file.write(str(count+1) + " color " + str(es.source)+' '+str(es.target)+' '+color+'\n')
        if is_draw:
            draw_graph_color(graph, save_path=save_path[:-4]+'_'+str(count)+'.png', red_set=red_set, blue_set=blue_set)
        count += 1
    return k_4


if __name__ == "__main__":
    vertex_num = 100
    draw_or_not = False if vertex_num > 10 else True
    save_graph = "./two_coloring/Full" + str(vertex_num) + '.png'
    g = get_full_graph(vertex_num)
    draw_graph_color(g, save_graph)
    res_color = color_two(g, save_path=save_graph, is_draw=draw_or_not)
    res_color.print_result(save_graph)
