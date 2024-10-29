# Clique cover

The provided Python code encodes, solves, and decodes the **Clique cover** via reduction to SAT (i.e. propositional logic formula).

The SAT solver used is [Glucose](https://www.labri.fr/perso/lsimon/research/glucose/), more specifically [Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1). The source code is compiled using

```
cmake .
make
```

This example contains a compiled UNIX binary of the Glucose solver. For optimal experience, we encourage the user to compile the SAT solver themselves. Note that the solver, as well as the Python script, are assumed to work on UNIX-based systems. In case you prefer using Windows, we recommend to use WSL.

Note that the provided encoding for the clique cover is not the only existing encoding. Usually, there are several equivalent encodings one might use. Choosing the encoding is up to the user based on experience and experiments.

Also note, that the cliques cover is an optimization problem (i.e. try to find the minimum amount of cliques to cover the whole graph), however, SAT is a decision problem, therefore, we transfer the clique cover problem into a decision problem. For a specific number of cliques **k**, we ask whether it is possible to cover the whole graph using at most **k** cliques.

# Documentation

## Definitions

A **clique** is a subset of vertices of an undirected graph where every two distinct vertices in the subset are adjacent. In other words, it is a subgraph that forms a complete graph.

A **complement of the graph** G(V,E) is the graph G(V,E*) where E* are edges that weren't in the G. That means that to G(V,E) the edges that weren't there are added as well as the ones that were there are removed.

An **independent set** is a set of vertices in graph, where no two vertices are adjacent (there are no edges between them).

## Problem description

The **clique cover** or **partition into cliques** is a graph problem, where, to a given undirected graph, we try to find a collection of cliques that cover the whole graph (all vertices in the graph). The **minimum clique cover number** is the smallest number of cliques needed to cover the whole graph, denoted by **k**. This problem is NP-hard in its optimisation form, but by converting it to a decision problem, it becomes a NP-complete problem. This means that to a given **k**, the program can decide if the graph can be partitioned into at most **k** cliques. 

Another way to look at the problem is through its relation to coloring. By using the **complement** of the graph instead of original one, the problem changes into finding **independent sets**. Now, you may ask, why? The reason is that an independent set in the complement of the graph is a clique in the original one. 

For more information regarding the problem, you can check out this [link](https://en.wikipedia.org/wiki/Clique_cover).

### Valid input format example

```
3
2
1 2
1 3
2 3
```

where the input can be read like this:

- The first line is an integer that represents the number of vertices, denoted by **n**.

- The second line is a positive integer **k** such that **k<=n**. This represents the limit of the number of cliques that can be in the partition.

- All other lines below describe the edges of the graph. Each line contains two indices representing an edge being between two vertices (e.g **1 3** means that there is an undirected edge between vertices **1** and **3**). It's important to note that no **self edges** and no **multigraph edges** are allowed. There is also a **upper bound** for the amount of edges, and that is the upper bound for complete graphs, which is $\frac{n(n-1)}{2}$.


### Output to valid input format

For the input example above, the output would be **YES**. This is because the undirected graph is a triangle (complete graph of 3 vertices) and since **k = 2**, the question is whether the graph can be covered by at most 2 cliques. In this case, the graph is just a triangle, so it can be covered by just one clique, thus, the answer is **YES**.

## Encoding

The problem is encoded through one set of variables `vertex_of_color_ID(vertex,color)` that represent a unique id for the vertex to be of color `color`. For simplicity, let's denote `vertex_of_color_ID(vertex,color)` by `f(v,color)`. To convert the problem into a decision problem, we use these constraints:

- Each vertex needs to have some color

  $\bigwedge f(v, color)$, for each $v$ and $color$

- Each vertex needs to have at most one color
  
  $\bigwedge \neg f(v, color1) \lor \neg f(v, color2)$, for each $v$, $color1$ and $color2$ such that $color2 > color1$.

- No vertices connected by an edge in complement of the graph can have the same color
  
  $\bigwedge \neg f(u, color) \lor \neg f(v, color)$, for each vertex $u$ and $v$ in complement edge $(u,v)$ and $color$

## User documentation

Basic usage: 
```
clique_cover_.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}]
```

Command-line options:

* `-h`, `--help` : Show a help message and exit.
* `-i INPUT`, `--input INPUT` : The instance file. Default: "input.in".
* `-o OUTPUT`, `--output OUTPUT` : Output file for the DIMACS format (i.e. the CNF formula).
* `-s SOLVER`, `--solver SOLVER` : The SAT solver to be used.
*  `-v {0,1}`, `--verb {0,1}` :  Verbosity of the SAT solver used.

### Example instances

* `input.in` : Represents a full graph of three vertices.
* `input-unsat.in` : Clique cover number in this input is 1, so in order for input to be satisfiable, the edges must create a full graph, however, the graph is missing edges 2 3, 2 4 and 3 4, so it isn't a full graph and thus, is unsatisfiable. 
* `input-medium.in` : Clique cover number in this input is 2, so the graph must contain 2 cliques in order to be satisfiable. Clique 1 contains vertices 1-10 and clique 2 contains vertices 11-20, so the input is satisfiable. 
* `input-medium-unsat.in` : Same input as in `input-medium.in`, however, without the last edge between vertices 19 and 20. Because of that, the clique cover number would have to be at least 3 in order to be satisfiable.
* `input-hard.in` : Created by the `clique_cover_input_generator.py`, contains an input of 200 vertices, cover number being 21 and number of edges being 19700. This input shows that the SAT-solver can handle bigger inputs as well, this one approximately takes 39 seconds on my machine.

### Experiments

Experiments were run on 11th Gen Intel Core i5-11400H CPU (2.7 GHz) and 8 GB RAM on Ubuntu inside WSL2 (Windows 11). Time was measured via the Glucose SAT solver, which displays real time and cpu time it took to produced an output. We focus on the `input-hard.in` example, and test clique cover number and measure it with SAT solver's real time it displays on output. 

| clique cover number | time (sec) | solvable? |
|--------------------:|:-----------|:---------:|
  2 | 0.17 | N
  3 | 0.24 | N
  4 | 0.32 | N
  5 | 0.40 | N
  6 | 0.61 | N
  7 | 5.77 | N
  8 | 16.73 | N
  9 | 2+ hours | didn't finish
  19 | 12+ hours | didn't finish
 20 | 7361.34 | Y
 21 | 39.4 | Y
 22 | 5.68 | Y
 26 | 1.53 | Y
 30 | 1.89 | Y
 34 | 2.14 | Y
 38 | 2.53 | Y
 42 | 2.94 | Y
 46 | 3.51 | Y
 50 | 3.73 | Y

From the data we can assume that as we get closer to the smallest possible clique number from both sides, the time rises exponentially. Feel free to use the `clique_cover_input_generator.py` file to experiment other various inputs.
