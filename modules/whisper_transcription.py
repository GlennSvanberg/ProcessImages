import openai
from pydub import AudioSegment
import os
import logging
import re
import shutil

openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

def process_audio(src_path, output_folder, archive_folder, max_duration=10 * 60 * 1000, prompt=None):
    logging.info(f"Processing audio file: {src_path}")

    audio_file = open(src_path, "rb")

    file_ext = os.path.splitext(src_path)[1].lower()
    if file_ext == '.mp3':
        song = AudioSegment.from_mp3(audio_file)
    elif file_ext == '.m4a':
        song = AudioSegment.from_file(audio_file, format='m4a')
    else:
        raise ValueError(f"Unsupported audio format: {file_ext}")

    audio_file.close()  # Close the audio_file object

    total_duration = len(song)

    logging.info(f"Total duration: {total_duration} ms")

    start = 0
    chunk_id = 1

    output_file = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(src_path))[0]}.txt")  # Create a single output file

    with open(output_file, "w") as f_out:  # Open the output file before the loop
        while True:
            end = min(start + max_duration, total_duration)  # Make sure end doesn't exceed total_duration
            if start >= end:  # Exit the loop if there's no more data to transcribe
                break

            chunk = song[start:end]

            logging.info(f"Processing chunk {chunk_id} from {start} ms to {end} ms")
            try:
                # Export the chunk as a temporary mp3 file
                with open("temp.mp3", "wb") as f:
                    chunk.export(f, format="mp3")

                # Transcribe the chunk
                with open("temp.mp3", "rb") as f:
                    transcript = openai.Audio.transcribe("whisper-1", f, prompt=prompt)
                    text = transcript.get("text", "")

                formatted_text = re.sub(r"([.!?])\s*", r"\1\n", text.strip())

                # Append the transcribed text to the output file
                f_out.write(formatted_text)
                f_out.write("\n")  # Add an extra newline to separate chunks

                logging.info(f"Transcribed text appended to: {output_file}")

                # Update the prompt and move to the next chunk
                if prompt:
                    prompt += " " + text[-100:]
                else:
                    prompt = text[-100:]
            except Exception as e:
                print("Exception", e)

            if end >= total_duration:  # Exit the loop when start exceeds the total_duration
                break

            start = end  # Increment start by the actual duration of the current chunk
            chunk_id += 1

    # Move the original audio file to the archive folder
    try:
        shutil.move(src_path, os.path.join(archive_folder, os.path.basename(src_path)))
    except Exception as e:
        logging.error(f"Failed to move the file: {src_path} - Error: {e}")

    logging.info(f"Finished processing audio file: {src_path}")
