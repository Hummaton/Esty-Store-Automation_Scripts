"""
Author: Harjot Gill
Email: harjotgill2025@gmail.com 

Description:

This script automates the process of converting images to cartoon-style images using a web service. It performs the following tasks:
    1. Moves a specified zip file from the downloads directory to a processing directory.
    2. Unzips the folder containing potential sticker images.
    3. Converts all images in the specified directory to JPG format.
    4. Sets up a Selenium WebDriver to interact with a cartoon image conversion website.
    5. Automates the process of uploading images to the website, adjusting edge intensity settings, and downloading the processed images.
    6. Plays a sound notification upon completion.
    7. Organizes the processed images into folders based on their original filenames.
    8. Allows the user to select the best cartoonified image based on edge intensity.
    9. Moves all selected images to the main directory and removes empty folders.

Functions:
- move_zip_to_directory(): Moves a specified zip file from the downloads directory to the processing directory.
- unzip_folder(): Unzips the folder containing potential sticker images.
- convert_images_to_jpg(directory): Converts all images in the specified directory to JPG format.
- setup_driver(website): Sets up a Selenium WebDriver to interact with the specified website.
- get_images(directory): Retrieves a list of image files from the specified directory.
- automation_loop(image_files, driver, wait): Automates the process of uploading images to the website, adjusting edge intensity settings, and downloading the processed images.
- move_downloaded_file(edge_intensity_value, folder_dst_path): Moves the downloaded file to the specified folder and renames it based on edge intensity.
- assert_finished(wait, element): Waits for the image processing to complete and clicks the download button.
- send_cartoonify(driver, edge_intensity_value, image_file, image_path): Uploads an image to the website and sets the edge intensity for cartoonification.
- get_valid_directory(): Prompts the user to enter a valid directory path.
- check_directory(path): Checks if the specified directory exists and contains image files.
- picture_picker(directory): Allows the user to select the best cartoonified image based on edge intensity.
- keep(filename, folder_path): Keeps the specified file and removes all other files in the folder.
- check_for_match(folder_path, pattern): Checks if a file matching the specified pattern exists in the folder.
- move_to_current_directory(directory): Moves all files from subdirectories to the main directory.
- remove_empty_folders(directory): Removes all empty folders in the specified directory.
- playSound(sound_file): Plays a sound notification upon completion.
- assert_empty_directory(directory): Checks if the specified directory is empty and prompts the user to clear it if not.
- main(): Main function that orchestrates the entire automation process.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import glob
import os
import subprocess
import webbrowser
import shutil
from PIL import Image
import time
import pygetwindow as gw
import re
import zipfile
import pygame

# Replace with your folder path containing your images
source_path = r'/Users/harjotgill/Documents/Sticker-Repo-/processing_directory/Potential_Stickers'
# Replace with your downloads folder path
download_path = r'/Users/harjotgill/Downloads'

# Website for processing images
cartoon_website ='https://www.imgonline.com.ua/eng/cartoon-picture.php'

# Edge intensity settings from the website
edge_intensity_max = 30
edge_intensity_min = 10
edge_intensity_increment = 10

# Zip file containing potential sticker images from Google photos Album
zip_filename = 'potential stickers-001.zip'

# Set up browser options for download preferences
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,  # Disable prompt for download
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)


def move_zip_to_directory():
    """
    Moves a ZIP file from the download directory to a specified destination directory.
    This function constructs the source path of the ZIP file using the `download_path` and `zip_filename` variables.
    It then constructs the destination path using the `source_path` variable. If the ZIP file exists at the source path,
    it moves the file to the destination directory and prints a success message. If the file does not exist, it prints
    an error message.
    Returns:
        bool: True if the ZIP file was successfully moved, False otherwise.
    """
    source_zip_path = os.path.join(download_path, zip_filename)
    destination_folder_path = source_path

    if os.path.exists(source_zip_path):
        shutil.move(source_zip_path, destination_folder_path)
        print(f"Moved '{zip_filename}' to '{destination_folder_path}'")
        return True 
    else:
        print(f"'{zip_filename}' not found in Downloads directory.")
        return False
    

def unzip_folder():
    """
    Unzips a specified zip file located in the source path.
    This function checks if the zip file exists in the source path. If it does,
    it extracts all files from the zip file to the source path, avoiding the creation
    of directories. After extraction, the zip file is removed from the source path.
    Parameters:
    None
    Returns:
    None
    Prints:
    - A message indicating the start of the unzipping process.
    - A message indicating the removal of the zip file.
    - A message if the zip file is not found in the specified directory.
    """
    zip_file_path = os.path.join(source_path, zip_filename)

    if os.path.exists(zip_file_path):
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            print(f"Unzipping '{zip_filename}' in '{source_path}'")
            # Iterate through the files in the zip file
            for member in zip_ref.namelist():
                # Get the file's basename (to avoid directory creation)
                filename = os.path.basename(member)
                if not filename:
                    continue  # Skip directories

                # Extract the file to the specified directory
                target_path = os.path.join(source_path, filename)
                with zip_ref.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())

        # Remove the zip file
        os.remove(zip_file_path)
        print(f"Removed '{zip_filename}'")
    else:
        print(f"'{zip_filename}' not found in the specified directory.")


                   
def convert_images_to_jpg(directory):
    """
    Converts all images in the specified directory to JPG format.

    This function scans the given directory for image files. It converts any image
    that is not already in JPG format to JPG. If an image is in RGBA mode, it will
    be converted to RGB before saving as JPG. The original files are removed after
    conversion. If a file named ".DS_Store" is found, it will be deleted.

    Args:
        directory (str): The path to the directory containing the images to be converted.

    Returns:
        list: A list of filenames of the converted JPG images.

    Raises:
        Exception: If an error occurs during the conversion process, the error is printed,
                   a web browser is opened to the CloudConvert image converter, and the
                   program exits with status 1.
    """
    image_files = []  # Create an empty list to store the image filenames
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isdir(file_path):
            continue  # Skip folders
        if filename.endswith(".jpg"):
            image_files.append(filename)
            continue
        if filename == ".DS_Store":
            os.remove(file_path)
            continue    
        try:
            img = Image.open(file_path)
            if img.mode == "RGBA":
                img = img.convert("RGB")  # Convert RGBA to RGB
            jpg_filename = os.path.splitext(filename)[0] + ".jpg"
            img.save(os.path.join(directory, jpg_filename))
            print(f"Converted {filename} to {jpg_filename}")
            os.remove(file_path)  # Remove the old file
            image_files.append(jpg_filename)  # Append the converted image filename to the list
        except Exception as e:
            print(f"Error converting {filename}: {e}")
            webbrowser.open("https://cloudconvert.com/image-converter")
            exit(1)
    print("All images converted to jpg successfully.")
    return image_files  # Return the list of image filenames


def setup_driver(website):
    """
    Set up a Chrome WebDriver and open the specified website.
    Args:
        website (str): The URL of the website to open.
    Returns:
        WebDriver: An instance of the Chrome WebDriver with the specified website opened.
    """
    print("Setting up Webdriver...")
    # Set up WebDriver (replace with the path to your WebDriver)
    driver = webdriver.Chrome()

    print("Opening Website...")
    # Open the website
    driver.get(website)
    print("Website successfully opened")
    return driver


def get_images(directory):
    """
    Retrieves a list of image files from the specified directory, excluding system files like .DS_Store.
    Args:
        directory (str): The path to the directory containing image files.
    Returns:
        list: A list of image file names in the specified directory.
    Notes:
        - If the specified directory is not valid, it will prompt the user to provide a valid directory.
        - The function prints the path and names of the images to be processed.
    """
    global source_path
    if not check_directory(directory):
        source_path = get_valid_directory()
        directory = source_path

    # List all files in the source directory
    files = os.listdir(directory)

    # Filter image files
    image_files = [f for f in files]

    #Delete .DS_Store file
    if ".DS_Store" in image_files:
        image_files.remove(".DS_Store")
    
    print("Images to cartoonify from path '" + source_path + "'")
    for image_file in image_files:
        print(image_file)

    return image_files


def automation_loop(image_files, driver, wait):
    """
    Automates the process of cartoonifying images using a web-based tool.
    Args:
        image_files (list): List of image file names to be processed.
        driver (selenium.webdriver): Selenium WebDriver instance for browser automation.
        wait (selenium.webdriver.support.ui.WebDriverWait): WebDriverWait instance for handling waits.
    Workflow:
        1. For each image file in the list:
            a. Create a folder named after the image file (without extension) if it doesn't exist.
            b. Move the image file to its respective folder.
            c. Begin the cartoonization process for the image file.
            d. For each edge intensity value in the specified range:
                i. Send the image to the cartoonify web tool.
                ii. Wait for the processing to complete.
                iii. Download the processed image.
                iv. Move the downloaded file to the respective folder.
        2. Close the browser after processing all images.
    Note:
        - The function assumes the existence of certain global variables such as `source_path`, 
          `edge_intensity_min`, `edge_intensity_max`, `edge_intensity_increment`, and `cartoon_website`.
        - The helper functions `send_cartoonify`, `assert_finished`, and `move_downloaded_file` 
          are used within this function but are not defined here.
    """
    for image_file in image_files:
        folder_dst_name = os.path.splitext(image_file)[0]  # Extract file name without extension
        folder_dst_path = os.path.join(source_path, folder_dst_name)

        # Create folder if it doesn't exist
        os.makedirs(folder_dst_path, exist_ok=True)
        #print("\nCreated folder to store " + image_file + " and cartoonified versions")

        # Move image file to its respective folder
        src = os.path.join(source_path, image_file)
        dst = os.path.join(folder_dst_path, image_file)
        shutil.move(src, dst)
        # print("Moving image to new folder and beginning cartoonization...")

        print("Beginning cartoonization for " + image_file)
        for edge_intensity_value in range(edge_intensity_min, edge_intensity_max + 1, edge_intensity_increment):
            send_cartoonify(driver, edge_intensity_value, image_file, folder_dst_path)
            #print("Waiting for webpage to load...")
            time.sleep(5)
            assert_finished(wait, "Download processed image")
            driver.get(cartoon_website)
            time.sleep(8)
            move_downloaded_file(edge_intensity_value, folder_dst_path)

    # Close the browser after saving all processed images
    print("Finished! Closing driver now...")
    driver.quit()


def move_downloaded_file(edge_intensity_value, folder_dst_path):
    """
    Moves the most recently downloaded file from the downloads folder to a specified destination folder,
    renaming it to include an edge intensity prefix if it matches a specific regex pattern.

    Args:
        edge_intensity_value (str): The edge intensity value to prefix the file name with.
        folder_dst_path (str): The destination folder path where the file should be moved.

    Raises:
        Exception: If an error occurs during the file operation, it retries after a delay.
    """
    try:
        # Find the newest downloaded file in the downloads folder
        list_of_files = glob.glob(os.path.join(download_path, "*"))
        latest_file = max(list_of_files, key=os.path.getctime)
        # Check if the latest downloaded file matches the regex pattern
        regex_pattern = r'imgonline-com-ua-CartoonPicture.*\.jpg'
        if re.match(regex_pattern, os.path.basename(latest_file)):
            # Rename the latest downloaded file to include edge intensity prefix
            new_file_name = f"EdgeIntensity_{edge_intensity_value}_{os.path.basename(latest_file)}"
            new_file_path = os.path.join(folder_dst_path, new_file_name)
            os.rename(latest_file, new_file_path)
        else:
            print("Downloaded file doesn't match the expected pattern or does not exist")
            exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Retrying...")
        time.sleep(5)
        move_downloaded_file(edge_intensity_value, folder_dst_path)


def assert_finished(wait, element):
    """
    Waits for a specific element to be present on the page and clicks it once found.
    Args:
        wait (WebDriverWait): The WebDriverWait instance used to wait for the element.
        element (str): The text of the element to wait for and click.
    Raises:
        TimeoutException: If the element is not found within the specified wait time.
        Exception: For any other exceptions that occur during the process.
    Prints:
        Status messages indicating the progress of locating and clicking the element.
    """
    # Wait for the elements indicating the image processing is complete on the result page
    try:
        print("Locating download button...")
        download_button = wait.until(EC.presence_of_element_located((By.XPATH, f'//a[b[text()="{element}"]]')))
    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

    print(f"Downloading image...")  # Print statement when the element is found
    download_button.click()


def send_cartoonify(driver, edge_intensity_value, image_file, image_path):
    """
    Automates the process of uploading an image and setting parameters for cartoonification using a web driver.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web page.
        edge_intensity_value (int): The value to set for edge intensity.
        image_file (str): The name of the image file to be uploaded.
        image_path (str): The path to the directory containing the image file.
    Raises:
        NoSuchElementException: If any of the required elements (file input, edge intensity input, image quality input, or submit button) are not found on the web page.
    Example:
        send_cartoonify(driver, 5, 'example.jpg', '/path/to/images')
    """
    try:
        upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
        upload_input.send_keys(os.path.join(image_path, image_file))  # Provide full path

        # Set edge intensity
        edge_intensity = driver.find_element(By.NAME, 'efset4')
        edge_intensity.clear()
        edge_intensity.send_keys(str(edge_intensity_value))  # Adjust edge intensity

        img_quality = driver.find_element(By.NAME, 'jpegqual')  # Use By.NAME for finding elements
        img_quality.clear()
        img_quality.send_keys('100')  # Set segmentation level to 7

        print("Sending " + image_file + " with Edge Intensity " + str(edge_intensity_value))
        # Submit the form or initiate processing (assuming a button click)
        submit_button = driver.find_element(By.XPATH, '//input[@type="submit"]')
        submit_button.click()

    except NoSuchElementException:
        print("Upload input element not found!")  # Print message if the element is not found
        # Handle the case when the element is not found or perform additional actions


def get_valid_directory():
    """
    Prompts the user to continue and enter a valid directory path.
    The function repeatedly asks the user if they want to continue. If the user
    chooses to continue by entering 'Y', they are prompted to enter a directory path.
    The entered path is then validated using the `check_directory` function. If the
    directory is valid, the path is returned. If the directory is invalid or no path
    is provided, the user is prompted again. If the user chooses not to continue by
    entering 'N', the program exits.
    Returns:
        str: A valid directory path provided by the user.
    Raises:
        SystemExit: If the user chooses not to continue.
    """
    continue_request = input("Continue? Enter (Y/N): ").lower()

    if continue_request == "y":
        print("Please enter the path to the folder containing your pictures")
        new_path = input("Path: ")
        if new_path:  # If a directory is provided
            if check_directory(new_path):
                return new_path
            else:
                print("Invalid directory!")
                return get_valid_directory()
        else:
            print("No directory provided!")
            return get_valid_directory()
    else:
        print("Adios!")
        exit(0)


def check_directory(path):
    """
    Checks if the given path is a valid directory and contains image files.
    Args:
        path (str): The path to the directory to check.
    Returns:
        bool: True if the directory exists, is a directory, and contains image files; False otherwise.
    Prints:
        - "The directory path does not exist." if the path does not exist.
        - "The provided path is not a directory." if the path is not a directory.
        - "The directory does not contain any image files." if the directory does not contain any image files.
    """
    if not os.path.exists(path):
        print("The directory path does not exist.")
        return False

    if not os.path.isdir(path):
        print("The provided path is not a directory.")
        return False

    # Get all files in the directory
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.PNG', '.gif', '.png', '.JPG', '.JPEG', '.GIF'))]

    if not image_files:
        print("The directory does not contain any image files.")
        return False

    return True


def picture_picker(directory):
    """
    Opens all images in each subfolder of the given directory and prompts the user to enter an edge intensity value.
    If a match is found for the entered edge intensity value, the corresponding image is kept and all others are closed.
    Args:
        directory (str): The path to the main directory containing subfolders with images.
    Raises:
        FileNotFoundError: If the specified directory does not exist.
        ValueError: If the user input for edge intensity is invalid.
    Notes:
        - The function uses the 'open' command to open images on macOS.
        - The function uses 'osascript' to close Preview windows on macOS.
        - The function expects images to have extensions: .jpg, .jpeg, .png, .gif.
        - The function relies on the 'check_for_match' and 'keep' functions which are not defined in this snippet.
    """
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):
            # Select all images in the folder and open them together
            image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            
            if image_files:
                subprocess.Popen(['open'] + image_files)
                while True:
                    user_input = input("Enter the edge intensity value to keep for images in " + folder + ": ")
                    regex_pattern = r'EdgeIntensity_' + user_input
                    match, matching_filename = check_for_match(folder_path, regex_pattern)
                    if match:
                        for image_file in image_files:
                            subprocess.call(["osascript", "-e", 'tell application "Preview" to close windows'])
                        keep(matching_filename, folder_path)
                        break
                    else:
                        print("No match found")
                        continue
                    
            else:
                print(f"No images found in folder {folder}")
        
           
def keep(filename, folder_path):
    """
    Removes all files in the specified folder except for the given filename.

    Args:
        filename (str): The name of the file to keep.
        folder_path (str): The path to the folder where files will be removed.

    Returns:
        None
    """
    for file in os.listdir(folder_path):
        if file != filename:
            os.remove(os.path.join(folder_path, file))
            print("Removed " + file)
    print("\n")


def check_for_match(folder_path, pattern):   
    """
    Checks for a file in the specified folder that matches the given pattern.

    Args:
        folder_path (str): The path to the folder where the files are located.
        pattern (str): The regex pattern to match the filenames against.

    Returns:
        tuple: A tuple containing a boolean and a string. The boolean is True if a match is found, 
               otherwise False. The string is the filename of the matched file if a match is found, 
               otherwise None.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg"):
            match = re.search(pattern, filename)
            if match:
                print("Match found. Keeping " + filename)
                return True, filename
    return False, None          


