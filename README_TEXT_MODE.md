# Text-Based Dog Companion Usage Guide

## Overview
The text-based dog companion allows you to interact with your AI dog using natural language instead of finger gestures. The dog will respond with appropriate actions and emotions based on what you say.

## How to Run

### Option 1: Integrated Mode (Updated behavior_logic.py)
```bash
python behavior_logic.py
```
Then select option "2. Text Input Mode (natural language)"

### Option 2: Standalone Mode (New file)
```bash
python text_dog_companion.py
```

## Features

### 🗣️ Natural Language Input
Talk to your dog using everyday phrases:
- **Commands**: "Sit!", "Come here!", "Stay!"
- **Praise**: "Good boy!", "You're such a good dog!"
- **Emotions**: "I'm feeling sad today", "I'm so happy!"
- **Activities**: "Want to play fetch?", "Time for dinner!", "Let's go for a walk!"
- **Reactions**: "Bad dog! No!", "That was amazing!"

### 🎭 Emotion-Driven Responses
The dog's actions are accompanied by emotion vectors that change based on:
- **Your tone**: Friendly vs. stern commands
- **Your emotions**: The dog empathizes with your feelings
- **Context**: Previous interactions influence responses
- **Personality**: The dog's consistent personality traits

### 📊 Emotion Visualization
Type `emotions` to see the dog's current emotional state with visual bars:
```
📊 Dog's current emotional state:
   Happy          |████████████████░░░░| 0.832
   Curious        |██████░░░░░░░░░░░░░░| 0.124
   Excitement     |██░░░░░░░░░░░░░░░░░░| 0.044
```

### 🔄 Action Sequences
The dog responds with sequences of actions, each with associated emotions:
```
🎭 Dog's response sequence:
   1. Jump (Happy: 0.45, Excitement: 0.35)
   2. Bark (Excitement: 0.55, Curious: 0.25)
   3. SitIdle (Happy: 0.60, Self confidence: 0.20)
```

## Example Interactions

### Positive Interaction
```
💬 Say something to your dog: Good boy! You're the best dog ever!

🐕 Processing: 'Good boy! You're the best dog ever!'
📋 Generated 2 actions: ['Jump', 'SitIdle']
🎭 Dog's response sequence:
   1. Jump (Happy: 0.65, Excitement: 0.30)
   2. SitIdle (Happy: 0.70, Self confidence: 0.25)
```

### Emotional Support
```
💬 Say something to your dog: I had a terrible day at work

🐕 Processing: 'I had a terrible day at work'
📋 Generated 2 actions: ['Walk', 'LickPaw']
🎭 Dog's response sequence:
   1. Walk (Intimacy: 0.40, Curious: 0.20)
   2. LickPaw (Intimacy: 0.50, Happy: 0.15)
```

### Playful Interaction
```
💬 Say something to your dog: Want to play fetch?

🐕 Processing: 'Want to play fetch?'
📋 Generated 3 actions: ['Jump', 'Bark', 'ChaseTail']
🎭 Dog's response sequence:
   1. Jump (Excitement: 0.55, Happy: 0.35)
   2. Bark (Excitement: 0.60, Curious: 0.25)
   3. ChaseTail (Excitement: 0.50, Happy: 0.40)
```

## Available Actions
The dog can perform these actions:
- **Basic**: Sit, Lie, Walk, Jump
- **Eating**: Eat
- **Vocalization**: Bark
- **Play**: Roll, ChaseTail, JumpAndPaw
- **Interaction**: PawUp, LickPaw
- **Tricks**: PlayDead

## Emotion Types
The dog experiences these emotions:
- Happy, Sad, Curious, Vigilant, Fear
- Intimacy, Confusion, Self confidence
- Boredom, Grievances, Excitement, Tired

## Technical Details

### Server Integration
- Actions are automatically uploaded to `localhost:50007` for Unity integration
- JSON format: `{"action": "actionName", "emotions": {"Happy": 0.5, "Curious": 0.3, ...}}`
- Compatible with existing animation pipeline

### LLM Processing
- Uses GPT-4.1-mini for fast, real-time responses
- Considers dog personality, conversation history, and emotional context
- Validates outputs to ensure only valid actions and emotions

### Emotion Vector System
- 12-dimensional emotion space
- Normalized weights (always sum to 1.0)
- Dynamic blending and evolution
- Persistent across interactions

## Tips for Best Results

1. **Be expressive**: Use emotional language to get more varied responses
2. **Build context**: Reference previous interactions or ongoing activities
3. **Mix interactions**: Combine commands, praise, and conversation
4. **Check emotions**: Use the `emotions` command to see how your dog is feeling
5. **Be patient**: The LLM might take a moment to generate complex responses

## Troubleshooting

### Common Issues
- **"OPENAI_API_KEY environment variable not set"**: Set your OpenAI API key
- **"Could not connect to server"**: The action server isn't running (optional for text mode)
- **"Failed to get valid LLM goals"**: Check your internet connection and API key

### Requirements
- Python 3.7+
- OpenAI API key (set as environment variable)
- Required packages: `openai`, `requests` (see requirements.txt)

## Getting Started

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Run the text companion:
   ```bash
   python text_dog_companion.py
   ```

3. Start talking to your dog and watch it respond with personality-driven actions!

Enjoy your new AI dog companion! 🐕 