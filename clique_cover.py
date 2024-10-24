import subprocess
from argparse import ArgumentParser

class Input_Handler():
    def __init__(self):
        self.nodes_count = 0
        self.min_clique_num = 0
        self.edges_count = 0
        self.complete_graph_edges_count = 0
        self.edges = []

    def load_instance(self, input_file_name):
        with open(input_file_name, 'r') as file:
            self.nodes_count = int(next(file))       # first line represents nodes (n)
            self.min_clique_num = int(next(file))    # second line represents clique cover number to test (k)
            for edge in file:                        # rest are edges
                edge = edge.split()
                if edge:
                    edge = [int(vertex) for vertex in edge]
                    # append only new edges, doesn't matter what the order is, because the graph is undirected
                    if edge not in self.edges and [edge[1],edge[0]] not in self.edges:  
                        self.edges.append([edge[0],edge[1]])

        self.complete_graph_edges_count = (self.nodes_count * (self.nodes_count - 1)) // 2
        self.edges_count = len(self.edges)

        # debugging
        #print("n (nodes): " + str(self.nodes_count))
        #print("k (min clique number): " + str(self.min_clique_num))
        #print("m (edges): " + str(self.edges_count))
        #print("complete graph count: " + str(self.complete_graph_edges_count))
        #print("Edges are: ", self.edges)

    def check_for_valid_input(self):
        # k <= n && k > 0
        if self.min_clique_num > self.nodes_count or self.min_clique_num < 0:
            print(f"Invalid input: k ({self.min_clique_num}) must be <= to n ({self.nodes_count}) and > 0")
            exit(1)

        # m <= (n(n-1)) / 2
        if self.edges_count > self.complete_graph_edges_count:
            print(f"Invalid input: m ({self.edges_count}) must be <= number of edges in complete graph of n-nodes ({self.complete_graph_edges_count})")
            exit(1)
        
        # if one of the vertex indices are out of bounds
        for edge in self.edges:
            if (edge[0] > self.nodes_count) or (edge[0] <= 0) or (edge[1] > self.nodes_count) or (edge[1] <= 0):
                print(f"Invalid vertex index: vertex indices must be ranging from 1-{self.nodes_count}")
                exit(1)
                
        # there cant be loop edges on the input
        for edge in self.edges:
            if (edge[0] == edge[1]):
                print(f"Invalid vertex index: loop edges are not allowed")
                exit(1)

class Encoder():
    def __init__(self, graph):
        self.graph = graph

    def encode(self):
        cnf = []
        n = graph.nodes_count
        k = graph.min_clique_num # number of colors
        complement_edges = self.graph.get_complement_edges()
        variables_count = n*k

        ### CONSTRAINTS

        # each vertex must have a color
        for vertex in range(1, n + 1):
            clause = []
            for color in range(1, k + 1):
                clause.append(self.vertex_of_color_ID(vertex, color)) # for each vertex: vertex(color)
            clause.append(0) # add zero to have correct dimacs format clause
            cnf.append(clause)

        # each vertex can be of at most of one color
        for vertex in range(1, n + 1):
            for color1 in range(1, k + 1):
                for color2 in range(color1 + 1, k + 1):
                    cnf.append([-self.vertex_of_color_ID(vertex, color1), -self.vertex_of_color_ID(vertex, color2), 0]) # for each vertex: not vertex(color1) or not vertex(color2)

        # no adjacent vertices can be of the same color
        for (u,v) in complement_edges:
            for color in range(1, k + 1):
                cnf.append([-self.vertex_of_color_ID(u, color), -self.vertex_of_color_ID(v, color), 0]) # for edge between vertices 'u' and 'v': not u(color) or not v(color)

        return (cnf, variables_count)

    # create a unique id representing truth for vertex 'vertex' to be of color 'color'
    def vertex_of_color_ID(self, vertex, color):
        return ((vertex - 1) * self.graph.min_clique_num) + color;


