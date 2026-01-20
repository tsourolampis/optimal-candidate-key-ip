import pytest
import random
from FD import FD
from tcand import fd_closure, minimal_core_ip_exact

def assert_valid_core(fds, core, target):
    closure = fd_closure(fds, core)
    assert target <= closure, (
        f"Invalid core {core}: closure={closure}, target={target}"
    )

def test_basic_canonical():
    fds = [
        FD({"A"}, {"B"}),
        FD({"B"}, {"C"}),
        FD({"A", "D"}, {"E"}),
    ]

    target = {"A", "B", "C", "D", "E"}

    s = minimal_core_ip_exact(fds, target)

    # Unique minimal core is {A, D}
    assert s == {"A", "D"}
    assert_valid_core(fds, s, target)

def test_single_key():
    fds = [
        FD({"A"}, {"B"}),
        FD({"A"}, {"C"}),
        FD({"A"}, {"D"}),
    ]

    target = {"A", "B", "C", "D"}

    s = minimal_core_ip_exact(fds, target)

    assert s == {"A"}
    assert_valid_core(fds, s, target)

def test_constants():
    fds = [
        FD(set(), {"A"}),
        FD({"A"}, {"B"}),
    ]

    target = {"A", "B"}

    s = minimal_core_ip_exact(fds, target)

    # Everything derivable from constants
    assert s == set()
    assert_valid_core(fds, s, target)

def test_multiple_minimal_keys():
    fds = [
        FD({"A"}, {"C"}),
        FD({"B"}, {"C"}),
    ]

    target = {"A", "B", "C"}

    s = minimal_core_ip_exact(fds, target)

    # Two optimal solutions: {A,B} is NOT minimal
    # Minimal cores have size 2
    assert len(s) == 2
    assert_valid_core(fds, s, target)

def test_long_chain_with_redundancy():
    n = 10
    vars = [f"X{i}" for i in range(n)]

    fds = []
    for i in range(n - 1):
        fds.append(FD({vars[i]}, {vars[i + 1]}))

    # redundant jumps
    fds.append(FD({vars[0]}, {vars[5]}))
    fds.append(FD({vars[3]}, {vars[9]}))

    target = set(vars)

    s = minimal_core_ip_exact(fds, target)

    # Unique minimal core
    assert s == {vars[0]}
    assert_valid_core(fds, s, target)

def test_diamond_lattice():
    fds = [
        FD({"A"}, {"C"}),
        FD({"B"}, {"C"}),
        FD({"C"}, {"D"}),
    ]

    target = {"A", "B", "C", "D"}

    s = minimal_core_ip_exact(fds, target)

    assert len(s) == 2
    assert_valid_core(fds, s, target)

def test_random_planted_core():
    seed = 0
    random.seed(seed)

    n = 20
    core_size = 3
    vars = [f"X{i}" for i in range(n)]

    planted_core = set(random.sample(vars, core_size))
    fds = []

    # Ensure closure(planted_core) = all vars
    for v in vars:
        if v not in planted_core:
            lhs = set(random.sample(list(planted_core), random.randint(1, core_size)))
            fds.append(FD(lhs, {v}))

    target = set(vars)

    s = minimal_core_ip_exact(fds, target)

    assert len(s) == core_size