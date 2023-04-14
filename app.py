import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


from modules import upscale, remove_background, adobe

class ImageProcessor:
    def __init__(self, name, process_image, *args):
        self.name = name
        self.process_image = process_image
        self.input_folder = os.path.join('Hotfolder', name)
        self.output_folder = os.path.join('Output', name)
        self.archive_folder = os.path.join('Archive', name)
        self.args = args

processors = [
    ImageProcessor('Upscale', upscale.process_image, 8),
    ImageProcessor('RemoveBG', remove_background.process_image),
    ImageProcessor('Adobe', adobe.process_image, 2),  # Adjust the megapixels value as needed
]

class MultiFolderEventHandler(FileSystemEventHandler):
    def __init__(self, processors):
        self.processors = processors

    def on_created(self, event):
        for processor in self.processors:
            if event.src_path.startswith(processor.input_folder) and not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                print(f"New image detected in {processor.name}: {event.src_path}")
                processor.process_image(event.src_path, processor.output_folder, processor.archive_folder, *processor.args)



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
        observer.stop()

    observer.join()
