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
import threading

edge_intensity_max = 70
edge_intensity_min = 20
edge_intensity_increment = 15
maximum_threads = 8

picture_extensions = (".jpg", ".jpeg", ".png", "avif")
downloads_path = r'C:\Users\harry\Downloads'  # Update with your Downloads directory path
potential_stickers_path = r'C:\Users\harry\Desktop\Stickers\processing_directory\Potential_Stickers'  # Update with the destination directory path
enhancedImages_path = r'C:\Users\harry\Desktop\Stickers\processing_directory\Enhanced_Images'  # Update with the destination directory path
cartoonified_images_path = r'C:\Users\harry\Desktop\Stickers\processing_directory\Cartoonified_Images'  # Update with the destination directory path
zip_filename = 'potential stickers.zip'
quality_scaler_path = r'C:\Users\harry\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam\QualityScaler.url'  # Update with the path to your Quality Scaler application
audio_path = r'C:\Users\harry\Desktop\Stickers\Scripts\Oven-Timer-Ding.mp3' # Update with the path to your audio file
cartoon_website ='https://www.imgonline.com.ua/eng/cartoon-picture.php'
zip_filename = 'potential stickers.zip'

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

    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.PNG', '.gif'))]

    if not image_files:
        print("The directory does not contain any image files.")
        return False

    return True

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
    newest_files = []  # Create an empty list to store newest files
    current_image_being_cartoonified = 0

    while True:
        images_enhanced = len(os.listdir(enhancedImages_path))
        wait_time += 3
        current_threads = threading.active_count()

        if ammount_of_images != len(os.listdir(potential_stickers_path)):
            move_newest_image(potential_stickers_path, enhancedImages_path)
            images_enhanced = len(os.listdir(enhancedImages_path))
            images_remaining = ammount_of_images - images_enhanced
            print("Enhanced", images_enhanced, "images so far..." + str(images_remaining) + " images remaining")
            
            # Retrieve the newest file from enhancedImages_path
            files = [os.path.join(enhancedImages_path, f) for f in os.listdir(enhancedImages_path) if os.path.isfile(os.path.join(enhancedImages_path, f))]
            newest_file = max(files, key=os.path.getmtime, default=None)
            newest_files.append(newest_file)  # Add the newest file to the list
            
            # Run cartoonify_image in the background

            # Extracting the filename without extension
            folder_dst_name = os.path.splitext(os.path.basename(newest_file))[0]
            folder_dst_path = os.path.join(cartoonified_images_path, folder_dst_name)
            os.makedirs(folder_dst_path, exist_ok=True)
            # print("\nCreated folder to store " + newest_file + " and cartoonified versions into " + folder_dst_name + "with path " + folder_dst_path)

            # Copying the file to the newly created folder
            shutil.copy(newest_file, folder_dst_path)
            # print("Copied " + newest_file + " to " + folder_dst_path)

            if current_threads < maximum_threads:
                print("Current image being cartoonified: " + str(current_image_being_cartoonified))
                parallel_cartoonify(newest_files[current_image_being_cartoonified], folder_dst_name, folder_dst_path)   
                current_image_being_cartoonified += 1

        if ammount_of_images == images_enhanced != current_image_being_cartoonified:
            if current_threads < maximum_threads and (current_image_being_cartoonified != ammount_of_images):
                parallel_cartoonify(newest_files[current_image_being_cartoonified], folder_dst_name, folder_dst_path)       
                current_image_being_cartoonified += 1


        if ammount_of_images == images_enhanced == current_image_being_cartoonified: 
            check_threads_done()
            print("\nProcessing complete! Total wait time was", wait_time, "seconds")
            break
            

        time.sleep(3) 

def parallel_cartoonify(newest_file, folder_dst_name, folder_dst_path):
    print("Beginning cartoonization for " + os.path.splitext(os.path.basename(newest_file))[0])
    wait_index = 0
    for edge_intensity_value in range(edge_intensity_min, edge_intensity_max + 1, edge_intensity_increment):
        inner_folder_name = f"EdgeIntensity_{edge_intensity_value}" + folder_dst_name
        inner_folder_path = os.path.join(folder_dst_path, inner_folder_name)
        os.makedirs(inner_folder_path, exist_ok=True)
        wait_index += 4
        threading.Thread(target=cartoonify_image, args=(newest_file, inner_folder_path, edge_intensity_value, wait_index)).start() # Check directory size every 3 seconds

