import os
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import tkinter as tk
from tkinter import filedialog
import glob
import subprocess
import webbrowser
import shutil
from PIL import Image
import time
import pygetwindow as gw
import re
import zipfile
import keyboard

edge_intensity_max = 60
edge_intensity_min = 10
edge_intensity_increment = 10

picture_extensions = (".jpg", ".jpeg", ".png", "avif")
downloads_path = r'C:\Users\harry\Downloads'  # Update with your Downloads directory path
potential_stickers_path = r'C:\Users\harry\Desktop\Stickers\Potential_Stickers'  # Update with the destination directory path
zip_filename = 'potential stickers.zip'
quality_scaler_path = r'C:\Users\harry\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam\QualityScaler.url'  # Update with the path to your Quality Scaler application
audio_path = r'C:\Users\harry\Desktop\Stickers\Scripts\Oven-Timer-Ding.mp3' # Update with the path to your audio file
cartoon_website ='https://www.imgonline.com.ua/eng/cartoon-picture.php'
zip_filename = 'potential stickers.zip'

# Set up browser options for download preferences
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": downloads_path,
    "download.prompt_for_download": False,  # Disable prompt for download
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)


def move_zip_to_directory():
    source_zip_path = os.path.join(downloads_path, zip_filename)
    destination_folder_path = potential_stickers_path

    if os.path.exists(source_zip_path):
        shutil.move(source_zip_path, destination_folder_path)
        print(f"Moved '{zip_filename}' to '{destination_folder_path}'")
        return True 
    else:
        print(f"'{zip_filename}' not found in Downloads directory.")
        return False

def move_to_current_directory():
    # Move picture files from each folder to the current directory
    for folder in os.listdir():
        folder_path = os.path.join(os.getcwd(), folder)
        if os.path.isdir(folder_path) and os.access(folder_path, os.R_OK):
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    ext = os.path.splitext(item_path)[1].lower()
                    if ext in picture_extensions:
                        dest = item_path
                        if os.path.exists(dest):
                            filename, file_extension = os.path.splitext(item_path)
                            dest = f"{filename}_renamed{file_extension}"
                        shutil.move(item_path, dest)
                        print(f"Moved '{item_path}' from '{folder}' to '{dest}' in the current directory.")
                        return True
                    
def convert_images_to_jpg(directory):
    image_files = []  # Create an empty list to store the image filenames
    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            image_files.append(filename)
            continue
        try:
            img = Image.open(os.path.join(directory, filename))
            jpg_filename = os.path.splitext(filename)[0] + ".jpg"
            img.save(os.path.join(directory, jpg_filename))
            print(f"Converted {filename} to {jpg_filename}")
            os.remove(os.path.join(directory, filename))  # Remove the old file
            image_files.append(jpg_filename)  # Append the converted image filename to the list
        except Exception as e:
            print(f"Error converting {filename}: {e}")
            webbrowser.open("https://cloudconvert.com/image-converter")
            exit(1)
    print("All images converted to jpg successfully.")
    return image_files  # Return the list of image filenames

def unzip_folder():
    zip_file_path = os.path.join(potential_stickers_path, zip_filename)

    if os.path.exists(zip_file_path):
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            print(f"Unzipping '{zip_filename}' in '{potential_stickers_path}'")
            zip_ref.extractall(potential_stickers_path)
        os.remove(zip_file_path)  # Remove the zip file
        print(f"Removed '{zip_filename}'")
    else:
        print(f"'{zip_filename}' not found in the specified directory.")

def run_application(application_path):
    if os.path.exists(application_path):
        webbrowser.open(application_path)
        print(f"Opened quality scaler app: {application_path}")
    else:
        print(f"Application path not found: {application_path}")
        exit(1)

def enter_parameters():
    pyautogui.hotkey('win', 'd')  # Minimize all windows    
    time.sleep(10)  # Wait for 10 seconds
    pyautogui.click(492, 268)  
    pyautogui.hotkey('win', 'right')  # Move the window to the right side of the screen
    time.sleep(1)  # Wait for 1 second

    pyautogui.click(1171, 719)
    pyautogui.click(1127, 867) #change AI model to SAFMNLx4_Real

    pyautogui.click(1184, 848)
    pyautogui.click(1135, 900) #changes AI precision

    pyautogui.click(1180, 970)
    pyautogui.click(1142, 892) #changes sets Interpolation to Low

    pyautogui.click(1420, 589)
    pyautogui.click(1393, 643) #image output turns into jpg

   # pyautogui.click(1431, 843)
   # pyautogui.click(1382, 896) #Utilizes GPU

    pyautogui.click(1458, 967)
    pyautogui.hotkey('ctrl', 'a')  
    pyautogui.press('backspace')  
    pyautogui.typewrite('6')  # Enter correct VRAM for GPU

    pyautogui.click(1736, 592) #click on select button
    pyautogui.hotkey('ctrl', 'a')  # Select all text in the input line
    pyautogui.press('backspace')  # Delete the selected text
    pyautogui.typewrite('100')  # Enter "100" into the input Res line

    pyautogui.click(1458, 384)  # Click on the select button
    
