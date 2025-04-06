# -*- coding: utf-8 -*-

import os
import shutil
import argparse
import glob
from datetime import datetime
from PIL import Image
import piexif
from pathlib import Path

class ImageImporter:
    def __init__(self, source_files, destination_dir):
        self.source_files = source_files
        self.destination_dir = Path(destination_dir)
        
    def get_image_date(self, image_path):
        """Extract date from image EXIF data or fallback to file modification time."""
        try:
            exif_dict = piexif.load(str(image_path))
            if "0th" in exif_dict and piexif.ImageIFD.DateTime in exif_dict["0th"]:
                date_str = exif_dict["0th"][piexif.ImageIFD.DateTime].decode('utf-8')
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except Exception:
            pass
        
        # Fallback to file modification time
        return datetime.fromtimestamp(os.path.getmtime(image_path))
    
    def create_date_folder(self, date):
        """Create a folder with format yyyy-mm-dd."""
        folder_path = self.destination_dir / date.strftime('%Y-%m-%d')
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path
    
    def import_images(self):
        """Import all specified images to date-based folders."""
        # Create destination directory if it doesn't exist
        self.destination_dir.mkdir(parents=True, exist_ok=True)
        
        # Process all specified files
        for source_pattern in self.source_files:
            # Expand wildcards if present
            for file_path in glob.glob(source_pattern):
                file_path = Path(file_path)
                if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    try:
                        # Get image date
                        image_date = self.get_image_date(file_path)
                        
                        # Create destination folder
                        dest_folder = self.create_date_folder(image_date)
                        
                        # Copy file to destination
                        dest_path = dest_folder / file_path.name
                        shutil.copy2(file_path, dest_path)
                        print(f"Copied {file_path.name} to {dest_path}")
                        
                    except Exception as e:
                        print(f"Error processing {file_path.name}: {str(e)}")

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Import and organize images by date using EXIF data.')
    parser.add_argument('sources', nargs='+', help='Source files or patterns (e.g., *.jpg) to import')
    parser.add_argument('destination', help='Destination directory where images will be organized')
    
    args = parser.parse_args()
    
    # Create and run the importer
    importer = ImageImporter(args.sources, args.destination)
    importer.import_images()

if __name__ == "__main__":
    main()
