# Audio Generation and Storage Service

This application generates speech audio using Azure Cognitive Services, processes it with background music, and stores the final audio in MongoDB. It’s designed for scenarios where audio content, such as podcasts, is synthesized and saved for later streaming.

## Features
- Converts text to speech using Azure Cognitive Services.
- Adds background music and customizes audio segments.
- Stores generated audio files in MongoDB as binary data for easy retrieval.

## Prerequisites
- **Azure Cognitive Services Speech API**: Set up and obtain API keys.
- **MongoDB**: Access to a MongoDB instance.
- **Environment Variables**:
  - `MONGO_URI`: MongoDB connection URI
  - `SPEECH_KEY`: Azure Speech API subscription key
  - `SPEECH_REGION`: Azure Speech API region
  - `EPISODE_ID`: ID for storing the audio in MongoDB
  - `PROMPT`: Text to be converted to speech
  - **Dependencies**: Ensure Python libraries are installed using `pip install azure-cognitiveservices-speech pymongo pydub`

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>

2. **Install Dependencies:**:
   ```bash
    pip install -r requirements.txt

3. **Configure Environment Variables:**:
   ```bash
    MONGO_URI=<your-mongodb-uri>
    SPEECH_KEY=<your-azure-speech-key>
    SPEECH_REGION=<your-azure-speech-region>
    EPISODE_ID=<unique-episode-id>
    PROMPT=<text-to-synthesize>

4. **Run the Application:**:
     ```bash
    python app.py