def select_images(potential_stickers_path):
    time.sleep(2)  # Wait for the file explorer tab to open
    pyautogui.typewrite(potential_stickers_path)  # Type the path to the directory
    pyautogui.press('enter')  # Press enter to confirm the path
    pyautogui.click(1546, 677)  # Click on center of the window
    pyautogui.hotkey('ctrl', 'a')  # Select all images
    print("Selected", len(os.listdir(potential_stickers_path)), "images")
    pyautogui.press('enter')  # Press enter to confirm the selection
    time.sleep(5)  # Wait for the images to load
    pyautogui.click(1750, 963)  # Click on upscale button

def check_progress(ammount_of_images):
    wait_time = 0
    print("waiting for processing to complete...")

    while True:
        current_ammount_of_images = len(os.listdir(potential_stickers_path))
        wait_time += 3
        if current_ammount_of_images >= 2 * ammount_of_images:
            print("Processing complete! Total wait time was", wait_time, "seconds")
            break
        time.sleep(3)  # Check directory size every 3 seconds
        if current_ammount_of_images != len(os.listdir(potential_stickers_path)):
            print("Processed", len(os.listdir(potential_stickers_path)) - ammount_of_images,
             "images so far...")

def get_directory_size(directory):
    total = 0
    for path, dirs, files in os.walk(directory):
        for f in files:
            fp = os.path.join(path, f)
            total += os.path.getsize(fp)
    return total

def remove_images(old_images):
    for filename in old_images:
            os.remove(os.path.join(potential_stickers_path, filename))
            print(f"Removed previous file: {filename}")

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
    global potential_stickers_path
    if not validate_directory(directory):
        potential_stickers_path = get_valid_directory()

    # List all files in the source directory
    files = os.listdir(directory)

    # Filter image files
    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    
    print("Images to cartoonify from path '" + potential_stickers_path + "'")
    for image_file in image_files:
        print(image_file)

    return image_files

def automation_loop(image_files, driver, wait):
    for image_file in image_files:
        folder_dst_name = os.path.splitext(image_file)[0]  # Extract file name without extension
        folder_dst_path = os.path.join(potential_stickers_path, folder_dst_name)

        # Create folder if it doesn't exist
        os.makedirs(folder_dst_path, exist_ok=True)
        #print("\nCreated folder to store " + image_file + " and cartoonified versions")

        # Move image file to its respective folder
        src = os.path.join(potential_stickers_path, image_file)
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
        list_of_files = glob.glob(os.path.join(downloads_path, "*"))
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
        print("Please select the folder containing your pictures")
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        new_path = filedialog.askdirectory()
        if new_path:  # If a directory is selected
            if validate_directory(new_path):
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

def validate_directory(path):
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

def open_popup_windows(popup_text):
    # Open a popup window to display instructions
    root = tk.Tk()
    root.title("Instructions")
    root.geometry("400x200")
    root.resizable(False, False)
    root.configure(background="white")

    label = tk.Label(root, text=popup_text)
    label.pack()

    root.mainloop()

def picture_picker(directory):
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)

        if os.path.isdir(folder_path):
            subprocess.Popen(f'explorer {folder_path}')
            while True:
                user_input = track_first_two_digits()
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

def track_first_two_digits():
    digits = ""
    while len(digits) < 2:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            char = event.name
            if char.isdigit():
                digits += char
            elif char == 'backspace':
                print("input reset")
                digits = ""  # Reset digits variable
            elif char == 'esc':
                print("Exiting...")
                exit(0)
    return digits

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
    # move_zip_to_directory()
    # unzip_folder()
    # if not validate_directory(potential_stickers_path):
    #     exit(1)
    # old_images = convert_images_to_jpg(potential_stickers_path) 
    # run_application(quality_scaler_path)
    # enter_parameters()
    # ammount_of_images = len(os.listdir(potential_stickers_path)) 
    # size_of_directory = get_directory_size(potential_stickers_path)   
    # select_images(potential_stickers_path)
    # check_progress(ammount_of_images)  
    # os.startfile(audio_path)      
    # remove_images(old_images)
    # print("Size of old directory:", size_of_directory/1000000, "MB")
    # print("Size of new directory:", get_directory_size(potential_stickers_path)/1000000, "MB")
    
    # # Beginning of cartoonification process
    # image_files = get_images(potential_stickers_path)
    # driver = setup_driver(cartoon_website)
    # wait = WebDriverWait(driver, 10)  # Initialize WebDriverWait object
    # automation_loop(image_files, driver, wait)
    # os.startfile(r'C:\Users\harry\Desktop\Stickers\Scripts\Oven-Timer-Ding.mp3')      

    # open_popup_windows("When each folder opens on screen,\n please type the edge intensity value you want to keep for that folder.\n" +
    #                     "If you want to keep the image with Edge Intensity with 20,\n simply type '20' on your keyboard and it will move onto the next folder" +
    #                      "\n.... Understood?")
    picture_picker(potential_stickers_path)
    move_to_current_directory(potential_stickers_path)
    remove_empty_folders(potential_stickers_path)
    print("Finished!")
    subprocess.Popen(f'explorer {potential_stickers_path}')

main()
