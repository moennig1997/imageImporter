import unittest
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from PIL import Image
import piexif
from imageImporter import ImageImporter
from io import StringIO
import sys

class TestImageImporter(unittest.TestCase):
    def setUp(self):
        """Create temporary directories and test images before each test."""
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.test_dir) / "source"
        self.dest_dir = Path(self.test_dir) / "destination"
        self.source_dir.mkdir()
        
        # Create test images with known dates
        self.create_test_image("test1.jpg", "2024:03:15 10:30:00")
        self.create_test_image("test2.jpg", "2024:03:16 15:45:00")
        self.create_test_image("test3.CR2")  # CR2 file without EXIF data
        self.create_test_image("test_no_exif.jpg")  # Image without EXIF data
        
    def tearDown(self):
        """Clean up temporary files after each test."""
        shutil.rmtree(self.test_dir)
        
    def create_test_image(self, filename, date_time=None):
        """Create a test image with optional EXIF data."""
        image_path = self.source_dir / filename
        # Create a small test image
        image = Image.new('RGB', (100, 100), color='red')
        
        if date_time:
            # Create EXIF data with the specified date
            exif_dict = {"0th": {}, "Exif": {}}
            exif_dict["0th"][piexif.ImageIFD.DateTime] = date_time.encode('utf-8')
            exif_bytes = piexif.dump(exif_dict)
            image.save(image_path, exif=exif_bytes)
        else:
            image.save(image_path)
            
    def test_get_image_date_with_exif(self):
        """Test extracting date from image with EXIF data."""
        importer = ImageImporter([str(self.source_dir / "test1.jpg")], str(self.dest_dir))
        date = importer.get_image_date(self.source_dir / "test1.jpg")
        expected_date = datetime(2024, 3, 15, 10, 30)
        self.assertEqual(date, expected_date)
        
    def test_get_image_date_without_exif(self):
        """Test fallback to file modification time when no EXIF data."""
        test_file = self.source_dir / "test_no_exif.jpg"
        importer = ImageImporter([str(test_file)], str(self.dest_dir))
        date = importer.get_image_date(test_file)
        self.assertIsInstance(date, datetime)
        
    def test_get_image_date_cr2(self):
        """Test handling CR2 files."""
        test_file = self.source_dir / "test3.CR2"
        importer = ImageImporter([str(test_file)], str(self.dest_dir))
        date = importer.get_image_date(test_file)
        self.assertIsInstance(date, datetime)
        
    def test_create_date_folder(self):
        """Test creation of date-based folder."""
        importer = ImageImporter([str(self.source_dir)], str(self.dest_dir))
        test_date = datetime(2024, 3, 15)
        
        # Capture stdout to check for directory creation message
        captured_output = StringIO()
        sys.stdout = captured_output
        
        folder = importer.create_date_folder(test_date)
        expected_path = self.dest_dir / "2024-03-15"
        self.assertEqual(folder, expected_path)
        self.assertTrue(folder.exists())
        self.assertIn(f"Created directory: {expected_path}", captured_output.getvalue())
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
    def test_import_images(self):
        """Test importing multiple images."""
        importer = ImageImporter([str(self.source_dir / "*.jpg"), str(self.source_dir / "*.CR2")], str(self.dest_dir))
        
        # Capture stdout to check for messages
        captured_output = StringIO()
        sys.stdout = captured_output
        
        importer.import_images()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Check if files were copied to correct directories
        self.assertTrue((self.dest_dir / "2024-03-15" / "test1.jpg").exists())
        self.assertTrue((self.dest_dir / "2024-03-16" / "test2.jpg").exists())
        self.assertTrue(any(Path(self.dest_dir).glob("*/test3.CR2")))  # CR2 file should be in some date folder
        self.assertTrue(any(Path(self.dest_dir).glob("*/test_no_exif.jpg")))
        
        # Check for directory creation messages
        output = captured_output.getvalue()
        self.assertIn(f"Created destination directory: {self.dest_dir}", output)
        self.assertIn(f"Created directory: {self.dest_dir}/2024-03-15", output)
        self.assertIn(f"Created directory: {self.dest_dir}/2024-03-16", output)
        
    def test_import_specific_file(self):
        """Test importing a specific file."""
        importer = ImageImporter([str(self.source_dir / "test1.jpg")], str(self.dest_dir))
        importer.import_images()
        
        self.assertTrue((self.dest_dir / "2024-03-15" / "test1.jpg").exists())
        self.assertFalse((self.dest_dir / "2024-03-16" / "test2.jpg").exists())
        
    def test_skip_existing_file(self):
        """Test skipping files that already exist in the destination."""
        # First import
        importer = ImageImporter([str(self.source_dir / "test1.jpg")], str(self.dest_dir))
        importer.import_images()
        
        # Capture stdout for the second import
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Second import (should skip the file)
        importer.import_images()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Check that the file was not overwritten
        self.assertTrue((self.dest_dir / "2024-03-15" / "test1.jpg").exists())
        
        # Check for skip message
        output = captured_output.getvalue()
        self.assertIn(f"Skipped test1.jpg: File already exists in {self.dest_dir}/2024-03-15", output)

if __name__ == '__main__':
    unittest.main() 