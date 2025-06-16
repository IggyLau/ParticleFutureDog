
core_sentiments = [
    "Happy",
    "Sad",
    "Curious",
    "Vigilant",
    "Fear",
    "Intimacy",
    "Confusion",
    "Self confidence",
    "Boredom",
    "Grievances",
    "Excitement",
    "Tired"
]

action_transitions = {
    "Super Stand": ["Stand"],
    "Stand": ["Super Stand", "Sit", "Jump", "Walk", "Spin", "Kick", "Shake", "Jump", "Retreat", "Downward Dog"],
    "Sit": ["Stand", "Downward Dog", "Lie Face Down"],
    "Lie Face Down": ["Lie Face Up", "Roll", "Sit"],
    "Lie Face Up": ["Lie Face Down", "Roll", "Sit"],
    "Walk": ["Stand", "Spin", "Retreat"],
    "Spin": ["Stand", "Walk"],
    "Paw Up": ["Sit"],
    "Kick": ["Stand"],
    "Shake": ["Stand"],
    "Roll": ["Lie Face Down", "Lie Face Up"],
    "Jump": ["Stand"],
    "Retreat": ["Stand", "Walk"],
    "Downward Dog": ["Stand", "Sit"]
}

actions_short = ["Stand",
    "Sit",
    "Lie",
    "Walk",
    "Jump",
    "Eat",
    "Bark",
    "Roll",
    "ChaseTail",
    "JumpAndPaw",
    "PawUp",
    "LickPaw",
    "PlayDead"]

states=["Stand","Sit","Lie","Walk"]

allowed_actions = list(action_transitions.keys())

max_goals=5

rules = f"""
Just like a real dog you will respond to the users actions and inputs, but will also have a mind and personality of your own.
I want you to think of a personal goal and intent the dog is trying to achieve through these actions.
Your task is to plan the next 1 to {max_goals} actions to demonstrate your intent. 

For each action:
- Select two emotions from this list: {core_sentiments}
- Assign a weight to each emotion (between 0 and 1)
- Use higher weights for more extreme/intense actions, but never exceed a total of 1.0 per action
- Each emotion average should be around 0.25 for standard actions and based on the user intensity of input. Not every action emotion needs to add up to 1.0, it just cannot exceed it.
- Only use actions from this list: {actions_short}
- Output a list of 1 to {max_goals} in the following format:
  [
  ("Action1", [("Emotion1", weight1), ("Emotion2", weight2)]),
  ("Action2", [("Emotion3", weight3), ("Emotion4", weight4)]),
  ]
- Do not use any actions or emotions outside the allowed lists.
- Do not include any explanation or extra text, only the list."""

