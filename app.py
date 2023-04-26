import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import errno
from modules import upscale, remove_background, adobe, png_to_jpeg, meme_generator, whisper_transcription, interview_text,image_on_template
import concurrent.futures
import psutil  # Import the psutil library

def open_when_unlocked(file_path, max_retries=20, delay=1):
    retries = 0
    while retries < max_retries:
        try:
            with open(file_path, 'rb'):
                return True
        except OSError as e:
            if e.errno != errno.EACCES:
                raise
            time.sleep(delay)
            retries += 1
    return False


class ImageProcessor:
    def __init__(self, name, process_image, *args):
        self.name = name
        self.process_image = process_image
        self.input_folder = os.path.join('Hotfolder', name)
        self.output_folder = os.path.join('Output', name)
        self.archive_folder = os.path.join('Archive', name)
        self.args = args

processors = [
    ImageProcessor('Upscale2X', upscale.process_image, 2), 
    ImageProcessor('Upscale4X', upscale.process_image, 4), 
    ImageProcessor('Upscale8X', upscale.process_image, 8), 
    ImageProcessor('RemoveBG', remove_background.process_image),
    ImageProcessor('Adobe', adobe.process_image, 5),  # Adjust the megapixels value as needed
    ImageProcessor('PNGtoJPEG', png_to_jpeg.process_image),
    ImageProcessor('MemeGenerator', meme_generator.process_image),
    ImageProcessor('WhisperTranscription', whisper_transcription.process_audio),
    ImageProcessor('InterviewText', interview_text.process_text),
    ImageProcessor('ProductRelease', image_on_template.process_image, 'D:/Appar/ProcessImages/product_release.png'),
]
class MultiFolderEventHandler(FileSystemEventHandler):
    def __init__(self, processors):
        self.processors = processors
        # Set max_workers to 1 for limiting the upscale processing to one image at a time
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.cpu_usage_limit = 70  # Set the desired CPU usage limit in percentage

    def on_created(self, event):
        for processor in self.processors:
            if event.src_path.startswith(processor.input_folder) and not event.is_directory:
                if event.src_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    print(f"New image detected in {processor.name}: {event.src_path}")
                    self.executor.submit(self.process_image, event.src_path, processor)
                elif event.src_path.lower().endswith(('.mp3', '.m4a')) and processor.name == "WhisperTranscription":
                    print(f"New audio detected in {processor.name}: {event.src_path}")
                    self.executor.submit(self.process_image, event.src_path, processor)
                elif event.src_path.lower().endswith('.txt') and processor.name == "InterviewText":
                    print(f"New text file detected in {processor.name}: {event.src_path}")
                    self.executor.submit(self.process_image, event.src_path, processor)

    def process_image(self, src_path, processor):
        if open_when_unlocked(src_path):
            while True:
                # Check the current CPU usage
                current_cpu_usage = psutil.cpu_percent(interval=1)

                # If the current CPU usage is below the desired limit, start processing
                if current_cpu_usage < self.cpu_usage_limit:
                    processor.process_image(src_path, processor.output_folder, processor.archive_folder, *processor.args)
                    break
                else:
                    time.sleep(1)  # Sleep for 1 second and re-check the CPU usage

    def stop(self):
        self.executor.shutdown(wait=True)

if __name__ == '__main__':
    event_handler = MultiFolderEventHandler(processors)
    observer = Observer()

    for processor in processors:
        os.makedirs(processor.input_folder, exist_ok=True)
        os.makedirs(processor.output_folder, exist_ok=True)
        os.makedirs(processor.archive_folder, exist_ok=True)
        observer.schedule(event_handler, processor.input_folder, recursive=True)

    observer.start()

    monitored_folders = ', '.join([processor.input_folder for processor in processors])
    print(f"Monitoring {monitored_folders} for new images...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        event_handler.stop()
        observer.stop()
    observer.join()

