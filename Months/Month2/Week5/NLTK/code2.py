import threading
import time
from collections import defaultdict
import random
import math
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize

# Ensure NLTK resources are available
nltk.download('vader_lexicon')
nltk.download('punkt')

######################
# Knowledge Structures
######################

class KnowledgeNode:
    def __init__(self, name, category=None, attributes=None):
        self.name = name
        self.category = category
        self.attributes = attributes or {}
        self.relations = {}

    def add_relation(self, relation_type, other_node):
        self.relations[other_node] = relation_type

    def __repr__(self):
        return f"KnowledgeNode({self.name})"


class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name, category=None, attributes=None):
        node = KnowledgeNode(name, category, attributes)
        self.nodes[name] = node
        return node

    def get_node(self, name):
        return self.nodes.get(name)

    def add_relation(self, node1_name, node2_name, relation_type):
        node1 = self.get_node(node1_name)
        node2 = self.get_node(node2_name)
        if node1 and node2:
            node1.add_relation(relation_type, node2)
            node2.add_relation(relation_type, node1)

    def update_node_attributes(self, name, attributes):
        node = self.get_node(name)
        if node:
            node.attributes.update(attributes)

##############################
# Inferential Cognition Module
##############################

class ISeye:
    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.lock = threading.Lock()
        self.context = []

    # Knowledge Representation Methods

    def represent_knowledge(self, data):
        # Simulate knowledge representation
        for item in data:
            name = item.get('name')
            category = item.get('category')
            attributes = item.get('attributes')
            self.knowledge_graph.add_node(name, category, attributes)

    # Inference and Reasoning Methods

    def bayesian_inference(self, hypothesis, evidence):
        # Simplified Bayesian inference
        prior = hypothesis.get('prior', 0.5)
        likelihood = hypothesis.get('likelihood', 0.5)
        evidence_likelihood = evidence.get('likelihood', 0.5)
        posterior = (likelihood * prior) / evidence_likelihood
        return posterior

    def probabilistic_logic(self, propositions):
        # Simplified probabilistic logic
        probability = 1
        for prop in propositions:
            probability *= prop.get('probability', 0.5)
        return probability

    def fuzzy_logic(self, input_value, sets):
        # Simplified fuzzy logic membership calculation
        memberships = {}
        for set_name, set_params in sets.items():
            memberships[set_name] = max(0, min(1, (input_value - set_params['min']) / (set_params['max'] - set_params['min'])))
        return memberships

    # Learning and Knowledge Update Methods

    def update_knowledge(self, new_data):
        with self.lock:
            self.represent_knowledge(new_data)

    # Sentiment Analysis and Emotion Recognition Methods

    def analyze_sentiment(self, text):
        # Analyze sentiment using NLTK's VADER
        scores = self.sentiment_analyzer.polarity_scores(text)
        return scores

    def recognize_emotion(self, text):
        # Based on sentiment scores, determine primary emotion
        sentiment = self.analyze_sentiment(text)
        compound = sentiment['compound']
        if compound >= 0.5:
            emotion = 'Joy'
        elif compound <= -0.5:
            emotion = 'Anger'
        else:
            emotion = 'Neutral'
        return emotion

#######################
# Core ConsciousAI Class
#######################

class ConsciousAI:
    def __init__(self):
        self.icm = ISeye()
        self.self_awareness_state = {}
        self.running = False
        self.lock = threading.Lock()
        self.context_memory = []

    # Self-awareness Methods

    def self_reflect(self):
        # Simple self-reflection updating internal state
        self.self_awareness_state['last_reflection'] = time.time()
        self.self_awareness_state['mood'] = random.choice(['Happy', 'Sad', 'Thoughtful', 'Curious'])

    # Interaction Methods

    def perceive_input(self, input_data):
        # Process input data
        print("Perceiving input...")
        knowledge_data = self.extract_knowledge(input_data)
        self.icm.update_knowledge(knowledge_data)
        sentiment = self.icm.analyze_sentiment(input_data)
        emotion = self.icm.recognize_emotion(input_data)
        print(f"Detected emotion: {emotion}")
        self.context_memory.append({'input': input_data, 'emotion': emotion})

    def extract_knowledge(self, input_data):
        # Extract entities from text (simplified)
        words = word_tokenize(input_data)
        knowledge_data = [{'name': word, 'category': 'word'} for word in words]
        return knowledge_data

    def decide_action(self):
        # Make decisions based on current knowledge and context
        print("Deciding action...")
        # Simplified decision-making logic
        if self.context_memory:
            last_emotion = self.context_memory[-1]['emotion']
            if last_emotion == 'Joy':
                action = "Express gratitude."
            elif last_emotion == 'Anger':
                action = "Offer assistance."
            else:
                action = "Continue conversation."
        else:
            action = "Initiate greeting."
        print(f"Decided action: {action}")
        return action

    # Main Loop Methods

    def start(self):
        if not self.running:
            self.running = True
            self.main_thread = threading.Thread(target=self.run)
            self.main_thread.start()
            print("ConsciousAI started.")

    def run(self):
        while self.running:
            self.self_reflect()
            time.sleep(1)  # Simulate time passing

    def stop(self):
        if self.running:
            self.running = False
            self.main_thread.join()
            print("ConsciousAI stopped.")

#########################
# Example Usage of System
#########################

if __name__ == "__main__":
    ai = ConsciousAI()
    ai.start()

    try:
        # Simulate input
        user_inputs = [
            "I am very happy with your service today!",
            "I'm feeling quite frustrated with the issue I'm facing.",
            "Could you assist me with this problem?",
            "Thank you for your help!"
        ]

        for input_text in user_inputs:
            ai.perceive_input(input_text)
            action = ai.decide_action()
            print(f"Action: {action}\n")
            time.sleep(2)

    except KeyboardInterrupt:
        pass
    finally:
        ai.stop()