class SAT_Solver():
    def __init__(self, solver_name, verbosity):
        self.solver_name = solver_name
        self.verbosity = verbosity

    def call_solver(self, output_file_name, cnf, variables_count):
        clauses_count = len(cnf)

        # print CNF into formula.cnf in DIMACS format
        with open(output_file_name, 'w') as file:
            file.write("p cnf " + str(variables_count) + " " + str(clauses_count) + '\n')
            for clause in cnf:
                file.write(' '.join(str(literal) for literal in clause) + '\n')

        # call the solver and return the output
        return subprocess.run(['./' + self.solver_name, '-model', '-verb=' + str(self.verbosity) , output_file_name], stdout=subprocess.PIPE)

    def print_result(self, result, graph):
        # print the whole output of the SAT solver to stdout, so you can see the raw output for yourself
        for line in result.stdout.decode('utf-8').split('\n'):
            print(line)

        # check the returned result
        if (result.returncode == 20):       # returncode for SAT is 10, for UNSAT is 20
            print("Given input is unsatisfiable")
            return

        # parse the model from the output of the solver
        # the model starts with 'v'
        model = []
        for line in result.stdout.decode('utf-8').split('\n'):
            if line.startswith("v"):    # there might be more lines of the model, each starting with 'v'
                vars = line.split(" ")
                vars.remove("v")
                model.extend(int(v) for v in vars) 

        if 0 in model:
            model.remove(0) # 0 is the end of the model, just ignore it

        print()
        print("###################################################################")
        print("###########[ Human readable result of the clique cover ]###########")
        print("###################################################################")
        print()

        # decode the meaning of the assignment
        cliques = []
        for i in range(graph.min_clique_num + 1):
            cliques.append([])

        for vertex in range(1, graph.nodes_count + 1):
            for color in range(1, graph.min_clique_num + 1):
                var_id = ((vertex - 1) * graph.min_clique_num) + color  # get variable ID for this vertex and color
                if var_id in model:                                     # check if it is in the model and if so, add it to clique of color 'color'
                    cliques[color].append(vertex)

        # print the cliques of individual colors
        print("Given input is satisfiable, here are the cliques:")
        i = 1
        for clique in cliques:
            if clique:
                print(f"Clique of color {i} consists of vertices: ", end="")
                print(*clique)
                i += 1

class Graph():
    def __init__(self, nodes_count, edges, min_clique_num):
        self.nodes_count = nodes_count
        self.edges = edges
        self.min_clique_num = min_clique_num

    def get_complement_edges(self):
        complement_edges = []

        for i in range(1, self.nodes_count + 1):
            for j in range(2, self.nodes_count + 1):
                if [i,j] not in self.edges and [j,i] not in self.edges and i != j:
                    complement_edges.append([i,j])

        # debugging
        #print("Complement edges are: ", complement_edges)

        return complement_edges

if __name__ == "__main__": 
    
    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="instances/input.in",
        type=str,
        help=(
            "The instance file."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file for the DIMACS format (i.e. the CNF formula)."
        ),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help=(
            "The SAT solver to be used."
        ),
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=0,
        type=int,
        choices=range(0,2),
        help=(
            "Verbosity of the SAT solver used."
        ),
    )
    args = parser.parse_args()

    # load the input and check for validity
    input_handler = Input_Handler()
    instance = input_handler.load_instance(args.input)
    input_handler.check_for_valid_input()

    # create graph for encoder to use
    graph = Graph(input_handler.nodes_count, input_handler.edges, input_handler.min_clique_num)

    # encode the instance
    encoder = Encoder(graph)
    cnf, variables_count = encoder.encode()

    # call the SAT solver and get the result
    sat_solver = SAT_Solver(args.solver, args.verb)
    result = sat_solver.call_solver(args.output, cnf, variables_count)

    # print the result so in readable form
    sat_solver.print_result(result, graph)
