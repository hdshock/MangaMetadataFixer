# Manga Metadata Fixer
These are some Python scripts that help bridge the gap between .CBZ Manga automatically downloaded from FMD2 to be indexed by Komf for Kavita.

Purpose:
The Manga Metadata Fixer is a Python script designed to automatically add basic metadata to your manga library by generating ComicInfo.xml files for .cbz archives. It works seamlessly with manga management tools like Komf and Kavita, bridging the gap for missing metadata in your library.

The script scans your manga library, processes .cbz files, and ensures that every manga archive has a ComicInfo.xml file containing the series name, title, and other necessary metadata.

Features:
Automatically scans your manga library.
Adds ComicInfo.xml to .cbz files that don't have it.
Tracks processed files using an SQLite database, avoiding reprocessing.
Can handle large libraries by processing files in batches and updating the database periodically.
Uses a simple text-based progress bar to show the status of the scan. *For the "First Run" file only

Requirements:
Python 3.x
zipfile and sqlite3 (included in Python's standard library)
The program works out-of-the-box without any external dependencies.

Installation:
-Download the scripts and place them in a directory.
-Ensure that your manga library is accessible and organized.
-Make sure that your .cbz files are properly named and the folder name that contains them to match whatever manga it is. (this helps in creating proper metadata). - FMD2 does this automatically.


Setup:
The script will look for a file called "Manga Library Location" in the same directory to determine the path to your manga library. If the file does not exist, it will prompt you to enter the directory path.
The script uses an SQLite database (processed_files.db) to track which files have been processed, preventing redundant operations.
Usage:
Place the script in any directory.

Run the script in the terminal or command prompt.  

****IF YOU HAVE NEVER RUN THE SCRIPT BEFORE USE THE "FIRST RUN" SCRIPT TO BUILD YOUR DATABASE (IT'S MUCH FASTER)****

If it's the first run, the script will initialize the database and begin scanning your manga library.
If the database already exists, the script will skip previously processed files and only process new ones.
The script will display a progress bar showing the percentage of files processed.

The main script will loop and scan every 5 minutes, where the "First Run" script will close when finished.  Both scripts are capable of building the database, just one is built for speed and the other better suited to monitor continously.

How It Works:
The script scans all .cbz files in your manga library.
For each .cbz file that does not already contain a ComicInfo.xml, the script will generate a basic XML file with metadata such as the series name and title.
It then updates the SQLite database to mark the file as processed.
The program supports large libraries and can process files in batches to improve performance.

Notes:
Log File: All actions are logged in a file called process_log.txt that lives in the directory of the script.  This log file will get deleted and recreated if it gets too large

Database: The script uses an SQLite database (processed_files.db) to track processed files and ensure they aren't processed again.
Journal Files: If the script is interrupted unexpectedly, the journal files (.db-journal) may be left behind. The script will clean these up at the start to prevent issues.

License:
This script is free to use for personal purposes. It is provided "as is" with no warranty or guarantee.  When using tools like this with Komf/Kavita/FMD2 together, a lot can happen, so I urge you to test this before letting it loose on your main manga library.  (You can always just delete or change the location file in the script directory.)

