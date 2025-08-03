"""
Text-Based Dog Companion
========================

A standalone version of the dog companion that responds to written text input.
This version focuses on natural language interaction with your AI dog.

Usage:
    python text_dog_companion.py

Features:
- Natural language text input
- Emotional responses based on your words
- Persistent dog personality
- Action sequences with emotion vectors
- Server integration for Unity/animation systems
"""

import os
import openai
import requests
import json
from dog_personality import DogPersonality
from config import core_sentiments, rules, allowed_actions, actions_short

class TextDogCompanion:
    def __init__(self):
        self.server_url = "http://localhost:50007"
        self.dog = DogPersonality()
        
    def get_llm_goals_from_text(self, user_text):    
        """
        Generate dog actions based on written text input.
        """
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY environment variable not set.")

        # Initialize the OpenAI client with the new API
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        personality = self.dog.get_personality()
        
        # Get the last few user inputs for context
        recent_inputs = self.dog.get_user_inputs()[-3:]
        
        prompt = f"""
You are a dog with the following personality: {personality}

{rules}
"""
        
        userPrompt = f"""The human said to me: "{user_text}"

Recent conversation context: {recent_inputs}

I need to react as a dog would to this human communication. Consider:
- The tone and emotion in their words
- What they might want me to do
- How I should respond based on my personality
- Whether they're being friendly, commanding, playful, or emotional

React in an authentic dog-like manner with varied and creative actions!"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": userPrompt}
                    ],
                max_tokens=512,
                temperature=0.7,
            )
            content = response.choices[0].message.content.strip()
            return self.parse_llm_goal_output(content)
        except Exception as e:
            raise RuntimeError(f"Failed to get valid LLM goals from text: {e}")

    def parse_llm_goal_output(self, content, max_goals=3):
        """Parse LLM output into valid action-emotion pairs"""
        import ast
        
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
            
            # Check if action is in allowed actions
            if action not in actions_short:  # Use actions_short for validation
                continue
                
            if (
                isinstance(emotions, list) and
                1 <= len(emotions) <= 10 and
                all(
                    isinstance(e, tuple) and len(e) == 2 and
                    e[0] in core_sentiments and
                    isinstance(e[1], (float, int))
                    for e in emotions
                )
            ):
                total_weight = sum(float(e[1]) for e in emotions)
                if 0.0 <= total_weight <= 1.05:  # A small buffer for float math
                    valid_emotions = [(e[0], float(e[1])) for e in emotions]
                    valid_goals.append((action, valid_emotions))

        if not (1 <= len(valid_goals) <= max_goals):
            raise ValueError(f"Invalid number of goals: {len(valid_goals)}")

        return valid_goals

    def direct_emotion_blend(self, action, emotions):
        """Directly blend emotions for an action"""
        self.dog.blend_emotions(emotions)
        return (action, self.dog.get_emotion_vector())

    def build_sequence(self, valid_goals):
        """Build action sequence from LLM goals"""
        full_sequence = []
        
        if len(valid_goals) < 2:
            action, emotions = valid_goals[0]
            full_sequence.append(self.direct_emotion_blend(action, emotions))
            return full_sequence
            
        # Process all goals
        for goal in valid_goals:
            action, emotions = goal
            full_sequence.append(self.direct_emotion_blend(action, emotions))
            
        return full_sequence

    def upload_sequence(self, sequence):
        """Upload sequence to server"""
        try:
            response = requests.post(f"{self.server_url}/upload_sequence", 
                                   json={"sequence": sequence})
            return response.json()
        except requests.exceptions.RequestException:
            print("⚠️  Could not connect to server (server may not be running)")
            return None

    def process_text_input(self, user_text):
        """
        Process written text input and generate dog response sequence.
        """
        print(f"\n🐕 Processing: '{user_text}'")
        
        # Add the text input to dog's history
        self.dog.add_user_input(user_text)
        
        try:
            # Get LLM goals based on text input
            valid_goals = self.get_llm_goals_from_text(user_text)
            print(f"📋 Generated {len(valid_goals)} actions: {[goal[0] for goal in valid_goals]}")
            
            # Build the action sequence
            full_sequence = self.build_sequence(valid_goals)
            
            # Convert to JSON format
            json_ready_sequence = [{"action": act, "emotions": emos} for (act, emos) in full_sequence]
            
            print("🎭 Dog's response sequence:")
            for i, entry in enumerate(json_ready_sequence, 1):
                action = entry["action"]
                top_emotions = sorted(entry["emotions"].items(), key=lambda x: x[1], reverse=True)[:3]
                emotion_str = ", ".join([f"{e}: {w:.2f}" for e, w in top_emotions])
                print(f"   {i}. {action} ({emotion_str})")
            
            # Upload to server if available
            self.upload_sequence(json_ready_sequence)
                
            return json_ready_sequence
            
        except Exception as e:
            print(f"❌ Error processing text: {e}")
            return None

    def run(self):
        """Main interaction loop"""
        print("🐕 Text-Based Dog Companion")
        print("=" * 50)
        print("Talk to your AI dog using natural language!")
        print("\n💡 Example phrases to try:")
        print("  • 'Good boy! Come here!'")
        print("  • 'I'm feeling sad today'")
        print("  • 'Want to play fetch?'")
        print("  • 'Time for dinner!'")
        print("  • 'Sit! Stay!'")
        print("  • 'You're such a good dog!'")
        print("  • 'I had a terrible day'")
        print("  • 'Let's go for a walk!'")
        print("\nType 'quit' to exit, 'emotions' to see current state")
        print("=" * 50)
        
        print(f"\n🐕 Your dog's personality: {self.dog.get_personality()}")
        
        while True:
            # Get text input from user
            user_text = input("\n💬 Say something to your dog: ").strip()
            
            if user_text.lower() == 'quit':
                print("🐕 *wags tail goodbye* Woof!")
                break
            
            if user_text.lower() == 'emotions':
                print(f"\n📊 Dog's current emotional state:")
                top_emotions = self.dog.get_top_emotions(5)
                for emotion, weight in top_emotions:
                    bar_length = int(weight * 20)  # Visual bar
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    print(f"   {emotion:15s} |{bar}| {weight:.3f}")
                continue
            
            if not user_text:
                print("🐕 *tilts head* (Please say something!)")
                continue
            
            # Process the text input
            result = self.process_text_input(user_text)
            
            if result:
                print(f"\n📊 Dog's emotional response:")
                top_emotions = self.dog.get_top_emotions(3)
                for emotion, weight in top_emotions:
                    print(f"   {emotion}: {weight:.2f}")

def main():
    """Run the text-based dog companion"""
    companion = TextDogCompanion()
    companion.run()

if __name__ == "__main__":
    main() 