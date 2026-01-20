from __future__ import annotations

from typing import Set, List, Dict, TypeVar, Tuple

from pyomo.environ import (
    ConcreteModel,
    Var,
    Objective,
    Constraint,
    ConstraintList,
    Binary,
    minimize,
    SolverFactory,
    value,
)

from .FD import FunctionalDependency as FD, get_all_vars

T = TypeVar("T")

def fd_closure(
    fds: List[FD],
    vars: Iterable[T],
) -> Set[T]:
    """
    Compute the FD-closure of vars with respect to fds.
    Returns only the closure set.
    """

    closure: Set[T] = set(vars)
    remaining = [len(fd.keys) for fd in fds]
    waiting: dict[T, List[int]] = {}

    for i, fd in enumerate(fds):
        if not fd.keys:
            closure |= set(fd.values)
        else:
            for v in fd.keys:
                waiting.setdefault(v, []).append(i)

    queue = list(closure)
    idx = 0

    while idx < len(queue):
        v = queue[idx]
        idx += 1

        for fd_id in waiting.get(v, []):
            remaining[fd_id] -= 1
            if remaining[fd_id] == 0:
                for u in fds[fd_id].values:
                    if u not in closure:
                        closure.add(u)
                        queue.append(u)

    return closure

def preprocess_fds_ip(
    fds: List[FD[T]],
) -> Tuple[List[FD[int]], List[T], Dict[T, int], Dict[int, T]]:
    """
    - Decompose each FD to the form LS->singleton variable
    - Rename variables to integers 1..n
    - Return the renamed FDs, original variable list, and mappings
      var_to_id and id_to_var.
    """
    fd_vars = sorted(get_all_vars(fds))

    # Decompose RHS
    new_fds: List[FD[T]] = []
    for f in fds:
        for u in f.values:
            new_fds.append(FD(f.keys, {u}))

    # Renaming
    var_to_id: Dict[T, int] = {v: i + 1 for i, v in enumerate(fd_vars)}
    id_to_var: Dict[int, T] = {i + 1: v for i, v in enumerate(fd_vars)}

    renamed_fds: List[FD[int]] = []
    for f in new_fds:
        LS = {var_to_id[x] for x in f.keys}
        RS = {var_to_id[next(iter(f.values))]}
        renamed_fds.append(FD(LS, RS))

    return renamed_fds, fd_vars, var_to_id, id_to_var

def minimal_core_ip_exact(
    fds: List[FD[T]],
    target: Set[T],
    solver_name: str = "glpk",
    solver_executable: str | None = None,
    tee: bool = False,
    sanity_check: bool = False,
) -> Set[T]:
    """
    Semantics:
      x[r,i] is the value/presence of variable i after r iterations of applying rules (FDs),
      where x[r,i] = OR( x[r-1,i], OR_{(LS->i)} AND_{j in LS} x[r-1,j] ).
      The AND is encoded via auxiliary variables z[r,fd].
      We also set x[R, t] = 1 for all t in target (mapped to ids). Setting R=n suffices for the optimal solution.

    Objective:
      minimize sum_i x[0,i]

    Returns:
      A provably minimal core (over original symbols) whose FD-closure covers `target`.
    """
    # Preprocess
    new_fds, fd_vars, var_to_id, id_to_var = preprocess_fds_ip(fds)

    isolated = set(target) - set(fd_vars)      # targets not appearing in any FD must be chosen
    target_in = set(target) & set(fd_vars)

    if not target_in:
        return set(isolated)
    if len(target_in) == 1:
        return set(target_in) | set(isolated)

    n = len(fd_vars)
    R = n  # n iterations suffice
    q = len(new_fds)

    # Map RHS variable u -> list of fd indices producing u
    fd_dict: Dict[int, List[int]] = {}
    for idx, fd in enumerate(new_fds):
        u = next(iter(fd.values))
        fd_dict.setdefault(u, []).append(idx)

    # --- model ---
    m = ConcreteModel()

    # x[r,i] for r=0..R, i=1..n
    m.x = Var(range(R + 1), range(1, n + 1), domain=Binary)

    # z[r,fd] for r=0..R-1 (firing between r and r+1)
    m.z = Var(range(R), range(q), domain=Binary)

    m.cons = ConstraintList()

    for r in range(1, R + 1):
        for fd_id, fd in enumerate(new_fds):
            LS = fd.keys
            # let's encode the AND logic for the z variables
            #   z[r-1, fd_id] = AND_{j in LS} x[r-1, j]
            for j in LS:
                m.cons.add(m.z[r - 1, fd_id] <= m.x[r - 1, j])

            m.cons.add(
                m.z[r - 1, fd_id]
                >= sum(m.x[r - 1, j] for j in LS) - (len(LS) - 1)
            )

        #   For each variable u, encode:
        #   x[r,u] = OR( x[r-1,u], OR_{fd: fd -> u} z[r-1,fd] )
        for u in range(1, n + 1):
            firing_fds = fd_dict.get(u, [])

            m.cons.add(m.x[r, u] >= m.x[r - 1, u])
            for fd_id in firing_fds:
                m.cons.add(m.x[r, u] >= m.z[r - 1, fd_id])

            m.cons.add(
                m.x[r, u]
                <= m.x[r - 1, u] + sum(m.z[r - 1, fd_id] for fd_id in firing_fds)
            )

    # Target coverage at final round
    for t in target_in:
        m.cons.add(m.x[R, var_to_id[t]] == 1)

    # Objective: minimize initial variables
    m.obj = Objective(expr=sum(m.x[0, i] for i in range(1, n + 1)), sense=minimize)

    # Solve
    if solver_executable is None:
        solver = SolverFactory(solver_name)
    else:
        solver = SolverFactory(solver_name, executable=solver_executable)

    res = solver.solve(m, tee=tee)

    # Extract core: variables selected at round 0
    eps=1e-6
    sol_core = {id_to_var[i] for i in range(1, n + 1) if value(m.x[0, i]) >= 1.0 - eps}
    sol = set(sol_core) | set(isolated)

    if sanity_check:
        assert target <= fd_closure(fds, sol), f"Sanity check failed: closure(sol) does not cover target. sol={sol}"

    return sol
