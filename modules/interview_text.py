import openai
import shutil
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
import re

def split_text_into_chunks(text, max_chunk_size, min_chunk_size=500):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if re.search(r'[.!?]', word) and sum(len(w) for w in current_chunk) > max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []

    # Add the last chunk if it's not empty
    if current_chunk:
        last_chunk = ' '.join(current_chunk)
        if len(last_chunk) < min_chunk_size and len(chunks) > 0:
            chunks[-1] += ' ' + last_chunk
        else:
            chunks.append(last_chunk)

    return chunks

def process_text(src_path, output_folder, archive_folder, max_chunk_size=5000):
    print("Reading input file...")
    with open(src_path, "r") as f:
        text = f.read()

    # Extract the first line with the description
    lines = text.split("\n")
    description_line = lines.pop(0)

    # Generate conversation messages
    messages = [{"role": "system", "content": "You are an assistant assigning interview text segments to people based on a description. If a user request includes prior context, it should not be in the response."},
            {"role": "user", "content": f"Description: {description_line}"},
            {"role": "assistant", "content": "I'll assign segments to people. My response will only contain the assigned text. Please send the interview text."},
            ]

    
    print("Splitting text into smaller chunks...")
    interview_text = " ".join(lines)
    chunks = split_text_into_chunks(interview_text, max_chunk_size)
    print(f"Number of chunks: {len(chunks)}")
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        # Add the end of the previous response to the current chunk (except for the first chunk)
        if False:
            context = processed_chunks[-1][-2000:]  # Include the last 500 characters of the previous response
            user_message_content = f"Context: {context}\nInterview text: {chunk}"
        else:
            user_message_content = f"Interview text: {chunk}"

        temp_messages = messages.copy()
        temp_messages.append({"role": "user", "content": user_message_content})

        print("Sending chunk to GPT-3.5-turbo for processing...")
        print(f"Chunk size: {len(chunk)}")
        # print the messages to be sent to GPT-3.5-turbo
        for message in temp_messages:
            print(f"\n{message['role']}: {message['content']}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=temp_messages,
            temperature=0.1,
        )

        # Get the generated content
        generated_text = response.choices[0].message.content.strip()
        print(f"Generated text: {generated_text}")
        processed_chunks.append(generated_text)

    # Save the processed content to a new file in the output folder
    output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(src_path))[0] + "_processed.txt")
    with open(output_file, "w") as f:
        f.write(' \n'.join(processed_chunks))

    print(f"Processed interview text saved to: {output_file}")

    # Move the original text file to the archive folder
    shutil.move(src_path, os.path.join(archive_folder, os.path.basename(src_path)))
