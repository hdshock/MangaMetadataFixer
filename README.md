<h1>Manga Metadata Fixer</h1>

<p>These are Python scripts designed to bridge the gap between <code>.CBZ</code> manga automatically downloaded from FMD2 and indexing by Komf for Kavita.</p>

<h2>Purpose</h2>
<p>The Manga Metadata Fixer is a Python script designed to automatically add basic metadata to your manga library by generating <code>ComicInfo.xml</code> files for <code>.cbz</code> archives. It works seamlessly with manga management tools like Komf and Kavita, bridging the gap for missing metadata in your library.</p>
<p>The script scans your manga library, processes <code>.cbz</code> files, and ensures that every manga archive has a <code>ComicInfo.xml</code> file containing the series name, title, and other necessary metadata.</p>

<h2>Features</h2>
<ul>
  <li>Automatically scans your manga library.</li>
  <li>Adds <code>ComicInfo.xml</code> to <code>.cbz</code> files that don't have it.</li>
  <li>Tracks processed files using an SQLite database to avoid reprocessing.</li>
  <li>Handles large libraries by processing files in batches and periodically updating the database.</li>
  <li>Displays a simple text-based progress bar to show the status of the scan.</li>
</ul>
<p><em>Note: For the "First Run" script only.</em></p>

<h2>Requirements</h2>
<ul>
  <li>Python 3.x</li>
  <li><code>zipfile</code> and <code>sqlite3</code> (included in Python's standard library)</li>
</ul>
<p>The program works out-of-the-box without any external dependencies.</p>

<h2>Installation</h2>
<ol>
  <li>Download the scripts and place them in a directory.</li>
  <li>Ensure that your manga library is accessible and organized.</li>
  <li>Make sure your <code>.cbz</code> files are properly named, and the folder name containing them matches the manga title. (FMD2 does this automatically.)</li>
</ol>

<h2>Setup</h2>
<p>The script will look for a file called <code>Manga Library Location</code> in the same directory to determine the path to your manga library. If the file does not exist, it will prompt you to enter the directory path.</p>
<p>An SQLite database (<code>processed_files.db</code>) is used to track which files have been processed, preventing redundant operations.</p>

<h2>Usage</h2>
<ol>
  <li>Place the script in any directory.</li>
  <li>Run the script in the terminal or command prompt.</li>
</ol>
<p><strong>If you have never run the script before, use the "First Run" script to build your database (it’s much faster).</strong></p>
<p>On the first run, the script will initialize the database and begin scanning your manga library. If the database already exists, the script will skip previously processed files and only process new ones. The script will display a progress bar showing the percentage of files processed.</p>
<p>The main script will loop and scan every 5 minutes, whereas the "First Run" script will close when finished. Both scripts can build the database, but one is optimized for speed while the other is better suited for continuous monitoring.</p>

<h2>How It Works</h2>
<ol>
  <li>The script scans all <code>.cbz</code> files in your manga library.</li>
  <li>For each <code>.cbz</code> file that does not already contain a <code>ComicInfo.xml</code>, the script generates a basic XML file with metadata such as the series name and title.</li>
  <li>The script updates the SQLite database to mark the file as processed.</li>
</ol>
<p>The program supports large libraries and can process files in batches to improve performance.</p>

<h2>Notes</h2>
<ul>
  <li><strong>Log File:</strong> All actions are logged in a file called <code>process_log.txt</code> in the script directory. The log file is deleted and recreated if it gets too large.</li>
  <li><strong>Database:</strong> The script uses an SQLite database (<code>processed_files.db</code>) to track processed files and ensure they aren’t processed again.</li>
  <li><strong>Journal Files:</strong> If the script is interrupted unexpectedly, journal files (<code>.db-journal</code>) may be left behind. The script cleans these up at startup to prevent issues.</li>
</ul>

<h2>License</h2>
<p>This script is free to use for personal purposes. It is provided "as is" with no warranty or guarantee. When using tools like this with Komf/Kavita/FMD2 together, a lot can happen, so testing is strongly advised before using it on your main manga library. (You can always delete or change the location file in the script directory.)</p>
