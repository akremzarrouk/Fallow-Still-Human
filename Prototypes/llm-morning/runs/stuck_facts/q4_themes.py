"""The themes of q4_names.py, as regular expressions on one prompt line (copied from q4_names.py so that importing prints nothing)."""
THEMES = {
    "DANIEL": r"\bDaniel\b",
    "NIGHT": (r"went (there|out|to the neighbour)|neighbour's house (tonight|and see)|going out|\bcrossed?\b|\bshould go\b|"
              r"means to go|go out|into the night|came back|front door being opened|nothing in his hands|bed was empty"),
    "CAN": r"\bthe can\b|taking it|took the can|denied taking|denying it",
    "FIGHT": r"accus|confront|\bangry\b|\bfight|quarrel|argu",
    "TOGETHER": r"together|\bapart\b|family (whole|safe)|keeping the family|closeness|reassur|stay calm|stay together",
}
