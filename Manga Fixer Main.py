import os
import time
import zipfile
import threading
import sqlite3

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
    """)
    conn.commit()
    conn.close()
    return first_run

def is_file_processed(db_path, filepath):
    """Checks if a file has already been processed."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_files WHERE filepath = ?", (filepath,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_file_as_processed(db_path, filepath):
    """Marks a file as processed in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO processed_files (filepath) VALUES (?)", (filepath,))
    conn.commit()
    conn.close()

def process_cbz_file(filepath, log_file, db_path):
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
            print(log_entry.strip())
            with open(log_file, 'a') as log:
                log.write(log_entry)
        else:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ComicInfo.xml already exists in {filepath}")

    # Mark the file as processed, whether or not an XML file was added
    mark_file_as_processed(db_path, filepath)

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

def loading_animation(stop_flag, first_run):
    """Displays a loading animation."""
    animation = ["", ".", "..", "..."]
    while not stop_flag.is_set():
        for frame in animation:
            if stop_flag.is_set():
                break
            clear_console()
            print("Manga Metadata Fixer by HDShock")
            if first_run:
                print("\nFirst run  - Building Database! (This could take a while)")
            print("\nScanning New Manga" + frame)
            print("\n\nProcess Queue:\n\n")
            time.sleep(0.5)

def process_files(directory, log_file, db_path):
    """Processes .cbz files in the directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".cbz"):
                filepath = os.path.join(root, file)
                process_cbz_file(filepath, log_file, db_path)

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
    """Main function to process .cbz files in a directory tree, running every 5 minutes."""
    manga_directory = get_manga_directory()

    while True:
        # Clear screen and prepare the log file
        clear_console()
        print("Manga Metadata Fixer by HDShock")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(script_dir, "process_log.txt")
        db_path = os.path.join(script_dir, "processed_files.db")

        # Initialize the database
        first_run = initialize_database(db_path)

        # Check the log file size
        check_log_size(log_file)

        print(f"\nLog file location: {log_file}\n")

        # Setup for loading animation
        stop_flag = threading.Event()
        animation_thread = threading.Thread(target=loading_animation, args=(stop_flag, first_run))
        animation_thread.start()

        # Process files while the animation runs
        try:
            process_files(manga_directory, log_file, db_path)
        finally:
            stop_flag.set()  # Stop the loading animation
            animation_thread.join()  # Ensure the thread exits cleanly

        # Countdown timer for the next run
        wait_time = 300  # 5 minutes
        interval = 1  # Update every second
        while wait_time > 0:
            clear_console()
            print("Manga Metadata Fixer by HDShock")
            print(f"MANGA SCAN COMPLETED SUCCESSFULLY")
            print(f"Log file Exported to: {log_file}")
            print("\n-When the log file exceeds 50MB it will be deleted!-")
            print("\nNext Run:")
            print(f"Time remaining: {wait_time // 60} minutes and {wait_time % 60} seconds")
            time.sleep(interval)
            wait_time -= interval

if __name__ == "__main__":
    main()
