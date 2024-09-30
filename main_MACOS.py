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
import keyboard

# Replace with your folder path containing your images
source_path = r'/Users/harjotgill/Documents/Sticker-Repo-/processing_directory/Potential_Stickers'
# Replace with your downloads folder path
download_path = r'/Users/harjotgill/Downloads'
cartoon_website ='https://www.imgonline.com.ua/eng/cartoon-picture.php'
edge_intensity_max = 60
edge_intensity_min = 10
edge_intensity_increment = 10
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
    print("Setting up Webdriver...")
    # Set up WebDriver (replace with the path to your WebDriver)
    driver = webdriver.Chrome()

    print("Opening Website...")
    # Open the website
    driver.get(website)
    print("Website successfully opened")
    return driver

def get_images(directory):
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
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)

        if os.path.isdir(folder_path):
            subprocess.Popen(['open', folder_path])
            while True:
                user_input = input("Enter the edge intensity value to keep for images in " + folder + ": ")
                regex_pattern = r'EdgeIntensity_' + user_input
                match, matching_filename = check_for_match(folder_path, regex_pattern)
                if match:
                    keep(matching_filename, folder_path)
                    break
                else:
                    print("No match found")
                    continue

def keep(filename, folder_path):
    for file in os.listdir(folder_path):
        if file != filename:
            os.remove(os.path.join(folder_path, file))
            print("Removed " + file)
    print("\n")

def check_for_match(folder_path, pattern):   
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg"):
            match = re.search(pattern, filename)
            if match:
                print("Match found. Keeping " + filename)
                return True, filename
    return False, None          

def move_to_current_directory(directory):
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
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):
            if not os.listdir(folder_path):
                os.rmdir(folder_path)
    print("Removed empty folders")

def main():
    move_zip_to_directory()
    unzip_folder()
    image_files = get_images(source_path)
    driver = setup_driver(cartoon_website)
    wait = WebDriverWait(driver, 10)  # Initialize WebDriverWait object
    automation_loop(image_files, driver, wait)
    picture_picker(source_path)
    move_to_current_directory(source_path)
    remove_empty_folders(source_path)
    
    print("Finished!")
    
    # subprocess.Popen(f'explorer {source_path}')

main()
