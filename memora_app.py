import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Memora - AI Health Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

class MemoraCompanion:
    def __init__(self):
        self.setup_gemini()
        self.initialize_session_state()
        self.cognitive_questions = self.load_cognitive_questions()
        self.scoring_weights = {
            'orientation': 0.2,
            'memory': 0.25,
            'attention': 0.2,
            'language': 0.15,
            'visuospatial': 0.1,
            'executive': 0.1
        }
    
    def setup_gemini(self):
        """Initialize Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("Please set your GEMINI_API_KEY environment variable")
            st.stop()
        
        # Configure both genai and LangChain
        genai.configure(api_key=api_key)
        
        # Initialize LangChain ChatGoogleGenerativeAI with explicit API key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=1024
        )
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {
                'name': '',
                'age': None,
                'mood_history': [],
                'assessment_started': False
            }
        if 'cognitive_scores' not in st.session_state:
            st.session_state.cognitive_scores = {
                'orientation': [],
                'memory': [],
                'attention': [],
                'language': [],
                'visuospatial': [],
                'executive': []
            }
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = {
                'current_phase': 'greeting',
                'questions_asked': 0,
                'last_sentiment': 'neutral'
            }
    
    def load_cognitive_questions(self) -> Dict[str, List[Dict]]:
        """Load cognitive assessment questions inspired by RUDAS, MMSE, and MoCA"""
        return {
            'orientation': [
                {
                    'question': 'What day of the week is it today?',
                    'type': 'temporal_orientation',
                    'weight': 1.0
                },
                {
                    'question': 'What month and year are we in?',
                    'type': 'temporal_orientation',
                    'weight': 1.0
                },
                {
                    'question': 'Can you tell me where we are right now?',
                    'type': 'spatial_orientation',
                    'weight': 1.0
                }
            ],
            'memory': [
                {
                    'question': 'I\'m going to say three words. Please repeat them back to me: "Apple, Table, Penny"',
                    'type': 'immediate_recall',
                    'weight': 1.0,
                    'expected_words': ['apple', 'table', 'penny']
                },
                {
                    'question': 'Can you remember those three words I asked you to repeat earlier?',
                    'type': 'delayed_recall',
                    'weight': 2.0,
                    'expected_words': ['apple', 'table', 'penny']
                }
            ],
            'attention': [
                {
                    'question': 'Can you count backwards from 20 to 1?',
                    'type': 'serial_sevens',
                    'weight': 1.0
                },
                {
                    'question': 'Can you spell the word "WORLD" backwards?',
                    'type': 'spelling_backwards',
                    'weight': 1.0,
                    'expected': 'DLROW'
                }
            ],
            'language': [
                {
                    'question': 'Can you name as many animals as you can think of in one minute?',
                    'type': 'verbal_fluency',
                    'weight': 1.0
                },
                {
                    'question': 'Can you tell me what a clock is used for?',
                    'type': 'comprehension',
                    'weight': 1.0
                }
            ],
            'visuospatial': [
                {
                    'question': 'Can you draw a clock face and set the time to 3:45?',
                    'type': 'clock_drawing',
                    'weight': 2.0
                }
            ],
            'executive': [
                {
                    'question': 'If you had a problem with your neighbor making too much noise, what would you do?',
                    'type': 'problem_solving',
                    'weight': 1.0
                }
            ]
        }
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of user input using Gemini"""
        try:
            prompt = f"""
            Analyze the emotional tone and sentiment of this text. Respond with only one word from: 
            happy, sad, confused, anxious, tired, neutral, frustrated, calm
            
            Text: "{text}"
            """
            
            response = self.llm.invoke(prompt)
            sentiment = response.content.strip().lower()
            
            # Validate sentiment
            valid_sentiments = ['happy', 'sad', 'confused', 'anxious', 'tired', 'neutral', 'frustrated', 'calm']
            if sentiment not in valid_sentiments:
                sentiment = 'neutral'
            
            return sentiment
        except Exception as e:
            st.error(f"Error analyzing sentiment: {e}")
            return 'neutral'
    
    def generate_empathetic_response(self, user_input: str, sentiment: str) -> str:
        """Generate empathetic response based on user input and sentiment"""
        try:
            # Get conversation context
            context = st.session_state.conversation_context
            user_profile = st.session_state.user_profile
            
            # Create system prompt for empathetic response
            system_prompt = f"""
            You are Memora, an empathetic AI health companion designed to help assess cognitive function through natural conversation. 
            
            User Profile: Name: {user_profile['name']}, Age: {user_profile['age']}
            Current Sentiment: {sentiment}
            Conversation Phase: {context['current_phase']}
            
            Guidelines:
            1. Be warm, patient, and encouraging
            2. Adapt your tone to the user's emotional state
            3. If they seem confused or frustrated, be extra gentle and reassuring
            4. If they seem happy, match their positive energy
            5. Always maintain a supportive, non-judgmental tone
            6. Keep responses conversational and natural
            7. If this is part of a cognitive assessment, be subtle about it
            """
            
            # Create the full prompt
            full_prompt = f"{system_prompt}\n\nUser: {user_input}\n\nMemora:"
            
            # Generate response
            response = self.llm.invoke(full_prompt)
            return response.content
            
        except Exception as e:
            st.error(f"Error generating response: {e}")
            return "I'm here to listen and help. Could you tell me more about how you're feeling today?"
    
    def generate_next_question(self, category: str) -> Optional[Dict]:
        """Generate the next cognitive assessment question"""
        questions = self.cognitive_questions.get(category, [])
        context = st.session_state.conversation_context
        
        # Find unasked questions in this category
        asked_questions = context.get('questions_asked', 0)
        
        if asked_questions < len(questions):
            return questions[asked_questions]
        
        return None
    
    def calculate_score(self, category: str, response: str, question: Dict) -> float:
        """Calculate score for a cognitive assessment response"""
        try:
            if category == 'memory' and question['type'] == 'immediate_recall':
                # Check for word recall
                expected_words = question.get('expected_words', [])
                response_lower = response.lower()
                correct_words = sum(1 for word in expected_words if word in response_lower)
                return (correct_words / len(expected_words)) * question['weight']
            
            elif category == 'memory' and question['type'] == 'delayed_recall':
                # Check for delayed word recall
                expected_words = question.get('expected_words', [])
                response_lower = response.lower()
                correct_words = sum(1 for word in expected_words if word in response_lower)
                return (correct_words / len(expected_words)) * question['weight']
            
            elif category == 'attention' and question['type'] == 'spelling_backwards':
                # Check spelling backwards
                expected = question.get('expected', '').lower()
                user_response = response.lower().replace(' ', '')
                if expected in user_response or user_response in expected:
                    return question['weight']
                return 0.0
            
            elif category == 'language' and question['type'] == 'verbal_fluency':
                # Count animals mentioned (basic heuristic)
                animals = ['dog', 'cat', 'bird', 'fish', 'lion', 'tiger', 'elephant', 'bear', 'cow', 'horse', 'sheep', 'pig', 'chicken', 'duck', 'rabbit', 'mouse', 'snake', 'frog', 'butterfly', 'bee']
                response_lower = response.lower()
                mentioned_animals = sum(1 for animal in animals if animal in response_lower)
                # Score based on number of animals (max 10 for full points)
                return min(mentioned_animals / 10.0, 1.0) * question['weight']
            
            else:
                # For other questions, use Gemini to evaluate response quality
                evaluation_prompt = f"""
                Evaluate this response to a cognitive assessment question. Rate it from 0.0 to 1.0 based on:
                - Accuracy and correctness
                - Completeness of response
                - Clarity of expression
                
                Question: {question['question']}
                Response: {response}
                
                Respond with only a number between 0.0 and 1.0.
                """
                
                eval_response = self.llm.invoke(evaluation_prompt)
                score_text = eval_response.content.strip()
                
                # Extract number from response
                score_match = re.search(r'(\d+\.?\d*)', score_text)
                if score_match:
                    score = float(score_match.group(1))
                    return min(max(score, 0.0), 1.0) * question['weight']
                
                return 0.5 * question['weight']  # Default moderate score
                
        except Exception as e:
            st.error(f"Error calculating score: {e}")
            return 0.0
    
    def display_result(self) -> str:
        """Analyze all responses and generate cognitive assessment result"""
        try:
            scores = st.session_state.cognitive_scores
            total_score = 0
            max_possible = 0
            
            # Calculate weighted total score
            for category, category_scores in scores.items():
                if category_scores:
                    category_avg = sum(category_scores) / len(category_scores)
                    weight = self.scoring_weights.get(category, 0.1)
                    total_score += category_avg * weight
                    max_possible += weight
            
            # Normalize score to 0-100
            if max_possible > 0:
                normalized_score = (total_score / max_possible) * 100
            else:
                normalized_score = 0
            
            # Generate result interpretation
            if normalized_score >= 80:
                result = "Normal cognitive function"
                interpretation = "Your responses suggest normal cognitive functioning. Keep engaging in mentally stimulating activities!"
            elif normalized_score >= 60:
                result = "Mild cognitive impairment"
                interpretation = "Your responses suggest some mild cognitive changes. This is common with aging and doesn't necessarily indicate dementia. Consider consulting with a healthcare professional for further evaluation."
            else:
                result = "Possible dementia — professional evaluation recommended"
                interpretation = "Your responses suggest significant cognitive changes that warrant professional evaluation. Please consult with a healthcare provider or neurologist for a comprehensive assessment."
            
            return f"""
            ## 🧠 Cognitive Assessment Results
            
            **Overall Score:** {normalized_score:.1f}/100
            
            **Assessment:** {result}
            
            **Interpretation:** {interpretation}
            
            **Important Note:** This is a preliminary assessment tool and should not replace professional medical evaluation. If you have concerns about your cognitive health, please consult with a healthcare professional.
            
            **Recommendations:**
            - Maintain regular social interactions
            - Engage in mentally stimulating activities
            - Follow a healthy diet and exercise routine
            - Get adequate sleep
            - Consider regular cognitive check-ups with your doctor
            """
            
        except Exception as e:
            st.error(f"Error generating results: {e}")
            return "I apologize, but I encountered an error while analyzing your responses. Please try again or consult with a healthcare professional."
    
    def run_assessment_flow(self, user_input: str) -> str:
        """Run the cognitive assessment flow"""
        context = st.session_state.conversation_context
        scores = st.session_state.cognitive_scores
        
        # Determine current assessment phase
        if context['current_phase'] == 'greeting':
            if any(word in user_input.lower() for word in ['start', 'begin', 'test', 'assessment']):
                context['current_phase'] = 'assessment'
                context['questions_asked'] = 0
                return "I'd like to ask you some questions to better understand how you're thinking today. These are just friendly questions - there are no right or wrong answers. Shall we begin?"
            else:
                return self.generate_empathetic_response(user_input, self.analyze_sentiment(user_input))
        
        elif context['current_phase'] == 'assessment':
            # Check if user wants to see results
            if '/result' in user_input.lower():
                context['current_phase'] = 'completed'
                return self.display_result()
            
            # Continue with assessment questions
            categories = ['orientation', 'memory', 'attention', 'language', 'visuospatial', 'executive']
            current_category = categories[context['questions_asked'] % len(categories)]
            
            # Get next question
            question = self.generate_next_question(current_category)
            if question:
                # Score the previous response if this isn't the first question
                if context['questions_asked'] > 0:
                    prev_category = categories[(context['questions_asked'] - 1) % len(categories)]
                    prev_question = self.cognitive_questions[prev_category][(context['questions_asked'] - 1) % len(self.cognitive_questions[prev_category])]
                    score = self.calculate_score(prev_category, user_input, prev_question)
                    scores[prev_category].append(score)
                
                context['questions_asked'] += 1
                return f"Thank you for that response. Now, {question['question']}"
            else:
                # All questions asked, offer to show results
                return "Thank you for answering all the questions! You can type '/result' anytime to see your cognitive assessment summary."
        
        else:
            # Assessment completed
            if '/result' in user_input.lower():
                return self.display_result()
            else:
                return "The assessment is complete. You can type '/result' to see your summary, or we can just chat if you'd like!"

