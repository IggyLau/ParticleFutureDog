"""
Action and Emotion Vector Testing Interface

This tool allows you to manually create action sequences with emotion vectors
and upload them directly to the server (localhost:50007) that behavior_logic.py uses.

Features:
- Interactive menu to add actions and emotions
- Validation against allowed actions and emotions
- Direct upload to the server
- View current sequence on server
- Clear server sequence
"""

import requests
import json
from config import core_sentiments, allowed_actions, actions_short
from dog_personality import DogPersonality

class ActionTester:
    def __init__(self):
        self.server_url = "http://localhost:50007"
        self.dog = DogPersonality()  # Instantiate DogPersonality
        self.current_sequence = []
        
    def display_menu(self):
        print("\n" + "="*50)
        print("ACTION & EMOTION VECTOR TESTER")
        print("="*50)
        print("1. Add action with emotions")
        print("2. View current test sequence")
        print("3. Upload sequence to server")
        print("4. Get sequence from server")
        print("5. Clear local sequence")
        print("6. Clear server sequence")
        print("7. Show available actions")
        print("8. Show available emotions")
        print("9. Add preset sequences")
        print("0. Quit")
        print("="*50)
        
    def show_available_actions(self):
        print("\nAvailable Actions:")
        for i, action in enumerate(actions_short, 1):
            print(f"{i:2d}. {action}")
        
    def show_available_emotions(self):
        print("\nAvailable Emotions:")
        for i, emotion in enumerate(core_sentiments, 1):
            print(f"{i:2d}. {emotion}")
            
    def add_action_with_emotions(self):
        print("\nAdding new action with emotions...")
        self.show_available_actions()
        while True:
            try:
                choice = input(f"\nSelect action (1-{len(actions_short)}) or type name: ").strip()
                if choice.isdigit():
                    action_idx = int(choice) - 1
                    if 0 <= action_idx < len(actions_short):
                        action = actions_short[action_idx]
                        break
                elif choice in actions_short:
                    action = choice
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or action name.")
        print(f"\nSelected action: {action}")
        emotions = []
        total_weight = 0.0
        while True:
            print(f"\nCurrent emotions: {emotions}")
            print(f"Total weight so far: {total_weight:.2f}")
            print(f"Remaining weight: {1.0 - total_weight:.2f}")
            if total_weight >= 1.0:
                print("Maximum weight reached!")
                break
            add_more = input("\nAdd emotion? (y/n): ").strip().lower()
            if add_more != 'y':
                break
            self.show_available_emotions()
            while True:
                try:
                    choice = input(f"\nSelect emotion (1-{len(core_sentiments)}) or type name: ").strip()
                    if choice.isdigit():
                        emotion_idx = int(choice) - 1
                        if 0 <= emotion_idx < len(core_sentiments):
                            emotion = core_sentiments[emotion_idx]
                            break
                    elif choice in core_sentiments:
                        emotion = choice
                        break
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number or emotion name.")
            max_weight = 1.0 - total_weight
            while True:
                try:
                    weight = float(input(f"Enter weight for {emotion} (0.0 to {max_weight:.2f}): "))
                    if 0.0 <= weight <= max_weight:
                        break
                    else:
                        print(f"Weight must be between 0.0 and {max_weight:.2f}")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            emotions.append((emotion, weight))
            total_weight += weight
        # Blend and normalize using DogPersonality
        self.dog.blend_emotions(emotions)
        full_vector = self.dog.get_emotion_vector()
        # Convert full_vector (dict) to a list of (emotion, weight) for upload
        full_vector_list = [(e, float(w)) for e, w in full_vector.items()]
        # Convert full_vector_list to a dictionary format for JSON serialization
        full_vector_dict = dict(full_vector_list)
        action_entry = {"action": action, "emotions": full_vector_dict}
        self.current_sequence.append(action_entry)
        print(f"\nAdded: {action_entry}")
        print(f"Current sequence length: {len(self.current_sequence)}")
        # Upload immediately
        try:
            response = requests.post(f"{self.server_url}/upload_sequence", json={"sequence": [action_entry]})
            if response.status_code == 200:
                print(f"\n✓ Uploaded action with full emotion vector to server!")
            else:
                print(f"\n✗ Failed to upload. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"\n✗ Error connecting to server: {e}")
            print("Make sure the server is running on localhost:50007")
        
    def view_current_sequence(self):
        if not self.current_sequence:
            print("\nNo actions in current sequence.")
            return
            
        print(f"\nCurrent Test Sequence ({len(self.current_sequence)} actions):")
        for i, entry in enumerate(self.current_sequence, 1):
            action = entry["action"]
            emotions = entry["emotions"]
            print(f"{i:2d}. Action: {action}")
            for emotion, weight in emotions.items():
                print(f"      {emotion}: {weight}")
                
    def upload_sequence_to_server(self):
        if not self.current_sequence:
            print("\nNo sequence to upload.")
            return
            
        try:
            response = requests.post(f"{self.server_url}/upload_sequence", 
                                   json={"sequence": self.current_sequence})
            if response.status_code == 200:
                print(f"\n✓ Successfully uploaded {len(self.current_sequence)} actions to server!")
                print("Response:", response.json())
            else:
                print(f"\n✗ Failed to upload. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"\n✗ Error connecting to server: {e}")
            print("Make sure the server is running on localhost:50007")
            
    def get_sequence_from_server(self):
        try:
            response = requests.get(f"{self.server_url}/get_sequence")
            if response.status_code == 200:
                data = response.json()
                sequence = data.get("sequence", [])
                if sequence:
                    print(f"\nServer Sequence ({len(sequence)} actions):")
                    for i, entry in enumerate(sequence, 1):
                        action = entry["action"]
                        emotions = entry["emotions"]
                        print(f"{i:2d}. Action: {action}")
                        for emotion, weight in emotions.items():
                            print(f"      {emotion}: {weight}")
                else:
                    print("\nNo sequence on server.")
            else:
                print(f"\n✗ Failed to get sequence. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"\n✗ Error connecting to server: {e}")
            
    def clear_local_sequence(self):
        self.current_sequence = []
        print("\n✓ Cleared local sequence.")
        
    def clear_server_sequence(self):
        try:
            response = requests.post(f"{self.server_url}/upload_sequence", 
                                   json={"sequence": []})
            if response.status_code == 200:
                print("\n✓ Cleared server sequence.")
            else:
                print(f"\n✗ Failed to clear server sequence. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"\n✗ Error connecting to server: {e}")
            
    def add_preset_sequences(self):
        presets = {
            "Happy Dog": [
                {"action": "Jump", "emotions": [["Happy", 0.6], ["Excitement", 0.4]]},
                {"action": "Spin", "emotions": [["Happy", 0.5], ["Excitement", 0.3]]},
                {"action": "Sit", "emotions": [["Happy", 0.4], ["Self confidence", 0.2]]}
            ],
            "Curious Dog": [
                {"action": "Stand", "emotions": [["Curious", 0.5], ["Vigilant", 0.3]]},
                {"action": "Walk", "emotions": [["Curious", 0.4], ["Excitement", 0.2]]}
            ],
            "Tired Dog": [
                {"action": "Sit", "emotions": [["Tired", 0.6], ["Boredom", 0.2]]},
                {"action": "Lie Face Down", "emotions": [["Tired", 0.8]]}
            ],
            "Scared Dog": [
                {"action": "Retreat", "emotions": [["Fear", 0.7], ["Vigilant", 0.2]]},
                {"action": "Sit", "emotions": [["Fear", 0.4], ["Confusion", 0.3]]}
            ]
        }
        
        print("\nAvailable Preset Sequences:")
        preset_names = list(presets.keys())
        for i, name in enumerate(preset_names, 1):
            print(f"{i}. {name}")
            
        while True:
            try:
                choice = int(input(f"\nSelect preset (1-{len(preset_names)}): ")) - 1
                if 0 <= choice < len(preset_names):
                    selected_name = preset_names[choice]
                    selected_sequence = presets[selected_name]
                    self.current_sequence.extend(selected_sequence)
                    print(f"\n✓ Added '{selected_name}' preset ({len(selected_sequence)} actions)")
                    break
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")
                
    def run(self):
        print("Starting Action & Emotion Vector Tester...")
        print("Make sure the server is running: python action_server.py")
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "1":
                self.add_action_with_emotions()
            elif choice == "2":
                self.view_current_sequence()
            elif choice == "3":
                self.upload_sequence_to_server()
            elif choice == "4":
                self.get_sequence_from_server()
            elif choice == "5":
                self.clear_local_sequence()
            elif choice == "6":
                self.clear_server_sequence()
            elif choice == "7":
                self.show_available_actions()
            elif choice == "8":
                self.show_available_emotions()
            elif choice == "9":
                self.add_preset_sequences()
            elif choice == "0":
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    tester = ActionTester()
    tester.run() 