# Optimal Candidate Key in Relational Schemas


## Overview

This project computes a **minimum (candidate) key** of a relational schema given a set of **functional dependencies (FDs)**. A **key** is a set of attributes that functionally determines all attributes in the relation.

Given:
- a finite set of attributes $R$, and
- a set of functional dependencies $\mathcal{F}$,

the goal is to find the **smallest subset of attributes**

$$
K \subseteq R
$$
such that the **closure** of $K$ under $\mathcal{F}$ equals the entire schema:
$$
K^+_{\mathcal{F}} = R.
$$

The project implements an integer program that provably yields the key of smallest cardinality.  

- ✔ Correctness: the returned set is a valid key.
- ✔ Minimum size: instead of the usual guarantee that no strict subset is also a key, the IP returns the key of smallest possible cardinality.

## Use Cases

- Relational schema design and normalization
- Database theory research and teaching
- Query Optimization
