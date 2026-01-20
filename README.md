# Optimal Candidate Key in Relational Schemas using Integer Programming


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

The details can be found in the paper [Targeted Least Cardinality Candidate Key for Relational Database](https://tsourakakis.com/wp-content/uploads/2024/08/tcand.pdf) that appeared in ICDT 2025.

## Use Cases

- Relational schema design and normalization
- Database theory research and teaching
- Query Optimization


## How to run

This project uses a `src/` layout, `pyproject.toml` for packaging, and `pytest` for testing. Assuming you have macOS / Linux
create a virtual environment.

1.  `python3 -m venv .venv`
2. Activate it `source .venv/bin/activate`.
3. Install using `pip install -e .[dev]`
4. Run a quick import check `python -c "from tcand import minimal_core_ip_exact; print('OK')"`
5. If you haven't installed GLPK run `brew install glpk`.
6. Run all tests using `pytest -v`


