import simpleaudio as sa
from pydub import AudioSegment
from io import BytesIO
from pymongo import MongoClient
from bson import Binary
import os

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["mediaLibrary"]
collection = db["audioFiles"]

def fetch_and_play_audio(audio_id):
    document = collection.find_one({"name": audio_id})
    
    if not document:
        print(f"No audio found for ID {audio_id}.")
        return
    
    audio_binary = document.get("audio_data")
    
    if not audio_binary:
        print(f"No audio data found for ID {audio_id}.")
        return

    audio_stream = BytesIO(audio_binary)
    audio_segment = AudioSegment.from_file(audio_stream, format="mp3")  
    
    raw_audio = audio_segment.raw_data
    
    play_obj = sa.play_buffer(raw_audio, num_channels=audio_segment.channels, 
                              bytes_per_sample=audio_segment.sample_width, 
                              sample_rate=audio_segment.frame_rate)
    play_obj.wait_done()

# Example usage
audio_id = "123"  
fetch_and_play_audio(audio_id)
