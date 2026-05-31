import os

def rename_files_in_folder(folder_path, general_name, start_index=1):
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    # Get the list of files in the folder, excluding hidden files
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith('.')]

    # Sort files to ensure consistent renaming order
    files.sort()

    # Rename files
    for index, file_name in enumerate(files, start=start_index):
        # Get the file extension
        file_extension = os.path.splitext(file_name)[1]

        # Create the new file name
        new_name = f"{general_name}-{index}{file_extension}"

        # Full paths for renaming
        old_path = os.path.join(folder_path, file_name)
        new_path = os.path.join(folder_path, new_name)

        # Rename the file
        os.rename(old_path, new_path)

    print(f"Files in {folder_path} have been renamed to {general_name}-{start_index}, {general_name}-{start_index+1}, ...")

# Example usage
folder_path = '/Volumes/ME/MEO/Blogging/miawanders/articles_miawanders/00-china-fenghuang gucheng/edit' # Replace with the path to your folder
general_name = "how-to-visit-fenghuang-ancient-town" # Replace with your general name
start_index = 1                  # Replace with your desired starting index
rename_files_in_folder(folder_path, general_name, start_index)
