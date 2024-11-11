import os
import io
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from pymongo import MongoClient
from bson import Binary
from io import BytesIO
import sys

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)  
db = client["mediaLibrary"]
collection = db["audioFiles"]

BGM_PATH = 'backgroundMusic.mp3' 

# Synthesize speech and return audio data in memory
def synthesize_speech(text):
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))

    # Configure for MP3 format
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    # Synthesize text to audio in memory
    result = speech_synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # Convert audio stream into BytesIO and then load it into pydub
        audio_stream = BytesIO(result.audio_data)
        speech_audio = AudioSegment.from_file(audio_stream, format="mp3")  # MP3 format as expected from Azure
        
        # Save synthesized speech to a local file (before adding background music)
       # save_audio_to_file(speech_audio, "synthesized_speech.mp3")
        
        # Process the background music and overlay
        bgm_audio_stream = add_bgm_in_memory(speech_audio, BGM_PATH)
        
        # Save the final audio with background music to a local file (for testing)
        #save_audio_to_file(bgm_audio_stream, "final_audio_with_bgm.mp3")
        
        return bgm_audio_stream
    
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print(f"Error details: {cancellation_details.error_details}")
        return None

# Overlay background music onto the synthesized speech (all in-memory)
def add_bgm_in_memory(speech_audio, bgm_path):
    bgm = AudioSegment.from_file(bgm_path)

    # Extract intro (first 3 seconds), middle, and outro (last 10 seconds) of BGM
    bgm_intro = bgm[:3000]  
    bgm_outro = bgm[-13000:-5000]  
    bgm_middle = bgm[3000:-13000]  

    # Adjust volume levels for different parts of the background music
    bgm_intro = bgm_intro - 15  
    bgm_outro = bgm_outro - 18  
    bgm_middle = bgm_middle - 22  

    # Calculate required length for the middle BGM to loop
    middle_duration = len(speech_audio) - len(bgm_intro) - 1000  

    # Loop the middle part of the BGM to cover the podcast duration
    bgm_middle_loop = bgm_middle * (middle_duration // len(bgm_middle) + 1)
    bgm_middle_loop = bgm_middle_loop[:middle_duration]  

    # Combine intro, looped middle, and outro of BGM
    bgm_full = bgm_intro + bgm_middle_loop + bgm_outro

    # Overlay the background music onto the speech
    final_mix = bgm_full.overlay(speech_audio, position=len(bgm_intro))

    return final_mix

def save_audio_to_mongo(audio_data, audio_id):
    # Export the AudioSegment to a BytesIO buffer
    output_buffer = BytesIO()
    
    if isinstance(audio_data, BytesIO):
        # If audio_data is a BytesIO object, load it into an AudioSegment first
        audio_segment = AudioSegment.from_file(audio_data, format="mp3")
    else:
        audio_segment = audio_data
    
    # Compress the audio before saving
    audio_segment = audio_segment.set_frame_rate(22050)  
    audio_segment = audio_segment.set_channels(1)  
    audio_segment = audio_segment.set_sample_width(2)  

    # Export with a lower bit rate (e.g., 64k for compression)
    audio_segment.export(output_buffer, format="mp3", bitrate="24k")  
    output_buffer.seek(0)

    # Convert in-memory audio data to Binary format
    audio_binary = Binary(output_buffer.read())

    # Update or create a new document with the audio data
    result = collection.update_one(
        {"name": audio_id},  
        {"$set": {"audio_data": audio_binary}},  
        upsert=True  
    )

    # Check the result and print the appropriate message
    if result.upserted_id:
        print(f"New audio created in MongoDB with ID '{audio_id}'")
    else:
        print(f"Audio updated in MongoDB with ID '{audio_id}'")



def save_audio_to_file(audio_data, filename="final_audio.mp3",  bitrate="24k", sample_rate=22050):
    # Ensure that audio_data is in AudioSegment format
    if isinstance(audio_data, BytesIO):  
        audio_segment = AudioSegment.from_file(audio_data, format="mp3")
    else:
        audio_segment = audio_data  

    # Export the AudioSegment to a file
    audio_segment.export(filename, format="mp3", bitrate=bitrate, parameters=["-ar", str(sample_rate)])
    print(f"Audio saved to file '{filename}'")



if __name__ == "__main__":
    episode_id = os.getenv("EPISODE_ID")
    prompt = os.getenv("PROMPT")

    print("Calling text to spech")
    podcast_data = synthesize_speech(prompt)

    if podcast_data is None:
        print("Error in synthesizing speech. Audio will not be saved.")
    else:
        print("storing in db")
        save_audio_to_mongo(podcast_data, episode_id) 


  