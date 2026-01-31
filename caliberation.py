import cv2
import numpy as np
import json

# --- CONFIGURATION ---
SOURCE_IMAGE_PATH = 'camera_view.png'
DEST_IMAGE_PATH = 'top_down_view.png'
OUTPUT_MATRIX_FILE = 'matrix.npy'
# ---------------------

# Global variables to store clicks
src_points = []
dst_points = []

def select_points(event, x, y, flags, param):
    """
    Mouse callback function.
    Appends coordinates of the click to the specific list (src or dst).
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        points_list = param['points']
        image = param['image']
        window_name = param['window_name']
        
        # Add point
        points_list.append((x, y))
        
        # visual feedback: Draw a red circle and the number
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(image, str(len(points_list)), (x + 10, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow(window_name, image)

def get_points(image_path, point_store, window_name):
    """
    Opens an image and waits for 4 clicks.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image {image_path}")
        exit()
        
    clone = img.copy()
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, select_points, 
                         {'points': point_store, 'image': clone, 'window_name': window_name})

    print(f"\n--- {window_name} ---")
    print(f"Please click 4 points on the {window_name}.")
    print("Order matters! (e.g., Top-Left -> Top-Right -> Bottom-Right -> Bottom-Left)")
    print("Press any key when done.")

    while True:
        cv2.imshow(window_name, clone)
        key = cv2.waitKey(1) & 0xFF
        # Break if 4 points are selected or user presses a key
        if len(point_store) == 4:
            print(f"4 points selected for {window_name}. Press any key to confirm.")
            cv2.waitKey(0) # Wait for confirmation
            break

    cv2.destroyWindow(window_name)
    return img  # Return the original image for later use

def main():
    # 1. Get points from the Angled Camera View
    print("STEP 1: Select Points on CAMERA VIEW")
    src_img = get_points(SOURCE_IMAGE_PATH, src_points, "Camera View (Source)")

    # 2. Get points from the Top-Down Map
    print("\nSTEP 2: Select corresponding Points on TOP-DOWN MAP")
    dst_img = get_points(DEST_IMAGE_PATH, dst_points, "Top-Down View (Destination)")

    # 3. Calculate Homography
    if len(src_points) != 4 or len(dst_points) != 4:
        print("Error: You must select exactly 4 points on both images.")
        return

    pts_src = np.array(src_points, dtype=float)
    pts_dst = np.array(dst_points, dtype=float)

    # The Magic Function: Calculates the Matrix
    h_matrix, status = cv2.findHomography(pts_src, pts_dst)

    print("\nCalculated Homography Matrix:")
    print(h_matrix)

    # 4. Save the Matrix
    np.save(OUTPUT_MATRIX_FILE, h_matrix)
    print(f"\nMatrix saved to '{OUTPUT_MATRIX_FILE}'")

    # 5. VERIFICATION (Optional but Recommended)
    # Let's warp the camera image to see if it looks like the map!
    height, width, channels = dst_img.shape
    warped_image = cv2.warpPerspective(src_img, h_matrix, (width, height))

    # Show result side-by-side
    result = np.concatenate((dst_img, warped_image), axis=1)
    cv2.imshow("Comparison: True Map vs. Warped Camera", result)
    print("Showing verification. The right image is the Camera View warped to look like a map.")
    print("Press any key to exit.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()