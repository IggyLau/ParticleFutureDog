from config import core_sentiments
class DogPersonality:
    """
    Stores the dog's long-term personality/context, a malleable emotion vector, and a history of all user inputs.
    The emotion vector represents the current weight/percentage of each core sentiment.
    Designed for extensibility: can be expanded to include memory, mood, or adaptive traits.
    """
    def __init__(self, personality_description=None, core_emotions=core_sentiments, action="sit"):
        
        self.personality = personality_description or "A playful, loyal, and curious dog companion."
        self.user_inputs = []  
        self.core_emotions = core_emotions
        self.emotion_vector = {emotion: 0.0 for emotion in self.core_emotions}
        self.emotion_vector["Happy"] = 0.5 
        self.emotion_vector["Curious"] = 0.3
        self.emotion_vector["Excitement"] = 0.2
        self.action= action
        self.normalize_emotions()


    def set_personality(self, description):
        """
        Set or update the dog's personality/context.
        Args:
            description (str): New personality description.
        """
        self.personality = description

    def get_personality(self):
        """
        Get the current personality/context string.
        Returns:
            str: The personality description.
        """
        return self.personality

    def add_user_input(self, user_input):
        """
        Add a user input event to the history.
        Args:
            user_input (dict or str): The user input event.
        """
        self.user_inputs.append(user_input)

    def get_user_inputs(self):
        """
        Get the history of all user inputs.
        Returns:
            list: List of user input events.
        """
        return self.user_inputs

    def set_emotion_vector(self, new_vector):
        """
        Set the entire emotion vector. Expects a dict of emotion: weight.
        Automatically normalizes the vector.
        """
        for emotion in self.core_emotions:
            self.emotion_vector[emotion] = float(new_vector.get(emotion, 0.0))
        self.normalize_emotions()

    def update_emotion(self, emotion, delta):
        """
        Add (or subtract) a value to a specific emotion, then normalize.
        Args:
            emotion (str): The emotion to update.
            delta (float): The amount to add (can be negative).
        """
        if emotion in self.emotion_vector:
            self.emotion_vector[emotion] += delta
            # Clamp to [0, None] (no negative emotions)
            self.emotion_vector[emotion] = max(0.0, self.emotion_vector[emotion])
            self.normalize_emotions()

    def decay_emotions(self, decay_rate=0.05):
        """
        Decay all emotions toward zero by a fixed rate, except the dominant one.
        Args:
            decay_rate (float): The fraction to decay each emotion by.
        """
        dominant = self.get_dominant_emotion()
        for emotion in self.emotion_vector:
            if emotion != dominant:
                self.emotion_vector[emotion] *= (1.0 - decay_rate)
        self.normalize_emotions()

    def blend_emotions(self, blend_dict):
        """
        Blend in a new set of emotions (e.g., from a user event), then normalize.
        Args:
            blend_dict: Either a dict of emotion: weight or a list of (emotion, weight) tuples
        """
        # Handle both list of tuples and dictionary inputs
        if isinstance(blend_dict, list):
            # Convert list of tuples to dictionary
            emotion_dict = dict(blend_dict)
        else:
            emotion_dict = blend_dict

        # Update emotions
        for emotion, value in emotion_dict.items():
            if emotion in core_sentiments:
                self.emotion_vector[emotion] += value
        self.normalize_emotions()

    def normalize_emotions(self):
        """
        Normalize the emotion vector so all weights sum to 1.0 (if total > 0).
        """
        total = sum(self.emotion_vector.values())
        if total > 0:
            for emotion in self.emotion_vector:
                self.emotion_vector[emotion] /= total

    def get_emotion_vector(self):
        """
        Get the current emotion vector (dict of emotion: weight).
        """
        return dict(self.emotion_vector)

    def get_dominant_emotion(self):
        """
        Get the emotion with the highest weight.
        Returns:
            str: The dominant emotion.
        """
        return max(self.emotion_vector, key=self.emotion_vector.get)

    def get_top_emotions(self, n=3):
        """
        Get the top n emotions and their weights, sorted descending.
        Args:
            n (int): Number of top emotions to return.
        Returns:
            List[Tuple[str, float]]: List of (emotion, weight) tuples.
        """
        sorted_emotions = sorted(self.emotion_vector.items(), key=lambda x: x[1], reverse=True)
        return sorted_emotions[:n]

    def process_emotion_tuples(self, emotion_tuples):
        """
        Process a list of emotion tuples from valid goals and normalize the emotion vector.
        
        Args:
            emotion_tuples: List of tuples in format [('emotion1', weight1), ('emotion2', weight2)]
        """
        # Pass the emotion tuples directly to blend_emotions
        self.blend_emotions(emotion_tuples) 

    def get_action(self):
        """
        Get the current action.
        Returns:
            str: The current action.
        """
        return self.action