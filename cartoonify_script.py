from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import tkinter as tk
from tkinter import filedialog
import glob
import shutil
import os
import subprocess
import time
import re

# Replace with your folder path containing your images
source_path = r'C:\Users\harry\Desktop\Stickers\Potential_Stickers'
# Replace with your downloads folder path
download_path = r'C:\Users\harry\Downloads'
edge_intensity_max = 50
edge_intensity_min = 10
edge_intensity_increment = 10

# Set up browser options for download preferences
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,  # Disable prompt for download
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)


def main():
    global source_path
    if not check_directory(source_path):
        source_path = get_valid_directory()

    # List all files in the source directory
    files = os.listdir(source_path)

    # Filter image files
    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

    print("Images to cartoonify from path '" + source_path + "'")
    for image_file in image_files:
        print(image_file)

    print("Setting up Webdriver...")
    # Set up WebDriver (replace with the path to your WebDriver)
    driver = webdriver.Chrome()

    print("Opening Website...")
    # Open the website
    driver.get('https://www.imgonline.com.ua/eng/cartoon-picture.php')
    print("Website successfully opened")

    wait = WebDriverWait(driver, 10)  # Initialize WebDriverWait object

    for image_file in image_files:
        folder_dst_name = os.path.splitext(image_file)[0]  # Extract file name without extension
        folder_dst_path = os.path.join(source_path, folder_dst_name)

        # Create folder if it doesn't exist
        os.makedirs(folder_dst_path, exist_ok=True)
        print("\nCreated folder to store " + image_file + " and cartoonified versions")

        # Move image file to its respective folder
        src = os.path.join(source_path, image_file)
        dst = os.path.join(folder_dst_path, image_file)
        shutil.move(src, dst)
        print("Moving image to new folder and beginning cartoonization...")

        for edge_intensity_value in range(edge_intensity_min, edge_intensity_max + 1, edge_intensity_increment):
            send_cartoonify(driver, edge_intensity_value, image_file, folder_dst_path)
            print("Waiting for webpage to load...")
            time.sleep(5)
            assert_finished(wait, "Download processed image")
            driver.get('https://www.imgonline.com.ua/eng/cartoon-picture.php')
            time.sleep(3)
            move_downloaded_file(edge_intensity_value, folder_dst_path)

    # Close the browser after saving all processed images
    print("Finished! Closing driver now...")
    driver.quit()
    subprocess.Popen(f'explorer {source_path}')


def move_downloaded_file(edge_intensity_value, folder_dst_path):
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
        print("Please select the folder containing your pictures")
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        new_path = filedialog.askdirectory()
        if new_path:  # If a directory is selected
            if check_directory(new_path):
                return new_path
            else:
                print("Invalid directory!")
                return get_valid_directory()
        else:
            print("No directory selected!")
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

    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

    if not image_files:
        print("The directory does not contain any image files.")
        return False

    return True


main()
