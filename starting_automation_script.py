import webbrowser
import zipfile
import shutil
import os
import subprocess
import time
import pyautogui
from PIL import Image
import time
import pygetwindow as gw


picture_extensions = (".jpg", ".jpeg", ".png", "avif")
downloads_path = r'C:\Users\harry\Downloads'  # Update with your Downloads directory path
potential_stickers_path = r'C:\Users\harry\Desktop\Stickers\Potential_Stickers'  # Update with the destination directory path
zip_filename = 'potential stickers.zip'
quality_scaler_path = r'C:\Users\harry\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam\QualityScaler.url'  # Update with the path to your Quality Scaler application

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
                    
def convert_images_to_png(directory):
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
    
def main():
    move_zip_to_directory()
    unzip_folder()
    old_images = convert_images_to_png(potential_stickers_path) 
    run_application(quality_scaler_path)
    enter_parameters()
    ammount_of_images = len(os.listdir(potential_stickers_path)) 
    size_of_directory = get_directory_size(potential_stickers_path)   
    select_images(potential_stickers_path)
    check_progress(ammount_of_images)    
    remove_images(old_images)
    print("Size of old directory:", size_of_directory/1000000, "MB")
    print("Size of new directory:", get_directory_size(potential_stickers_path)/1000000, "MB")
    subprocess.Popen(f'explorer {potential_stickers_path}')

main()
