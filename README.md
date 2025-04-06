# Image Importer

A Python script that organizes images by copying them to date-based folders using EXIF data.

## Features

- Copies images to a destination directory organized by date
- Creates folders with format YYYY-MM-DD (e.g., "2024-03-15")
- Uses EXIF data to determine the image date
- Falls back to file modification time if EXIF data is not available
- Supports JPG, JPEG, PNG, and GIF formats
- Accepts multiple source files and wildcards as command line arguments

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script with source files/patterns and destination directory as arguments:
```bash
python imageImporter.py <source_files...> <destination>
```

Examples:
```bash
# Process a single file
python imageImporter.py photo.jpg ./organized_photos

# Process multiple specific files
python imageImporter.py photo1.jpg photo2.png photo3.gif ./organized_photos

# Process all JPG files in current directory
python imageImporter.py *.jpg ./organized_photos

# Process multiple file types
python imageImporter.py *.jpg *.png *.gif ./organized_photos

# Process files from different locations
python imageImporter.py /path1/*.jpg /path2/*.png ./organized_photos
```

The script will:
- Process each specified file or pattern
- Extract the date from EXIF data or file modification time
- Create date-based folders (YYYY-MM-DD format)
- Copy images to their respective date folders

## Example

If you have an image taken on March 15, 2024, it will be copied to:
```
organized_photos/2024-03-15/image.jpg
```

## Testing

The project includes a comprehensive test suite. To run the tests:
```bash
python -m unittest test_imageImporter.py
```

The tests cover:
- Extracting dates from EXIF data
- Handling images without EXIF data
- Creating date-based folders
- Importing single and multiple files
- File pattern matching

## Help

To see the help message and usage instructions:
```bash
python imageImporter.py --help
```
