import os
import time
import zipfile
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

def create_comicinfo_xml(series_name, title_name):
    """Creates an XML string for ComicInfo.xml."""
    import xml.etree.ElementTree as ET
    comic_info = ET.Element("ComicInfo")
    title = ET.SubElement(comic_info, "Title")
    title.text = title_name
    series = ET.SubElement(comic_info, "Series")
    series.text = series_name

    return ET.tostring(comic_info, encoding="utf-8", method="xml").decode("utf-8")

def initialize_database(db_path):
    """Initializes the SQLite database to track processed files."""
    first_run = not os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_files (
            filepath TEXT PRIMARY KEY
        )
    """
    )
    conn.commit()
    conn.close()
    return first_run

def cleanup_sql_journal(script_dir):
    """Deletes SQLite journal files at the beginning to prevent locking issues."""
    for file in os.listdir(script_dir):
        if file.endswith(".db-journal"):
            os.remove(os.path.join(script_dir, file))

def is_file_processed(db_path, filepath):
    """Checks if a file has already been processed."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_files WHERE filepath = ?", (filepath,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_files_as_processed(db_path, filepaths):
    """Marks a batch of files as processed in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executemany("INSERT OR IGNORE INTO processed_files (filepath) VALUES (?)", [(fp,) for fp in filepaths])
    conn.commit()
    conn.close()

def process_cbz_file(filepath, log_file, db_path, processed_files_batch):
    """Checks if ComicInfo.xml exists in the .cbz file and creates one if not."""
    if is_file_processed(db_path, filepath):
        return  # Skip already processed files

    with zipfile.ZipFile(filepath, 'a') as cbz:
        if "ComicInfo.xml" not in cbz.namelist():
            series_name = os.path.basename(os.path.dirname(filepath))
            title_name, _ = os.path.splitext(os.path.basename(filepath))
            comicinfo_content = create_comicinfo_xml(series_name, title_name)
            cbz.writestr("ComicInfo.xml", comicinfo_content)
            log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Added ComicInfo.xml to {filepath}\n"
            with open(log_file, 'a') as log:
                log.write(log_entry)

    # Add to the batch of processed files
    processed_files_batch.append(filepath)

def check_log_size(log_file):
    """Checks the size of the log file and deletes it if it exceeds 50MB."""
    if os.path.exists(log_file):
        file_size = os.path.getsize(log_file)
        if file_size > 50 * 1024 * 1024:  # 50 MB
            print(f"Log file exceeds 50MB. Deleting {log_file}...")
            os.remove(log_file)

def clear_console():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_progress_bar(current, total, bar_length=40):
    """Prints a simple text-based progress bar on the same line."""
    percent = (current / total) * 100
    filled_length = int(bar_length * current // total)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    print(f"\r[{bar}] {percent:.2f}% ({current}/{total})", end="")

def process_files(directory, log_file, db_path, log_entries, total_files, batch_size=500):  # Changed batch size to 500
    """Processes .cbz files in the directory with a progress bar."""
    processed_files_batch = []
    processed_count = 0
    start_time = time.time()

    # Create a ThreadPoolExecutor to handle the file processing concurrently
    with ThreadPoolExecutor() as executor:
        futures = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".cbz"):
                    filepath = os.path.join(root, file)
                    if is_file_processed(db_path, filepath):  # Skip already processed files
                        continue
                    future = executor.submit(process_cbz_file, filepath, log_file, db_path, processed_files_batch)
                    futures.append(future)

        # Track the completion of each file processing task
        for future in as_completed(futures):
            processed_count += 1

            # Update progress bar every 10 files
            if processed_count % 10 == 0:
                print_progress_bar(processed_count, total_files)

            # Save progress to the database periodically (after every 500 files)
            if processed_count % batch_size == 0:
                mark_files_as_processed(db_path, processed_files_batch)
                processed_files_batch.clear()  # Clear the batch after committing

        # Mark all processed files in a single batch after completion
        if processed_files_batch:
            mark_files_as_processed(db_path, processed_files_batch)

def get_manga_directory():
    """Prompts the user for the manga directory or loads it from a file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    manga_location_file = os.path.join(script_dir, "Manga Library Location")

    if os.path.exists(manga_location_file):
        with open(manga_location_file, 'r') as file:
            return file.read().strip()

    manga_directory = input("Enter the full path to your Manga directory: ").strip()
    with open(manga_location_file, 'w') as file:
        file.write(manga_directory)
    return manga_directory

def main():
    """Main function to process .cbz files in a directory tree, running once and then closing with countdown."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Cleanup SQLite journal files at the start
    cleanup_sql_journal(script_dir)

    manga_directory = get_manga_directory()

    # Clear screen and prepare the log file
    clear_console()
    print("Manga Metadata Fixer by HDShock")
    log_file = os.path.join(script_dir, "process_log.txt")
    db_path = os.path.join(script_dir, "processed_files.db")

    # Initialize the database
    first_run = initialize_database(db_path)

    # Check the log file size
    check_log_size(log_file)

    print(f"\nLog file location: {log_file}\n")

    # Count the total number of files to process
    total_files = sum([len(files) for _, _, files in os.walk(manga_directory) if any(file.endswith('.cbz') for file in files)])

    # Process files with progress bar and periodic database updates
    log_entries = []
    process_files(manga_directory, log_file, db_path, log_entries, total_files)

    # Display first scan complete message
    clear_console()
    print("Manga Metadata Fixer by HDShock")
    print("\nFirst Scan complete!")

    # Countdown timer before closing the console
    countdown = 10  # Countdown in seconds
    while countdown > 0:
        clear_console()
        print("Manga Metadata Fixer by HDShock")
        print("\nFirst Scan complete!")
        print(f"\nClosing in {countdown} seconds...")
        time.sleep(1)
        countdown -= 1

    clear_console()  # Clear console before closing

if __name__ == "__main__":
    main()