def move_to_current_directory(directory):
    """
    Moves all files from subdirectories within the given directory to the given directory itself.
    Args:
        directory (str): The path to the directory where files should be moved.
    Raises:
        FileNotFoundError: If the provided directory does not exist.
        PermissionError: If there are permission issues accessing the directory or its contents.
        shutil.Error: If an error occurs during the file moving process.
    Example:
        move_to_current_directory('/path/to/directory')
    """
    # Iterate through each item in the provided directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        if os.path.isdir(item_path):
            # Iterate through each item in the subdirectory
            for sub_item in os.listdir(item_path):
                sub_item_path = os.path.join(item_path, sub_item)

                # Form the new path for moving the sub-item
                new_sub_item_path = os.path.join(directory, sub_item)
                # Move the sub-item to the directory one level below
                shutil.move(sub_item_path, new_sub_item_path)
    print("Moved all files to current directory")
    

def remove_empty_folders(directory):
    """
    Removes empty folders within the specified directory.

    Args:
        directory (str): The path to the directory to scan for empty folders.

    Returns:
        None
    """
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):
            if not os.listdir(folder_path):
                os.rmdir(folder_path)
    print("Removed empty folders")


def playSound(sound_file):
    """
    Plays a sound file using the pygame library.

    Args:
        sound_file (str): The path to the sound file to be played.

    Raises:
        ImportError: If the pygame module is not found.
        Exception: If any other error occurs during the execution.

    Note:
        Ensure that the pygame library is installed before using this function.
        The function will block until the sound file has finished playing.
    """
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    except ImportError:
        print("pygame module not found. Please install it using 'pip install pygame'.")
    except Exception as e:
        print(f"An error occurred: {e}")


