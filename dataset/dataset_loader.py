from datasets import load_dataset
from PIL import Image
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.constants import DATASET_NAME, SPLIT_NAME, IMAGES_DIR, NUM_SAMPLES

"""
Dataset loading exceptions
"""
class DatasetLoadingError(Exception):
    pass

class ImageProcessingError(Exception):
    pass



"""
Load images from dataset. If the next object is not an image, skip it and move to the next one.
"""
def load_first_images():

    try:
        dataset = load_dataset(DATASET_NAME, split=SPLIT_NAME)
    except Exception as e:
        error_msg = f"Failed to load dataset {DATASET_NAME}: {str(e)}"
        raise DatasetLoadingError(error_msg) from e
    
    images = []
    skipped_samples = 0
    missing_image_field = 0
    
    try:
        for i, sample in enumerate(dataset):
            if i >= NUM_SAMPLES:
                break

            if 'image' in sample:
                image = sample['image']
                if isinstance(image, Image.Image):
                    images.append(image)
                else:
                    skipped_samples += 1
                    error_msg = f"Sample #{i+1} contains invalid image data (type: {type(image)})"
            else:
                missing_image_field += 1
                error_msg = f"Sample #{i+1} missing 'image' field. Available fields: {list(sample.keys())}"
    
    except Exception as e:
        error_msg = f"Error during image processing: {str(e)}"
        raise ImageProcessingError(error_msg) from e
    
    if len(images) == 0:
        error_msg = "No valid images were loaded from the dataset"
        raise ImageProcessingError(error_msg)
    
    return images


"""
Save images to output directory.
"""
def save_images(images, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        error_msg = f"Failed to create output directory {output_dir}: {str(e)}"
        raise OSError(error_msg) from e
    
    saved_count = 0
    save_errors = 0
    
    for i, image in enumerate(images):           
        try:
            filename = f"mobile_ui_{i+1:03d}.png"
            filepath = os.path.join(output_dir, filename)
            image.save(filepath)
            saved_count += 1
        except Exception as e:
            save_errors += 1
            error_msg = f"Failed to save image #{i+1} to {filepath}: {str(e)}"
    
    if saved_count == 0:
        error_msg = "No images were successfully saved"
        raise ImageProcessingError(error_msg)
    
    return saved_count, save_errors

"""
Combine loading and saving images.
"""
def load_and_save_first_images():
    images = load_first_images()
    saved_count, save_errors = save_images(images, IMAGES_DIR)
    
    return images, saved_count, save_errors


def main():
    try:
        images, saved_count, save_errors = load_and_save_first_images()
        
        print(f"Successfully loaded {len(images)} images")
        print(f"Successfully saved {saved_count} images to {IMAGES_DIR}")
        if save_errors > 0:
            print(f"Had {save_errors} save errors")
        
        return True
        
    except DatasetLoadingError as e:
        print(f"Dataset loading failed: {e}")
        return False
    except ImageProcessingError as e:
        print(f"Image processing failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("Program completed successfully!")
    else:
        print("Program failed!")