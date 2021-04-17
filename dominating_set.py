from matplotlib.artist import Artist
from igraph import BoundingBox, Graph, palettes, plot


class GraphArtist(Artist):
    """Matplotlib artist class that draws igraph graphs.

    Only Cairo-based backends are supported.
    """

    def __init__(self, graph, bbox, palette=None, *args, **kwds):
        """Constructs a graph artist that draws the given graph within
        the given bounding box.

        `graph` must be an instance of `igraph.Graph`.
        `bbox` must either be an instance of `igraph.drawing.BoundingBox`
        or a 4-tuple (`left`, `top`, `width`, `height`). The tuple
        will be passed on to the constructor of `BoundingBox`.
        `palette` is an igraph palette that is used to transform
        numeric color IDs to RGB values. If `None`, a default grayscale
        palette is used from igraph.

        All the remaining positional and keyword arguments are passed
        on intact to `igraph.Graph.__plot__`.
        """
        Artist.__init__(self)

        if not isinstance(graph, Graph):
            raise TypeError("expected igraph.Graph, got %r" % type(graph))

        self.graph = graph
        self.palette = palette or palettes["gray"]
        self.bbox = BoundingBox(bbox)
        self.args = args
        self.kwds = kwds

    def draw(self, renderer):
        from matplotlib.backends.backend_cairo import RendererCairo
        if not isinstance(renderer, RendererCairo):
            raise TypeError("graph plotting is supported only on Cairo backends")
        self.graph.__plot__(renderer.gc.ctx, self.bbox, self.palette, *self.args, **self.kwds)


def draw_graph_matlabplot(graph, save_path="test.png", dominated_set=[], dominating_set=[]):
    """
    draw the graph to visualize
    :param dominated_set:  dominated set to color
    :param dominating_set: dominating set to color else
    :param save_path: path to save
    :param graph: graph to be drawn
    :return:
    """
    import math

    # Make Matplotlib use a Cairo backend
    import matplotlib
    matplotlib.use("cairo")
    import matplotlib.pyplot as plt

    # Create the figure
    fig = plt.figure(figsize=(6, 6))

    # Create a basic plot
    axes = fig.add_subplot(111)
    # xs = range(200)
    # ys = [math.sin(x/10.) for x in xs]
    # axes.plot(xs, ys)

    # Draw the graph over the plot
    # Two points to note here:
    # 1) we add the graph to the axes, not to the figure. This is because
    #    the axes are always drawn on top of everything in a matplotlib
    #    figure, and we want the graph to be on top of the axes.
    # 2) we set the z-order of the graph to infinity to ensure that it is
    #    drawn above all the curves drawn by the axes object itself.

    # Matplotlib jet colorbar not understand
    # cmap = matplotlib.cm.jet
    # norm = matplotlib.colors.Normalize(vmin=0, vmax=1)  # 自己设置
    # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # sm._A = []
    # cbar = fig.colorbar(sm)
    color = ["red" for v in graph.vs]
    for v in graph.vs:
        if v.index in dominated_set and v.index not in dominating_set:
            color[v.index] = "yellow"
        elif v.index in dominated_set and v.index in dominating_set:
            color[v.index] = "blue"

    graph_artist = GraphArtist(graph, bbox=(20, 20, 580, 580), margin=(20, 70, 20, 20),
                               vertex_color=color,
                               layout="circle")
    graph_artist.set_zorder(float('inf'))
    axes.artists.append(graph_artist)
    plt.axis("off")

    # fig.suptitle(save_path)
    fig.suptitle("GRG20")
    # Save the figure
    fig.savefig(save_path)
    plt.close(fig)

    # print("Plot saved to test.png")


def draw_graph_plot(graph, save_path="test.png", dominated_set=[], dominating_set=[]):
    """
    draw the graph to visualize
    :param dominated_set:  dominated set to color
    :param dominating_set: dominating set to color else
    :param save_path: path to save
    :param graph: graph to be drawn
    :return:
    """
    visual_style = dict()
    visual_style["vertex_color"] = ["red" for _ in graph.vs]
    for v in graph.vs:
        if v.index in dominated_set and v.index not in dominating_set:
            visual_style["vertex_color"][v.index] = "yellow"
        if v.index in dominating_set:
            visual_style["vertex_color"][v.index] = "blue"
    print(save_path, "dom", dominating_set, visual_style["vertex_color"])
    visual_style["vertex_label"] = graph.vs["name"]
    visual_style["vertex_size"] = 20
    visual_style["layout"] = "circle"
    visual_style["margin"] = 20
    plot(graph, save_path, **visual_style)
    return


def get_dominating_set():
    # graph tutorial
    vertex_num = 100
    result_path = "./dominating_graph/grg" + str(vertex_num)
    # graph = Graph.GRG(vertex_num, 0.4)  # complete graph
    # Graph.write_edgelist(graph, result_path + "_edge.txt")
    graph = Graph.Read_Edgelist(result_path+"_edge.txt", directed=False)
    graph.vs["name"] = list(range(vertex_num))
    # print(graph.vs.select(_degree=graph.maxdegree())[0])
    # print("edgelist", graph.get_edgelist())
    print("min degree of the graph is {}".format(min(graph.degree())))

    dominating_set = []
    dominated_set = []

    count = 0
    # draw_graph_matlabplot(graph, "result_path + "_edge" + str(count) + ".png", dominating_set)
    draw_graph_plot(graph, result_path + "_edge" + str(count) + ".png", dominating_set, dominated_set)
    # graph.delete_edges(3)
    for index, degree in enumerate(graph.degree()):
        # print(index, degree)
        if degree == 0:
            dominating_set.append(index)
            dominated_set.append(index)
        elif degree == 1 and index not in dominated_set:
            neighbors = graph.neighbors(vertex=index)
            dominating_set.extend(neighbors)
            dominated_set.extend(graph.neighbors(vertex=neighbors[0]))
            dominated_set.extend(neighbors)

    count += 1
    select = graph.vs.select(_degree=graph.maxdegree())[0].index
    dominated_set.append(select)
    dominated_set.extend(graph.neighbors(select))
    dominating_set.append(select)
    # adjacency_set = list(set(adjacency_set) - set(dominated_set))
    draw_graph_plot(graph, result_path + "_edge" + str(count) + ".png", dominated_set, dominating_set)

    while len(dominated_set) < vertex_num:  # dominated num smaller than whole num
        (dfs, _) = graph.dfs(select)
        new_dominating = list()
        max_vertex = None
        for vertex in dfs:
            if vertex in dominating_set:
                continue
            n_neighbors = graph.neighbors(vertex)
            n_neighbors.append(vertex)
            v_dominating = list(set(n_neighbors) - set(dominated_set))
            new_dominating = v_dominating if len(v_dominating) > len(new_dominating) else new_dominating
            max_vertex = vertex
        dominating_set.append(max_vertex)
        dominated_set.extend(new_dominating)
        count += 1
        # Graph.write_edgelist(graph, "dominating_graph/k5_edge"+str(count)+".txt")
        draw_graph_plot(graph, result_path+"_edge"+str(count)+".png", dominated_set, dominating_set)
        if count >= 100:
            break
    # print("vertex list", list(graph.vs))
    # graph.delete_edges(2)
    draw_graph_plot(graph, result_path + ".png", dominating_set=dominating_set)
    # print(graph.degree())
    # Graph.write_edgelist(graph, "k5_edge.txt")


if __name__ == "__main__":
    # draw_graph_matlabplot(graph=Graph.GRG(120, 0.2))
    get_dominating_set()