def main():
    # Initialize Memora
    memora = MemoraCompanion()
    
    # Sidebar for user profile
    with st.sidebar:
        st.title("🧠 Memora")
        st.caption("Your AI Health Companion")
        
        # User profile section
        st.subheader("Your Profile")
        name = st.text_input("Your name", value=st.session_state.user_profile['name'])
        age = st.number_input("Your age", min_value=18, max_value=120, value=st.session_state.user_profile['age'] or 65)
        
        if name:
            st.session_state.user_profile['name'] = name
        if age:
            st.session_state.user_profile['age'] = age
        
        # Assessment status
        st.subheader("Assessment Status")
        context = st.session_state.conversation_context
        if context['current_phase'] == 'greeting':
            st.info("Ready to start assessment")
        elif context['current_phase'] == 'assessment':
            st.warning("Assessment in progress")
        else:
            st.success("Assessment completed")
        
        # Quick actions
        st.subheader("Quick Actions")
        if st.button("Start New Assessment"):
            st.session_state.conversation_context = {
                'current_phase': 'greeting',
                'questions_asked': 0,
                'last_sentiment': 'neutral'
            }
            st.session_state.cognitive_scores = {
                'orientation': [],
                'memory': [],
                'attention': [],
                'language': [],
                'visuospatial': [],
                'executive': []
            }
            st.rerun()
    
    # Main chat interface
    st.title("🧠 Memora - AI Health Companion")
    st.caption("Your empathetic companion for cognitive health assessment")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            response = memora.run_assessment_flow(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Footer
    st.markdown("---")
    st.caption("💡 Tip: Type '/result' anytime to see your cognitive assessment summary")
    st.caption("🔒 Your data is stored locally and never shared")

if __name__ == "__main__":
    main()
