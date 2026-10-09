"""Writes streetdata/lines.json, the stranger's words at the door in W2a (reports/w2_design.md, §4.3; amendment 3:
at least 8 variants per slot). Run once from Prototypes/llm-morning/."""
import json

P = lambda *xs: [{"text": x} for x in xs]
C = lambda x: {"text": x, "with": "child"}
O = lambda x: {"text": x, "with": "others"}
slots = {
    "voice_ask_water": P(
        "Hello? I'm sorry to knock. I've run out of water. Could you spare a little? Even a cup would help.",
        "I'm sorry, I know nobody's opening doors. I haven't had a drink since yesterday. Have you any water at all?",
        "Please, it's only water I'm after. A cup or a bottle, whatever you can spare.",
        "I won't come in. I just need water. Mine ran out and the taps are dry.",
        "Sorry to bother you. Is there any water in the house you could spare? I've nothing left.",
        "Hello. I'm not here to cause trouble. I'm out of water, that's all. Could you spare some?",
        "I heard voices, so I knocked. I've no water left. Anything you could spare, I'd be grateful.",
        "It's water. I need water. A little, if you have it. I'm sorry to ask.") + [
        C("Please, I've a little one at home and no water left to give her. Just a cup, if you can."),
        O("Hello? There's a few of us at home and the water's gone. Whatever you can spare.")],
    "voice_ask_food": P(
        "Hello? I'm sorry to knock. Have you anything to eat you could spare? Anything at all.",
        "I haven't eaten in days. I'm not asking for much. A tin, a bit of bread, whatever you have.",
        "Please, if there's any food you can spare, I'd be grateful. I won't come in.",
        "Sorry to bother you. My food ran out. Is there anything at all you could let me have?",
        "I'm not here for trouble. I'm hungry, that's all. Have you anything to spare?",
        "I heard voices, so I knocked. I've nothing left to eat. Could you spare a little?",
        "Is anybody in? I'm sorry. I've had nothing to eat for days. Anything would help.",
        "It's food I'm asking for. Only a little. I'm sorry, I know it's hard for everyone.") + [
        C("Please, my little one hasn't eaten properly in days. Anything you could spare, for the child."),
        O("Hello? There's a few of us at home and the food's gone. Could you spare anything at all?")],
    "open_ask_water": P(
        "Thank you for opening. I've had no water since yesterday. A bottle would see me through.",
        "Thank you. I didn't think anyone would open. Could you spare some water? Only a little.",
        "Oh, thank you. I won't keep you. It's water I need, whatever you can manage.",
        "Thank you for opening the door. I'm out of water. A cup, a bottle, anything.",
        "I'm grateful you opened. I've nothing left to drink. Could you fill one of these for me?",
        "Thank you. I know what it costs to open a door now. I just need some water.",
        "Hello. Thank you. I'm sorry, I'll be quick. Have you any water to spare?",
        "Thank you for opening. My water's gone and the taps are dry. Anything would help.") + [
        C("Thank you for opening. My little girl's had nothing to drink since this morning. Just a little water."),
        O("Thank you. There's a few of us at home with no water left. Whatever you can spare.")],
    "open_ask_food": P(
        "Thank you for opening. I've had nothing to eat in days. Anything you could spare.",
        "Thank you. I didn't think anyone would open. Have you any food? Even a little.",
        "Oh, thank you. I won't keep you. It's food I need, whatever you can manage.",
        "Thank you for opening the door. I've run out of food. Anything at all would help.",
        "I'm grateful you opened. I'm hungry, that's all. A tin, some bread, anything.",
        "Thank you. I know what it costs to open a door now. I just need something to eat.",
        "Hello. Thank you. I'm sorry, I'll be quick. Have you any food to spare?",
        "Thank you for opening. My food's gone. I'm not asking for much, just something.") + [
        C("Thank you for opening. My boy hasn't had a proper meal in days. Anything at all, for him."),
        O("Thank you. There's a few of us at home and nothing left to eat. Whatever you can spare.")],
    "insist_water": P(
        "Please. Just a cup.",
        "Please, I'm begging you. A little water. I won't ask again.",
        "I'm asking once more, that's all. Please, any water.",
        "Please. I'm so thirsty I can hardly think. Just a little.",
        "Anything. A mouthful. Please.",
        "I wouldn't ask if I had anywhere else to go. Please, some water.",
        "Please. I've tried other doors. Nobody answers.",
        "Just a cup, please. Then I'll go.") + [
        C("Please. Just a cup. For the child.")],
    "insist_food": P(
        "Please. Anything at all.",
        "Please, I'm begging you. A little food. I won't ask again.",
        "I'm asking once more, that's all. Please, anything to eat.",
        "Please. I'm so hungry I can hardly stand.",
        "A crust. Anything. Please.",
        "I wouldn't ask if I had anywhere else to go. Please, something to eat.",
        "Please. I've tried other doors. Nobody answers.",
        "Just a little, please. Then I'll go.") + [
        C("Please. Anything. For the child.")],
    "again_water": P(
        "I'm still here. I only want a little water, if you can spare it.",
        "I'll wait a moment, if that's all right. Just some water.",
        "I'm not going to cause trouble. It's only water I'm asking for.",
        "Did you hear me? I'm asking for a little water, that's all.",
        "Sorry. I'm still here. Any water at all?",
        "I understand if you can't. I'm just asking for some water.",
        "I'll not keep you long. A little water, if you have it.",
        "Hello? I'm still at the door. It's water I need."),
    "again_food": P(
        "I'm still here. I only want a little food, if you can spare it.",
        "I'll wait a moment, if that's all right. Just something to eat.",
        "I'm not going to cause trouble. It's only food I'm asking for.",
        "Did you hear me? I'm asking for a little food, that's all.",
        "Sorry. I'm still here. Anything to eat at all?",
        "I understand if you can't. I'm just asking for something to eat.",
        "I'll not keep you long. A bite to eat, if you have it.",
        "Hello? I'm still at the door. It's food I need."),
    "given": P(
        "God bless you. I won't forget this.",
        "Thank you. Thank you. I'll not forget it.",
        "Oh, thank you. You don't know what this means.",
        "Thank you. Look after yourselves in there.",
        "Bless you. I'll go now. Thank you.",
        "Thank you. I'll not tell anyone where it came from.",
        "That's more than I hoped for. Thank you.",
        "Thank you, truly. Stay safe."),
    "refused_polite": P(
        "I understand. I'm sorry to have bothered you. Look after yourselves.",
        "All right. I understand. Take care in there.",
        "That's all right. I'm sorry I asked. Goodbye.",
        "I understand. Everyone's in the same boat. I'll go.",
        "Right. I'm sorry. I'll try somewhere else.",
        "Of course. I'm sorry I knocked. Take care.",
        "I understand. Good luck to you.",
        "No, I understand. I'm sorry. I'll leave you be."),
    "refused_flat": P(
        "Right. Never mind.",
        "Fine.",
        "Right. Thanks for nothing.",
        "I see. Well. I'll go, then.",
        "Suit yourselves.",
        "Right. I won't bother you again.",
        "Fine. I'll find it somewhere else.",
        "Right. Goodbye, then."),
}
doc = {"about": ("The stranger's words at the family's door in W2a (reports/w2_design.md, §4.3), written by hand once, "
                 "before any run. Code chooses a line by slot, by the visiting household (`with`: only for a household "
                 "with a child, or of two or more), and by the string <seed>:street:<household>:visit<n>:<slot>. Rules: "
                 "at most 25 words; no digit, number word, weekday or house number; nothing the family's world does not "
                 "have; a request, never a duty; a line states a need the household really has."),
       "slots": slots}
with open("streetdata/lines.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
    f.write("\n")
print({k: len(v) for k, v in slots.items()})
