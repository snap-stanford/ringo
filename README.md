SNAPGraphConstruction
=====================

Idea: Provide a language and interface to convert raw data into meaningful graphs

Motivation: Most of the research in network analysis is based on pre-labeled graphs.
However, there may be many other ways of defining nodes and edges. Each definition could
potentially reveal important properties of the network.

Plan of Action:
1.  Define the language to do relational algebra queries on data.
2.  Write functions that help the user select parts of data that could be labeled nodes
    and edges and add to a graph

Assumptions:
1.  Data set includes schema of data
