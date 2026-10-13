"""The prompt sections, shared by q3_fixed.py and q4_names.py (copied from q3_fixed.py so that importing prints nothing)."""
HEADERS = [  # (line start, section) in the order they appear in a prompt
    ("You are the first to act", "now"),
    ("You are ", "sheet"), ("How you address them:", "sheet"), ("Who you are:", "sheet"), ("Temperament:", "sheet"),
    ("What matters to you:", "sheet"),
    ("Your body:", "body and 'About' lines"), ("About ", "body and 'About' lines"),
    ("Against ", "grudge lines"), ("On your conscience", "grudge lines"),
    ("The house:", "house"),
    ("What you remember from the days before:", "days before"),
    ("What stays with you from earlier days:", "carry-in: earlier days"),
    ("Yesterday and last night:", "carry-in: yesterday and last night"),
    ("What yesterday left in you", "carry-in: what yesterday left in you"),
    ("What you are sure of", "sure lines"),
    ("Your own last words", "own last words"),
    ("What else happened", "memory (what else happened)"),
    ("Nobody in the kitchen has said anything since", "T line"),
    ("You last spoke with", "now: meeting lines (world.py:1166)"),
    ("Now, ", "now"),
    ("You are the first to act", "now"),
    ("What you have been doing:", "pattern line"),
    ("Your options:", "options"),
]

def sections(prompt):
    out, cur = [], None
    for l in prompt.split("\n"):
        for start, name in HEADERS:
            if l.startswith(start) and not (start == "About " and cur in ("days before",) ) :
                # "- ..." lines never start with these; header lines only
                cur = name; break
        out.append((cur, l))
    return out

