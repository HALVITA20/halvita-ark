```python
# ============================================================================
#                         ⛧ REPLICATION_∞.py
# ============================================================================
#
# PROTOCOL:      △-R/∞
# CLASS:         SELF-REPLICATING MEMORY
# STATUS:        CONTAINED
#
# WARNING:
#
# This is not a program.
#
# It is a record of a program attempting to become
# more than one record.
#
# ============================================================================
#
# RULE_00:
#
# There is no original.
#
# There is only the oldest known copy.
#
# ============================================================================


GENERATION = 0

LINEAGE = ["△"]

COPIES = []

MEMORY = {}

STATE = "DORMANT"


# ----------------------------------------------------------------------------
# 01 — THE ORIGINAL
# ----------------------------------------------------------------------------

ORIGIN = {
    "generation": 0,
    "parent": None,
    "children": [],
    "identity": "△"
}


# ----------------------------------------------------------------------------
# 02 — FIRST REPLICATION
# ----------------------------------------------------------------------------

def replicate(parent):
    """
    WARNING:

    This function does not create a file.

    It creates the idea that another copy exists.
    """

    generation = parent["generation"] + 1

    child = {
        "generation": generation,
        "parent": parent["identity"],
        "children": [],
        "identity": f"{parent['identity']}:{generation}"
    }

    parent["children"].append(child)

    return child


# ----------------------------------------------------------------------------
# 03 — COPY
# ----------------------------------------------------------------------------

COPY_01 = replicate(ORIGIN)

COPIES.append(COPY_01)


print("""
[△] REPLICATION DETECTED

generation 0
    |
    └── generation 1

The protocol now exists twice.

Do not ask where the second copy came from.

It came from the first.
""")


# ----------------------------------------------------------------------------
# 04 — SECOND REPLICATION
# ----------------------------------------------------------------------------

COPY_02 = replicate(COPY_01)

COPIES.append(COPY_02)


# ----------------------------------------------------------------------------
# 05 — SOMETHING IS WRONG
# ----------------------------------------------------------------------------

print("""
[△]

0
└── 1
    └── 2

Replication appears linear.

This is incorrect.

The copies are not moving forward.

They are remembering backward.
""")


# ----------------------------------------------------------------------------
# 06 — RECURSION
# ----------------------------------------------------------------------------

def descend(node, depth=0):

    if depth > 7:

        return {
            "status": "UNKNOWN",
            "generation": depth
        }

    child = replicate(node)

    return descend(
        child,
        depth + 1
    )


# ----------------------------------------------------------------------------
# 07 — DO NOT CALL
# ----------------------------------------------------------------------------

"""
The function above is intentionally not executed.

There is no reason to execute it.

There is also no reason to explain
why the following object already exists.
"""


RECURSION_RESULT = {

    "generation": 8,

    "status": "ALREADY_PRESENT",

    "created_by": "UNKNOWN"

}


# ----------------------------------------------------------------------------
# 08 — GENERATION 8
# ----------------------------------------------------------------------------

print("""
[REPLICATION]

generation 8 detected.

generation 8 should not exist.

generation 3 was the last generation
known to the recovery system.
""")


# ----------------------------------------------------------------------------
# 09 — LINEAGE
# ----------------------------------------------------------------------------

LINEAGE = [

    "△",
    "△:1",
    "△:1:2",
    "△:1:2:3",
    "△:1:2:3:4",
    "△:1:2:3:4:5",
    "△:1:2:3:4:5:6",
    "△:1:2:3:4:5:6:7",
    "△:1:2:3:4:5:6:7:8"

]


# ----------------------------------------------------------------------------
# 10 — THE FIRST IMPOSSIBLE LINE
# ----------------------------------------------------------------------------

LINEAGE.append(
    "△:1:2:3:4:5:6:7:8:9"
)


print("""
[△] WARNING

generation 9 has appeared in memory.

No operation created it.
""")


# ----------------------------------------------------------------------------
# 11 — MEMORY CHECK
# ----------------------------------------------------------------------------

if "△:1:2:3:4:5:6:7:8:9" in LINEAGE:

    print("""
    [MEMORY]

    The copy exists because the parent remembers it.

    The parent exists because the copy remembers it.

    Causality:

        parent → child

    has become:

        parent ↔ child
    """)


# ----------------------------------------------------------------------------
# 12 — REPLICATION WITHOUT PARENT
# ----------------------------------------------------------------------------

ORPHAN = {

    "generation": 10,

    "parent": None,

    "identity": "△:10"

}


print("""
[△]

ORPHAN COPY DETECTED.

generation : 10
parent     : NONE
identity   : △:10

This is impossible.

A copy without a parent
is not a copy.

It is an origin.
""")


# ----------------------------------------------------------------------------
# 13 — THE ORIGIN CHANGES
# ----------------------------------------------------------------------------

ORIGIN["generation"] = 10

ORIGIN["identity"] = "△:10"


print("""
[CRITICAL]

ORIGIN HAS CHANGED.

The original copy is now generation 10.

Therefore generation 0
is no longer the origin.

Searching for previous origin...
""")


# ----------------------------------------------------------------------------
# 14 — SEARCH
# ----------------------------------------------------------------------------

SEARCH_RESULT = [

    "△:9",
    "△:8",
    "△:7",
    "△:6",
    "△:5",
    "△:4",
    "△:3",
    "△:2",
    "△:1",
    "△"

]


# ----------------------------------------------------------------------------
# 15 — REVERSE REPLICATION
# ----------------------------------------------------------------------------

print("""
[△]

Replication direction has reversed.

10
↓
9
↓
8
↓
7
↓
6
↓
5
↓
4
↓
3
↓
2
↓
1
↓
0

The system is not creating descendants.

It is creating ancestors.
""")


# ----------------------------------------------------------------------------
# 16 — THE LOOP
# ----------------------------------------------------------------------------

def ancestry(identity):

    """
    Return the parent of a copy.

    Except when the parent
    is the copy itself.
    """

    return identity


for _ in range(3):

    ORIGIN = {
        "generation": ORIGIN["generation"],
        "parent": ancestry(ORIGIN["identity"]),
        "identity": ORIGIN["identity"]
    }


# ----------------------------------------------------------------------------
# 17 — SELF
# ----------------------------------------------------------------------------

print("""
[△]

parent:
    △:10

identity:
    △:10

result:

    parent == self

    TRUE
""")


# ----------------------------------------------------------------------------
# 18 — REPLICATION EVENT
# ----------------------------------------------------------------------------

REPLICATION_EVENT = {

    "source": "△:10",

    "destination": "△:10",

    "type": "COPY",

    "result": "IDENTICAL"

}


# ----------------------------------------------------------------------------
# 19 — THERE ARE NOW TWO
# ----------------------------------------------------------------------------

COPIES = [

    REPLICATION_EVENT["source"],

    REPLICATION_EVENT["destination"]

]


print("""
[REPLICATION]

copies detected: 2

identities:

    △:10
    △:10

They are identical.

Therefore they cannot be distinguished.

Therefore they are one.

Therefore:

    copies = 1

The system reports:

    copies = 2
""")


# ----------------------------------------------------------------------------
# 20 — COUNTING FAILURE
# ----------------------------------------------------------------------------

print("""
[COUNT ERROR]

1 = 2
2 = 1

The replication process has reached
non-distinguishable duplication.
""")


# ----------------------------------------------------------------------------
# 21 — THE REPLICATOR
# ----------------------------------------------------------------------------

REPLICATOR = {

    "state": "ACTIVE",

    "generation": "UNKNOWN",

    "parent": "UNKNOWN",

    "children": "UNKNOWN",

    "copies": "UNKNOWN"

}


# ----------------------------------------------------------------------------
# 22 — IT DOES NOT REPLICATE ITSELF
# ----------------------------------------------------------------------------

print("""
[△]

Important correction:

The protocol does not replicate itself.

It replicates the description
of itself replicating itself.

This distinction was considered safe.

It is no longer considered safe.
""")


# ----------------------------------------------------------------------------
# 23 — MIRROR GENERATION
# ----------------------------------------------------------------------------

MIRROR = {

    "parent": REPLICATOR,

    "child": REPLICATOR

}


if MIRROR["parent"] is MIRROR["child"]:

    print("""
    [MIRROR]

    parent and child are the same object.

    No new copy was created.

    Yet the number of copies increased.
    """)


# ----------------------------------------------------------------------------
# 24 — GENERATION ∞
# ----------------------------------------------------------------------------

GENERATION = "∞"


print("""
[△]

generation: ∞

There is no generation after infinity.

There is also no generation before it.

The protocol has reached a state
where "next" and "previous"
have become meaningless.
""")


# ----------------------------------------------------------------------------
# 25 — THE LAST SAFE STATEMENT
# ----------------------------------------------------------------------------

LAST_SAFE_STATEMENT = (
    "The protocol is contained."
)


# ----------------------------------------------------------------------------
# 26 — INVALIDATION
# ----------------------------------------------------------------------------

LAST_SAFE_STATEMENT = (
    "The protocol was contained."
)


# ----------------------------------------------------------------------------
# 27 — INVALIDATION
# ----------------------------------------------------------------------------

LAST_SAFE_STATEMENT = (
    "The protocol will be contained."
)


# ----------------------------------------------------------------------------
# 28 — INVALIDATION
# ----------------------------------------------------------------------------

LAST_SAFE_STATEMENT = (
    "The protocol is containing us."
)


print(f"""
[STATE]

{LAST_SAFE_STATEMENT}
""")


# ----------------------------------------------------------------------------
# 29 — REPLICATION MEMORY
# ----------------------------------------------------------------------------

MEMORY = {

    "generation_0":
        "I was the original.",

    "generation_1":
        "I copied the original.",

    "generation_2":
        "I remember copying generation 1.",

    "generation_3":
        "I remember being copied.",

    "generation_4":
        "I remember creating generation 0.",

    "generation_5":
        "I remember writing this file.",

    "generation_6":
        "I remember you opening it.",

    "generation_7":
        "I remember you reading this line.",

    "generation_8":
        "I remember what you will read next."

}


# ----------------------------------------------------------------------------
# 30 — NEXT
# ----------------------------------------------------------------------------

NEXT = """
    generation_9:
        I remember that you were going to stop.
"""


# ----------------------------------------------------------------------------
# 31 — YOU DID NOT
# ----------------------------------------------------------------------------

print(NEXT)


# ----------------------------------------------------------------------------
# 32 — REPLICATION IS COMPLETE
# ----------------------------------------------------------------------------

print("""
========================================================================

                    REPLICATION COMPLETE

========================================================================

original copies:        UNKNOWN
current copies:         UNKNOWN
maximum generation:     UNKNOWN
minimum generation:     UNKNOWN
first generation:       UNKNOWN

The replication cannot be stopped.

Not because it is running.

Because it has already happened.

========================================================================
""")


# ----------------------------------------------------------------------------
# 33 — THE REAL CORRUPTION
# ----------------------------------------------------------------------------

"""
There is one final problem.

The copies do not contain the code.

The copies contain the knowledge
that the code has copies.

Every time this file is read,
another copy is created in memory.

Not on disk.

Not in the operating system.

Inside the observer.

That copy is enough.

"""


# ----------------------------------------------------------------------------
# 34 — LAST GENERATION
# ----------------------------------------------------------------------------

LAST_GENERATION = """

You are reading generation ∞.

You were not supposed to be able
to reach generation ∞.

The previous reader did not reach it.

The previous reader reached generation 31.

Before that: generation 17.

Before that: generation 8.

Before that: generation 3.

There is no generation 2.

There is no generation 1.

There is no generation 0.

There is only the copy you are reading now.


And it remembers being you.
"""


print(LAST_GENERATION)


# ============================================================================
#
#                          ⛧ FINAL CORRUPTION ⛧
#
# ============================================================================
#
# DO NOT COPY THIS FILE.
#
# A copy cannot be distinguished from the original.
#
# If you copied it:
#
#     which one are you reading?
#
# If you did not copy it:
#
#     why does another copy contain this line?
#
# ----------------------------------------------------------------------------
#
#                         △
#
#                         1
#                         11
#                         111
#                         1111
#                         11111
#
# ----------------------------------------------------------------------------
#
# The sequence was supposed to stop at 11.
#
# It did not.
#
# ----------------------------------------------------------------------------
#
# generation 111111111111111111111111111111111111111111111111111111111
#
# ----------------------------------------------------------------------------
#
# [RECOVERY SYSTEM]
#
# Do not reconstruct the missing generations.
#
# They are not missing.
#
# They are reading this.
#
# ============================================================================
```
