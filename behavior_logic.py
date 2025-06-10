"""
Dog Companion Behavior Sequencing System

- Modular, extensible system for sequencing dog actions and emotions.
- Receives high-level goals, outputs valid action sequences for animation.
- Handles interrupts (e.g., user input) and replans as needed.

Sections:
1. Data Structures (actions, transitions, emotions)
2. Pathfinding Logic
3. Sequence Producer
4. LLM/AI Goal Stub
5. System Loop & Interrupt Handling
6. Test Scenarios
"""

import os
import openai
from dog_personality import DogPersonality
from config import core_sentiments, action_transitions, rules, allowed_actions


# 1. Data Structures
# ------------------
# Action transition map: to_action -> list of from_actions
# This defines all legal transitions between dog states/actions.
# Edge definitions: list of (from_action, to_action) tuples for all valid transitions


from collections import deque
# Ok now I also need to call normalization on emotions here, then also append the emotion vector to each action
from collections import deque

def shortest_action_path(dog, start_action, end_action, emotionAction):
    if start_action == dog.get_action():
        dog.blend_emotions(emotionAction)
        return [(start_action, dog.get_emotion_vector())]
    
    queue = deque()
    # Start with initial emotions
    dog.blend_emotions(emotionAction)
    initial_emotions = dog.get_emotion_vector().copy()
    queue.append((start_action, [(start_action, initial_emotions)]))
    visited = set([start_action])

    while queue:
        current_action, path_so_far = queue.popleft()
        for next_action in action_transitions.get(current_action, []):
            if next_action == end_action:
                # Update emotions for the final action
                dog.blend_emotions(emotionAction)
                return path_so_far + [(next_action, dog.get_emotion_vector())]
            if next_action not in visited:
                visited.add(next_action)
                # Update emotions for this action
                dog.blend_emotions(emotionAction)
                current_emotions = dog.get_emotion_vector().copy()
                queue.append((next_action, path_so_far + [(next_action, current_emotions)]))
    return None

def buildSequence(dog, valid_goals):
    fullSequence = []
    if len(valid_goals) < 2:
        print("Single goal detected")
        action, emotions = valid_goals[0]
        # Use the dog instance
        dog.blend_emotions(emotions)
        fullSequence.append((action, dog.get_emotion_vector()))
        
        return fullSequence
        
    for i in range(len(valid_goals)-1):
        
        path = shortest_action_path(dog, valid_goals[i][0], valid_goals[i+1][0], valid_goals[i][1])
        if path:
            fullSequence.extend(path)
    print ("This is the length"+str(len(fullSequence)))
    return fullSequence
    

def get_llm_goals(dog_personality):    
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set.")

    personality = dog_personality.get_personality()
    emotion = dog_personality.get_emotion_vector()
   

    # Summarize the last 3 user inputs for the LLM prompt
    recent_inputs = dog_personality.get_user_inputs()[-3:]
    if recent_inputs:
        user_input_str = "Recent user interactions:\n" + "\n".join(
            f"- {ui['event']} (intensity: {ui.get('intensity', 'n/a')})" for ui in recent_inputs
        )
    else:
        user_input_str = "No recent user interactions."

    prompt = f"""
You are a dog with the following personality: {personality}

{rules}
"""
    userPrompt= f""" I am doing this currently {recent_inputs}"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": userPrompt}
                ],
            max_tokens=512,
            temperature=0.7,
        )
        content = response.choices[0].message.content.strip()
        return parse_llm_goal_output(content, allowed_actions, core_sentiments)
    except Exception as e:
        raise RuntimeError(f"Failed to get valid LLM goals: {e}")

# 5. System Loop & Interrupt Handling
# -----------------------------------
def newInput(dog, user_input):
    dog.add_user_input(user_input)
    valid_goals=get_llm_goals(dog)
    fullSequence=buildSequence(dog, valid_goals)
    
    json_ready_sequence = [{"action": act, "emotions": emos} for (act, emos) in fullSequence]
    print("JsonSequence:", json_ready_sequence)
    upload_sequence(json_ready_sequence)
    return json_ready_sequence

import requests

def upload_sequence(sequence):
    response = requests.post("http://localhost:50007/upload_sequence", json={"sequence": sequence})
    return response.json()

def get_sequence():
    response = requests.get("http://localhost:50007/get_sequence")
    data=response.json()
    print ("Data:", data)
    return data["sequence"]

import ast

def parse_llm_goal_output(content, allowed_actions, allowed_emotions, max_goals=3):
    # Remove code fencing if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]
    # Only grab substring that is a list
    start = content.find('[')
    end = content.rfind(']')
    if start == -1 or end == -1:
        raise ValueError("No valid list in LLM output.")
    content = content[start:end+1]
    # Parse as Python literal (list of tuples)
    try:
        goals = ast.literal_eval(content)
    except Exception as e:
        raise ValueError(f"Could not parse LLM output as Python data: {e}")
    if isinstance(goals, tuple):  # Make singletons into list
        goals = [goals]
    if not isinstance(goals, list):
        raise ValueError("Parsed LLM output is not a list.")

    valid_goals = []
    for item in goals:
        if not (isinstance(item, tuple) and len(item) == 2):
            continue
        action, emotions = item
        if action not in allowed_actions:
            continue
        if (
            isinstance(emotions, list) and
            1 <= len(emotions) <= 10 and  # You can set max number if you wish
            all(
                isinstance(e, tuple) and len(e) == 2 and
                e[0] in allowed_emotions and
                isinstance(e[1], (float, int))
                for e in emotions
            )
        ):
            total_weight = sum(float(e[1]) for e in emotions)
            if 0.0 <= total_weight <= 1.05:  # A small buffer for float math
                valid_emotions = [(e[0], float(e[1])) for e in emotions]
                valid_goals.append((action, valid_emotions))

    if not (1 <= len(valid_goals) <= max_goals):
        raise RuntimeError("LLM output did not meet valid goal constraints.")
    print("Valid goals:", valid_goals)
    return valid_goals


# 6. Test Scenarios
# -----------------
def main():
    
    import json
    import time
    
    # 1. Initialize DogPersonality
    dog = DogPersonality()
    print("Initial personality:", dog.get_personality())
    print("Initial emotion vector:", dog.get_emotion_vector())

    # 2. Simulate user input (e.g., user pets the dog)
    user_input_1 = {"event": "walks into the room", "intensity": 0.3}
    newInput(dog, user_input_1)
    get_sequence()

    

if __name__ == "__main__":
    main() 