def move_newest_image(source_folder, destination_folder):
    files = [os.path.join(source_folder, f) for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    newest_image = max(files, key=os.path.getmtime, default=None)
    shutil.move(newest_image, destination_folder)
    # print(f"Moved {newest_image} to {destination_folder}")
   
def check_threads_done():
    while threading.active_count() > 1:
        pass

def cartoonify_image(image, folder_dst_path, edge_intensity_value,variable_wait_time):
    download_directory = folder_dst_path
    website = cartoon_website

    driver = setup_driver(download_directory, website)
    wait = WebDriverWait(driver, 10)  # Initialize WebDriverWait object
    time.sleep(variable_wait_time)
    send_cartoonify(driver, edge_intensity_value, image, folder_dst_path)
    #print("Waiting for webpage to load...")
    time.sleep(5)
    if not assert_finished(wait, "Download processed image"):
        driver.quit()
        cartoonify_image(image, folder_dst_path, edge_intensity_value,variable_wait_time)
    time.sleep(5)
    rename_downloaded_file(edge_intensity_value, download_directory)
    # Close the browser after cartoonifying the image
    image_name = os.path.splitext(os.path.basename(image))
    print("Finished cartoonifying", image_name, "with Edge Intensity", edge_intensity_value)
    driver.quit() 

def setup_driver(download_directory, website):
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': download_directory}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(website)
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

def get_directory_size(directory):
    total = 0
    for path, dirs, files in os.walk(directory):
        for f in files:
            fp = os.path.join(path, f)
            total += os.path.getsize(fp)
    return total

def rename_downloaded_file(edge_intensity_value, folder_dst_path):
    try:
        # Find the newest downloaded file in the downloads folder
        files = [os.path.join(folder_dst_path, f) for f in os.listdir(folder_dst_path) if os.path.isfile(os.path.join(folder_dst_path, f))]
        latest_file = max(files, key=os.path.getmtime, default=None)
        
        if latest_file.lower().endswith(('.jpg', '.jpeg')):
            new_file_name = f"EdgeIntensity_{edge_intensity_value}_{os.path.basename(latest_file)}"
            new_file_path = os.path.join(folder_dst_path, new_file_name)
            os.rename(latest_file, new_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Retrying...")
        time.sleep(1)
        rename_downloaded_file(edge_intensity_value, folder_dst_path)

def assert_finished(wait, element):
    # Wait for the elements indicating the image processing is complete on the result page
    try:
        time.sleep(2)
        download_button = wait.until(EC.presence_of_element_located((By.XPATH, f'//a[b[text()="{element}"]]')))
    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
    download_button.click()
    return True

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

        #print("Sending " + image_file + " with Edge Intensity " + str(edge_intensity_value))
        # Submit the form or initiate processing (assuming a button click)
        submit_button = driver.find_element(By.XPATH, '//input[@type="submit"]')
        submit_button.click()

    except NoSuchElementException:
        print("Upload input element not found!")  # Print message if the element is not found
        # Handle the case when the element is not found or perform additional actions

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

def keep(filename, folder_path):
    for file in os.listdir(folder_path):
        if file != filename:
            os.remove(os.path.join(folder_path, file))
            # print("Removed " + file)
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
    # print("Moved all files to current directory")
    
def remove_empty_folders(directory):
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):
            if not os.listdir(folder_path):
                os.rmdir(folder_path)
    # print("Removed empty folders")


def validate_empty_directory(directory):
    if os.listdir(directory):
        print("Working directory " + directory + " is not empty. Would you like to empty it? (Y/N)")
        user_input = input().lower()
        if user_input == "y":
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print("Directory emptied")
        elif user_input == "n":
            print("Exiting...")
            subprocess.Popen(['explorer', directory])
            exit(0)
        else:
            print("Invalid input")
            validate_empty_directory(directory)


def main():
    validate_empty_directory(cartoonified_images_path)
    validate_empty_directory(enhancedImages_path)
    move_zip_to_directory()
    unzip_folder()
    if not validate_directory(potential_stickers_path):
        exit(1)
    run_application(quality_scaler_path)
    enter_parameters()
    ammount_of_images = len(os.listdir(potential_stickers_path)) 
    select_images(potential_stickers_path)
    check_progress(ammount_of_images)
    for folder in os.listdir(cartoonified_images_path):        
        folder_path = os.path.join(cartoonified_images_path, folder)
        move_to_current_directory(folder_path)
        remove_empty_folders(folder_path)
    subprocess.Popen(['start', audio_path], shell=True)    
    open_popup_windows("When each folder opens on screen,\n please type the edge intensity value you want to keep for that folder.\n" +
                        "If you want to keep the image with Edge Intensity with 20,\n simply type '20' on your keyboard and it will move onto the next folder" +
                         "\n.... Understood?")
    picture_picker(cartoonified_images_path)
    move_to_current_directory(cartoonified_images_path)
    remove_empty_folders(cartoonified_images_path)
    subprocess.Popen(f'explorer {cartoonified_images_path}')
    print("Finished!")
    
main()


