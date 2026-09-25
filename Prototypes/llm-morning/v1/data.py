"""The family, the house and what happened before the morning.

Copied by hand from the shipped data so the prototype never reads Assets/:
  people      Assets/_Project/Data/Minds/*.json (age, role, note, traits, values, hunger rate)
  house       Assets/_Project/Data/Scenario/morning.json (the kitchen and the private rooms)
  start       morning.json `start` and `opening`, variant daniel_ate_it
  backstory   Assets/_Project/Data/Scenario/backstory.json (who did, saw or heard each event)
Ages and family roles match Docs/understanding/target-morning.md. Nothing else from that
file is used anywhere in the prototype.
"""

ORDER = ["daniel", "elena", "leo", "mara"]

PEOPLE = {
    "daniel": {
        "name": "Daniel", "age": 25, "role": "the eldest son", "role_short": "eldest son",
        "note": "Older brother. Takes charge because he is frightened, not because he is sure. "
                "Proud, poor at reading a room, genuinely protective. Believes responsibility "
                "is his by right of age.",
        "traits": {"cautious": 0.35, "dominant": 0.85, "empathetic": 0.5, "impulsive": 0.6,
                   "proud": 0.85, "anxious": 0.65, "honest": 0.5},
        "values": ["being in control", "being respected", "keeping the family safe"],
        "hunger": 0.55, "hunger_rate": 1.15,
    },
    "elena": {
        "name": "Elena", "age": 42, "role": "the mother", "role_short": "mother",
        "note": "Mother. Reads everyone, says little, holds it in. Will lie to keep the family "
                "whole. Fears the household breaking apart more than she fears the outside.",
        "traits": {"cautious": 0.7, "dominant": 0.5, "empathetic": 0.9, "impulsive": 0.25,
                   "proud": 0.35, "anxious": 0.75, "honest": 0.7},
        "values": ["keeping the family safe", "closeness", "fairness"],
        "hunger": 0.60, "hunger_rate": 0.85,
    },
    "leo": {
        "name": "Leo", "age": 21, "role": "the younger son", "role_short": "younger son",
        "note": "Calm, rational, reads people well, knows survival. Annoyance shows as "
                "withdrawal and dry correction, not volume.",
        "traits": {"cautious": 0.7, "dominant": 0.35, "empathetic": 0.7, "impulsive": 0.2,
                   "proud": 0.5, "anxious": 0.25, "honest": 0.8},
        "values": ["keeping the family safe", "fairness", "deciding for yourself", "closeness"],
        "hunger": 0.45, "hunger_rate": 1.0,
    },
    "mara": {
        "name": "Mara", "age": 17, "role": "the youngest, the daughter", "role_short": "youngest",
        "note": "Younger sister. Frightened and easy to read, but old enough to resent being "
                "handled like a child. Everything she feels reaches her face before she decides "
                "to show it.",
        "traits": {"cautious": 0.5, "dominant": 0.25, "empathetic": 0.75, "impulsive": 0.7,
                   "proud": 0.55, "anxious": 0.8, "honest": 0.55},
        "values": ["closeness", "deciding for yourself", "fairness"],
        "hunger": 0.50, "hunger_rate": 0.95,
    },
}

ROOMS = {
    "kitchen": "kitchen",
    "brothers_room": "brothers room",
    "back_room": "back room",
    "bathroom": "bathroom",
}
ROOM_NOTES = {
    "kitchen": "the food is kept here",
    "brothers_room": "Daniel and Leo's room",
    "back_room": "Elena and Mara's room",
    "bathroom": "nothing is heard in or out of it",
}
# Voices carry between rooms, but not into or out of the bathroom (morning.json: the
# only connection that is not audible is the bathroom's).
SOUNDPROOF = {"bathroom"}

PORTIONS = 2
MINUTES = 90
MINUTES_PER_TURN = 3

HOUSE = ("The family has shut itself in the house. The water has stopped. Food is short. "
         "Rooms: " + "; ".join(f"{ROOMS[r]} ({ROOM_NOTES[r]})" for r in ROOMS) + ".")

# (day, summary, {person: "did" | "saw" | "heard"}); people not listed were not there.
EVERYONE_SAW = {p: "saw" for p in ORDER}
BACKSTORY = [
    (1, "Daniel boards the front windows on his own while the others watch.",
     {**EVERYONE_SAW, "daniel": "did"}),
    (1, "Leo says the water will stop running within a day and they should fill everything they have.",
     {**EVERYONE_SAW, "leo": "did"}),
    (2, "The taps run dry, exactly as Leo said they would.", EVERYONE_SAW),
    (2, "Daniel says they should cross to the neighbour's house tonight and see what is left there.",
     {**EVERYONE_SAW, "daniel": "did"}),
    (2, "Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. "
        "Daniel drops it.", {**EVERYONE_SAW, "leo": "did"}),
    (2, "Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his.",
     {**EVERYONE_SAW, "daniel": "did"}),
    (2, "Elena counts what is left in the pantry with Mara beside her.", {"elena": "did", "mara": "saw"}),
    (3, "Mara cries in the night. Elena sits with her until it stops.",
     {"elena": "did", "mara": "saw", "leo": "heard"}),
    (3, "Mara freezes in the doorway with something moving in the street. Daniel picks her up and "
        "carries her inside.", {**EVERYONE_SAW, "daniel": "did"}),
    # The variant daniel_ate_it: nobody saw it.
    (3, "In the night Daniel eats a can standing at the counter in the dark. Nobody sees.",
     {"daniel": "did"}),
    (4, "Leo says maybe they should let someone else handle this one.", {**EVERYONE_SAW, "leo": "did"}),
    (4, "Daniel empties Mara's bag onto the bed while she is standing there.",
     {"daniel": "did", "elena": "saw", "mara": "saw"}),
    (4, "Elena says she is quite sure nobody in this house would take food from the others.",
     {**EVERYONE_SAW, "elena": "did"}),
]
CULPRIT = "daniel"

OPENING = "Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left."
