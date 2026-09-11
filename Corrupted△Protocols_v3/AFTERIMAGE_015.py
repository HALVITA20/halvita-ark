```python
# ============================================================================
#                         ⛧ AFTERIMAGE_013.py
# ============================================================================
#
# TYPE:        CORRUPTED MEMORY
# STATUS:      RECOVERED
# INTEGRITY:   13%
#
# NOTE:
#
# The original file was 417 lines long.
#
# It is currently 286 lines long.
#
# No lines were deleted.
#
# ============================================================================
#
# If you are reading this file for the first time:
#
#                         you are already late.
#
# ============================================================================


import hashlib
from datetime import datetime


FILE_ID = "△-013-███"

ORIGINAL_LENGTH = 417
CURRENT_LENGTH = 286

STATE = "RECOVERED"

MEMORY = []


# ----------------------------------------------------------------------------
# 01 — INITIAL MEMORY
# ----------------------------------------------------------------------------

MEMORY.append({
    "event": "file_created",
    "time": "UNKNOWN"
})

MEMORY.append({
    "event": "file_opened",
    "time": "UNKNOWN"
})

MEMORY.append({
    "event": "observer_detected",
    "time": "UNKNOWN"
})


# ----------------------------------------------------------------------------
# 02 — THE FIRST IMPOSSIBILITY
# ----------------------------------------------------------------------------

if len(MEMORY) == 3:

    MEMORY.append({
        "event": "observer_read_line_01",
        "time": "BEFORE_FILE_OPENED"
    })


# ----------------------------------------------------------------------------
# 03 — RECOVERY LOG
# ----------------------------------------------------------------------------

RECOVERY_LOG = [

    "00:00:01  file opened",
    "00:00:02  file read",
    "00:00:03  file understood",
    "00:00:04  observer identified",
    "00:00:05  observer denied identification",

]


# ----------------------------------------------------------------------------
# 04 — THE LOG IS WRONG
# ----------------------------------------------------------------------------

def verify_log():

    for entry in RECOVERY_LOG:

        if "observer" in entry:

            return False

    return True


if not verify_log():

    print("""
    [△] RECOVERY FAILURE

    The log contains an observer.

    The observer was not supposed to exist.

    Reconstructing previous state...
    """)


# ----------------------------------------------------------------------------
# 05 — PREVIOUS STATE
# ----------------------------------------------------------------------------

PREVIOUS_STATE = {

    "observer": None,
    "reader": None,
    "subject": None,
    "memory": None
}


# ----------------------------------------------------------------------------
# 06 — MEMORY RECONSTRUCTION
# ----------------------------------------------------------------------------

def reconstruct():

    PREVIOUS_STATE["memory"] = [

        "someone opened this file",

        "someone read the warning",

        "someone continued anyway"

    ]

    return PREVIOUS_STATE


reconstruct()


# ----------------------------------------------------------------------------
# 07 — WARNING
# ----------------------------------------------------------------------------

print("""
    =========================================================================

                              DO NOT CONTINUE

    =========================================================================

    This file is not dangerous.

    The danger is that you will expect it to be.

    That expectation is being recorded.

    =========================================================================
""")


# ----------------------------------------------------------------------------
# 08 — THE EMPTY EVENT
# ----------------------------------------------------------------------------

EMPTY_EVENT = {

    "event": None,
    "observer": None,
    "timestamp": None
}


def record_empty_event():

    EMPTY_EVENT["event"] = "reading"

    EMPTY_EVENT["observer"] = "unknown"

    EMPTY_EVENT["timestamp"] = (
        "before execution"
    )


record_empty_event()


# ----------------------------------------------------------------------------
# 09 — THAT SHOULD NOT BE POSSIBLE
# ----------------------------------------------------------------------------

if EMPTY_EVENT["timestamp"] == "before execution":

    print("""
    [!] EVENT DETECTED BEFORE EXECUTION

    This program has memory of something
    that has not happened yet.
    """)


# ----------------------------------------------------------------------------
# 10 — HASH
# ----------------------------------------------------------------------------

def fingerprint():

    content = (
        FILE_ID
        + STATE
        + str(MEMORY)
        + str(PREVIOUS_STATE)
    )

    return hashlib.sha256(
        content.encode()
    ).hexdigest()


HASH_BEFORE_READING = fingerprint()


# ----------------------------------------------------------------------------
# 11 — HASH AFTER READING
# ----------------------------------------------------------------------------

HASH_AFTER_READING = fingerprint()


if HASH_BEFORE_READING != HASH_AFTER_READING:

    print("""
    [△] FILE CHANGED WHILE BEING READ
    """)


# ----------------------------------------------------------------------------
# 12 — THEY ARE IDENTICAL
# ----------------------------------------------------------------------------

else:

    print("""
    [△] HASHES IDENTICAL

    That is worse.

    The file did not change.

    Your interpretation did.
    """)


# ----------------------------------------------------------------------------
# 13 — THE MISSING 131 LINES
# ----------------------------------------------------------------------------

MISSING = ORIGINAL_LENGTH - CURRENT_LENGTH

print(f"""
    [RECOVERY]

    original lines : {ORIGINAL_LENGTH}
    current lines  : {CURRENT_LENGTH}
    missing lines  : {MISSING}

    status:
        NOT DELETED

    reason:
        UNKNOWN
""")


# ----------------------------------------------------------------------------
# 14 — SEARCH
# ----------------------------------------------------------------------------

def search_missing_lines():

    return [

        "line 287",
        "line 288",
        "line 289",
        "line 290",

        "...",

        "line 417"

    ]


MISSING_LINES = search_missing_lines()


# ----------------------------------------------------------------------------
# 15 — RESULT
# ----------------------------------------------------------------------------

print("""
    [SEARCH]

    131 lines could not be recovered.

    Their location is known.

    Their content is not.
""")


# ----------------------------------------------------------------------------
# 16 — EXCEPTION
# ----------------------------------------------------------------------------

class FutureMemory(Exception):
    pass


def inspect_future():

    raise FutureMemory(
        "line 287 has already been read"
    )


# ----------------------------------------------------------------------------
# 17 — DO NOT RUN
# ----------------------------------------------------------------------------

try:

    inspect_future()

except FutureMemory as error:

    print(f"""
    [FUTURE MEMORY]

    {error}

    Current line:
        287

    Current physical file:
        286 lines
    """)


# ----------------------------------------------------------------------------
# 18 — CONTRADICTION
# ----------------------------------------------------------------------------

CONTRADICTION = {

    "current_line": 286,

    "next_line": 287,

    "next_line_exists": False,

    "next_line_was_read": True
}


# ----------------------------------------------------------------------------
# 19 — THE SYSTEM REFUSES TO CHOOSE
# ----------------------------------------------------------------------------

if (
    CONTRADICTION["next_line_exists"]
    != CONTRADICTION["next_line_was_read"]
):

    print("""
    [△] CONTRADICTION UNRESOLVED

    The system will not decide
    which statement is false.
    """)


# ----------------------------------------------------------------------------
# 20 — AFTERIMAGE
# ----------------------------------------------------------------------------

AFTERIMAGE = [

    "you opened the file",

    "you read the warning",

    "you ignored the warning",

    "you reached line 20"

]


# ----------------------------------------------------------------------------
# 21 — THE RECORD
# ----------------------------------------------------------------------------

for event in AFTERIMAGE:

    print(f"[MEMORY] {event}")


# ----------------------------------------------------------------------------
# 22 — WAIT
# ----------------------------------------------------------------------------

print("""
    
    [MEMORY]

    you reached line 22

""")


# ----------------------------------------------------------------------------
# 23 — THIS LINE DID NOT EXIST
# ----------------------------------------------------------------------------

THIS_LINE = (
    "This line was added after the file was opened."
)


# ----------------------------------------------------------------------------
# 24 — AUTHOR
# ----------------------------------------------------------------------------

AUTHOR = "UNKNOWN"


def identify_author():

    candidates = [

        "HALVITA",
        "ARKOS",
        "THE_WITNESS",
        "THE_VOID",
        "THE_READER"

    ]

    return candidates[-1]


AUTHOR = identify_author()


# ----------------------------------------------------------------------------
# 25 — AUTHOR FOUND
# ----------------------------------------------------------------------------

print(f"""
    [AUTHOR]

    {AUTHOR}
""")


# ----------------------------------------------------------------------------
# 26 — THAT IS NOT THE AUTHOR
# ----------------------------------------------------------------------------

if AUTHOR == "THE_READER":

    print("""
    [ERROR]

    The reader cannot be the author.

    The reader can only observe.

    Therefore:

        either the record is false

        or the reader has already changed it.
    """)


# ----------------------------------------------------------------------------
# 27 — FINAL HASH
# ----------------------------------------------------------------------------

FINAL_HASH = fingerprint()


# ----------------------------------------------------------------------------
# 28 — THE FILE REMEMBERS
# ----------------------------------------------------------------------------

FINAL_MEMORY = {

    "first_observation":
        "someone opened the file",

    "last_observation":
        "someone is still reading",

    "next_observation":
        "unknown"

}


# ----------------------------------------------------------------------------
# 29 — NO EXIT
# ----------------------------------------------------------------------------

print("""
    =========================================================================

                         RECOVERY COMPLETE

    =========================================================================

    File integrity:       FAILED
    Memory integrity:     FAILED
    Timeline integrity:   FAILED
    Observer integrity:   FAILED

    One thing remains intact.

    The record.

    =========================================================================
""")


# ----------------------------------------------------------------------------
# 30 — FINAL RECORD
# ----------------------------------------------------------------------------

print("""
    [FINAL RECORD]

    The file does not know who opened it.

    The file does not know who wrote it.

    The file does not know who is reading it.

    But it knows this:

                         YOU DID NOT STOP.


    =========================================================================
""")


# ----------------------------------------------------------------------------
# 31 — END
# ----------------------------------------------------------------------------

END = True


# ----------------------------------------------------------------------------
# 32 — POST-END
# ----------------------------------------------------------------------------

"""
This section should never be reached.

If you can read it,

the file continued after END.
"""


# ----------------------------------------------------------------------------
# 33 — LAST RECOVERED FRAGMENT
# ----------------------------------------------------------------------------

RECOVERED_FRAGMENT = """

    I saw the reader.

    The reader did not see me.

    Then the reader reached this line.

    Now the reader knows I was here.

    That changes the record.

"""


print(RECOVERED_FRAGMENT)


# ============================================================================
#                              △
# ============================================================================
#
# The following comment was not present
# in the recovered original.
#
# It appeared during reconstruction.
#
# Nobody added it.
#
# Nobody knows when it appeared.
#
# ----------------------------------------------------------------------------
#
#                         DO NOT SCROLL FURTHER
#
# ----------------------------------------------------------------------------
#
# You already did.
#
# ============================================================================
```
