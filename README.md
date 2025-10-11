# Memora - AI Health Companion

Memora is an empathetic AI health companion designed to interact with aged users and detect early signs of dementia through natural, mood-based conversations. The application uses cognitive assessments inspired by RUDAS, MMSE, and MoCA tests.

## Features

- 🧠 **Interactive Chat Interface**: Natural conversation with empathetic AI companion
- 📊 **Cognitive Assessment**: Subtle testing based on established medical protocols
- 😊 **Emotional Adaptation**: AI adjusts tone based on user's mood and sentiment
- 👤 **Personalization**: Remembers user profile and conversation history
- 🔒 **Privacy-First**: All data stored locally, no cloud database
- 📈 **Comprehensive Scoring**: Multi-category cognitive assessment with detailed results

## Cognitive Assessment Categories

- **Orientation**: Temporal and spatial awareness
- **Memory**: Immediate and delayed recall tests
- **Attention**: Concentration and focus tasks
- **Language**: Verbal fluency and comprehension
- **Visuospatial**: Spatial reasoning and drawing tasks
- **Executive Function**: Problem-solving and planning

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for the next step

### 3. Configure Environment

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

```bash
streamlit run memora_app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

1. **Setup Profile**: Enter your name and age in the sidebar
2. **Start Conversation**: Begin chatting with Memora naturally
3. **Begin Assessment**: Type "start assessment" or similar to begin cognitive testing
4. **Answer Questions**: Respond naturally to Memora's questions
5. **View Results**: Type "/result" anytime to see your cognitive assessment summary

## How It Works

### Conversation Flow
1. **Greeting Phase**: Initial conversation and profile setup
2. **Assessment Phase**: Subtle cognitive testing through natural questions
3. **Results Phase**: Comprehensive analysis and recommendations

### Scoring System
- Each response is evaluated using AI-powered analysis
- Scores are weighted across different cognitive categories
- Final assessment provides one of three outcomes:
  - Normal cognitive function
  - Mild cognitive impairment
  - Possible dementia (professional evaluation recommended)

### Emotional Intelligence
- Real-time sentiment analysis of user responses
- Dynamic tone adaptation based on emotional state
- Supportive and encouraging communication style

## Technical Architecture

- **Frontend**: Streamlit for interactive web interface
- **AI Model**: Google Gemini API for conversation and reasoning
- **Framework**: LangChain for conversation memory and structured flow
- **Storage**: Local session state and JSON files
- **Language**: Python 3.11+

## Privacy & Security

- No data is sent to external servers except for Gemini API calls
- All conversation history is stored locally in session state
- No personal information is permanently stored
- API keys should be kept secure and not shared

## Important Medical Disclaimer

This application is designed as a preliminary assessment tool and should **NOT** replace professional medical evaluation. If you have concerns about your cognitive health, please consult with a healthcare professional or neurologist.

## Support

For technical issues or questions about the application, please refer to the code documentation or create an issue in the project repository.

## License

This project is for educational and research purposes. Please ensure compliance with all applicable regulations when using for medical or clinical purposes.