def assert_empty_directory(directory):
    """
    Checks if the specified directory is empty. If the directory is not empty, 
    prompts the user to clear it. If the user agrees, clears the directory. 
    Otherwise, opens the directory in Finder and exits the script.

    Args:
        directory (str): The path to the directory to check.

    Raises:
        SystemExit: Exits the script if the user chooses not to clear the directory.
    """
    if not os.listdir(directory):
        print(f"Directory '{directory}' is empty.")
    else:
        print(f"Directory '{directory}' is not empty. Would you like to clear it?")
        user_input = input("Enter (Y/N): ").lower()
        if user_input == "y":
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            print(f"Cleared '{directory}'")
        else:
            print("Exiting and opening in Finder...")
            subprocess.Popen(['open', directory])
            exit(0)


def main():
    """
    Main function to automate the process of handling image files and interacting with a cartoon website.

    Steps:
    1. Ensure the source directory is empty.
    2. Move zip files to the source directory.
    3. Unzip the folder.
    4. Retrieve image files from the source directory.
    5. Set up the web driver for the cartoon website.
    6. Initialize WebDriverWait object.
    7. Perform the automation loop with the image files, driver, and wait object.
    8. Play a sound notification upon completion.
    9. Pick pictures from the source directory.
    10. Move files to the current directory.
    11. Remove any empty folders in the source directory.
    12. Print a completion message.
    """
    assert_empty_directory(source_path)
    move_zip_to_directory()
    unzip_folder()
    image_files = get_images(source_path)
    driver = setup_driver(cartoon_website)
    wait = WebDriverWait(driver, 10)  # Initialize WebDriverWait object
    automation_loop(image_files, driver, wait)
    playSound("Oven-Timer-Ding.mp3")
    picture_picker(source_path)
    move_to_current_directory(source_path)
    remove_empty_folders(source_path)
    print("Finished!")

if __main__ == "__main__":
    main()
