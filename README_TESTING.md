# Action & Emotion Vector Testing Interface

This testing interface allows you to manually create action sequences with emotion vectors and upload them directly to the server that `behavior_logic.py` uses.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python action_server.py
   ```
   The server will run on `localhost:50007`

3. **Run the testing interface:**
   ```bash
   python action_tester.py
   ```

## Features

### Main Menu Options:

1. **Add action with emotions** - Manually create action/emotion pairs
2. **View current test sequence** - See your local sequence before uploading
3. **Upload sequence to server** - Send your sequence to the server
4. **Get sequence from server** - View what's currently on the server
5. **Clear local sequence** - Reset your local test sequence
6. **Clear server sequence** - Remove sequence from server
7. **Show available actions** - List all valid actions
8. **Show available emotions** - List all valid emotions
9. **Add preset sequences** - Quick presets for common scenarios

### Available Actions:
- Super Stand, Stand, Sit, Lie Face Down, Lie Face Up
- Walk, Spin, Paw Up, Kick, Shake, Roll, Jump, Retreat, Downward Dog

### Available Emotions:
- Happy, Sad, Curious, Vigilant, Fear, Intimacy
- Confusion, Self confidence, Boredom, Grievances, Excitement, Tired

### Preset Sequences:
- **Happy Dog**: Jump → Spin → Sit (with happy/excited emotions)
- **Curious Dog**: Stand → Walk (with curious/vigilant emotions)  
- **Tired Dog**: Sit → Lie Face Down (with tired/bored emotions)
- **Scared Dog**: Retreat → Sit (with fear/confusion emotions)

## How to Use

1. Start the server first (`python action_server.py`)
2. Run the tester (`python action_tester.py`)
3. Use option 9 to add a preset sequence, or option 1 to create custom actions
4. Use option 3 to upload your sequence to the server
5. Use option 4 to verify the server received your sequence

## Example Workflow

```
1. Select "9. Add preset sequences"
2. Choose "1. Happy Dog" 
3. Select "3. Upload sequence to server"
4. Select "4. Get sequence from server" to verify

Or manually:

1. Select "1. Add action with emotions"
2. Choose action "Jump" 
3. Add emotion "Happy" with weight 0.6
4. Add emotion "Excitement" with weight 0.4
5. Repeat for more actions
6. Upload to server when ready
```

## Notes

- Emotion weights must sum to ≤ 1.0 per action
- The interface validates all inputs against allowed actions/emotions
- Server must be running on port 50007 for uploads to work
- The same server format is used by `behavior_logic.py` 