"""
Dog Companion Behavior Sequencing System

- Modular, extensible system for sequencing dog actions and emotions.
- Receives high-level goals, outputs valid action sequences for animation.
- Handles interrupts (e.g., user input) and replans as needed.
- Polls finger sequence server for user inputs and generates dog responses.

Sections:
1. Data Structures (actions, transitions, emotions)
2. Pathfinding Logic
3. Sequence Producer
4. LLM/AI Goal Stub
5. System Loop & Interrupt Handling
6. Finger Sequence Polling
7. Test Scenarios
"""

import os
import openai
import requests
import time
import json
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
    print("This is the start action for SAP "+str(start_action))
    print("This is the end action "+str(end_action))
   
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

# New function to directly blend emotions for an action
def direct_emotion_blend(dog, action, emotions):
    dog.blend_emotions(emotions)
    return (action, dog.get_emotion_vector())


# Updated buildSequence function to use direct_emotion_blend
def buildSequence(dog, valid_goals):
    fullSequence = []
    if len(valid_goals) < 2:
        print("Single goal detected")
        action, emotions = valid_goals[0]
        # Use direct_emotion_blend instead of shortest_action_path
        fullSequence.append(direct_emotion_blend(dog, action, emotions))
        return fullSequence
        
    # Process all goals, including the last one
    for goal in valid_goals:
        print("Processing goal:", goal)
        action, emotions = goal
        fullSequence.append(direct_emotion_blend(dog, action, emotions))
    print("This is the length of the full sequence" + str(len(fullSequence)))
    return fullSequence
    

def get_llm_goals(dog_personality):    
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set.")

    personality = dog_personality.get_personality()
    emotion = dog_personality.get_emotion_vector()
   

    # Get the last user input 
    recent_inputs = dog_personality.get_user_inputs()[-1:]
    

    prompt = f"""
You are a dog with the following personality: {personality}

{rules}
"""
    userPrompt= f""" I am doing this currently {recent_inputs} I need you to react in an excited and very unique manner utilizing different commands and possibilities DO NOT JUST USE SIT AND WALK OR ELSE I WILL BEAT YOU"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
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


# 6. Finger Sequence Polling
# --------------------------
def get_finger_sequence():
    """Poll the finger sequence server for user input history"""
    try:
        response = requests.get("http://127.0.0.1:50007/get_Fingersequence", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Handle the new structure with "history" key
            if "history" in data:
                return data
            else:
                # Fallback to old structure
                return data.get("sequence", [])
        else:
            print(f"Failed to get finger sequence. Status code: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to finger sequence server: {e}")
        return {}

def parse_finger_sequence_to_user_input(finger_sequence):
    """Convert finger sequence data into meaningful user input for the LLM"""
    if not finger_sequence:
        return "No user activity detected"
    
    # Handle the new JSON structure with "history" key
    if isinstance(finger_sequence, dict) and "history" in finger_sequence:
        finger_sequence = finger_sequence["history"]
    
    # Extract the most recent actions (last 5 for better context)
    recent_actions = finger_sequence[-5:] if len(finger_sequence) >= 5 else finger_sequence
    
    # Analyze the recent actions for patterns
    keypoints = [action.get('keypoint', 'unknown') for action in recent_actions]
    point_history = [action.get('point_history', 'unknown') for action in recent_actions]
    emotions = [action.get('emotion', 'neutral') for action in recent_actions]
    emotion_strengths = [action.get('emotion_strength', 0) for action in recent_actions]
    
    # Get the most common patterns
    most_common_keypoint = max(set(keypoints), key=keypoints.count) if keypoints else "unknown"
    most_common_direction = max(set(point_history), key=point_history.count) if point_history else "unknown"
    
    # Calculate average emotion strength
    avg_emotion_strength = sum(emotion_strengths) / len(emotion_strengths) if emotion_strengths else 0
    
    # Create descriptive user input
    user_input = f"User hand gesture: {most_common_keypoint} keypoint, moving {most_common_direction}, "
    user_input += f"average emotion strength: {avg_emotion_strength:.1f}, "
    user_input += f"recent actions: {', '.join([f'{k}->{p}' for k, p in zip(keypoints[-3:], point_history[-3:])])}"
    
    return user_input

def poll_and_respond(dog, poll_interval=2.0):
    """Main polling loop that continuously monitors user inputs and generates dog responses"""
    print(f"Starting dog behavior polling system...")
    print(f"Polling finger sequence server every {poll_interval} seconds")
    print(f"Press Ctrl+C to stop")
    
    last_processed_sequence = None
    
    try:
        while True:
            # Get current finger sequence
            current_finger_sequence = get_finger_sequence()
            
            # Check if we have new data to process
            if current_finger_sequence and current_finger_sequence != last_processed_sequence:
                print(f"\n--- New user activity detected ---")
                print(f"Finger sequence: {current_finger_sequence}")
                
                # Parse finger sequence to user input
                user_input = parse_finger_sequence_to_user_input(current_finger_sequence)
                print(f"Parsed user input: {user_input}")
                
                # Process through behavior logic
                try:
                    dog_response = newInput(dog, user_input)
                    print(f"Generated dog response: {dog_response}")
                except Exception as e:
                    print(f"Error generating dog response: {e}")
                
                # Update last processed sequence
                last_processed_sequence = current_finger_sequence.copy()
            
            # Wait before next poll
            time.sleep(poll_interval)
            
    except KeyboardInterrupt:
        print("\nStopping dog behavior polling system...")

def start_polling_system(poll_interval=2.0):
    """Start the autonomous dog behavior polling system"""
    dog = DogPersonality()
    poll_and_respond(dog, poll_interval)

# 7. Test Scenarios
# -----------------
def main():
    print("Dog Companion Behavior System")
    print("=" * 40)
    print("1. Interactive Mode (manual input)")
    print("2. Polling Mode (autonomous from finger sequence server)")
    print("3. Exit")
    
    while True:
        choice = input("\nSelect mode (1-3): ").strip()
        
        if choice == "1":
            # Interactive Mode
            dog = DogPersonality()
            print("Initial personality:", dog.get_personality())
            print("Initial emotion vector:", dog.get_emotion_vector())
            
            print("\nDog Companion Interactive Mode")
            print("Type 'quit' to exit")
            
            while True:
                # Get event input
                event = input("\nEnter event (e.g., stand, sit, bark): ").strip().lower()
                if event == 'quit':
                    break
                    
                # Get intensity input
                while True:
                    try:
                        intensity = float(input("Enter intensity (0.0 to 1.0): ").strip())
                        if 0.0 <= intensity <= 1.0:
                            break
                        print("Please enter a number between 0.0 and 1.0")
                    except ValueError:
                        print("Please enter a valid number")
                
                # Create user input and process it
                user_input = {"event": event, "intensity": intensity}
                print(f"\nProcessing: {user_input}")
                newInput(dog, user_input)
                get_sequence()
        
        elif choice == "2":
            # Polling Mode
            try:
                poll_interval = float(input("Enter polling interval in seconds (default 2.0): ").strip() or "2.0")
                start_polling_system(poll_interval)
            except ValueError:
                print("Invalid interval, using default 2.0 seconds")
                start_polling_system(2.0)
        
        elif choice == "3":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main() 