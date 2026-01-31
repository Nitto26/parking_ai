import cv2
import numpy as np

# --- CONFIG ---
MATRIX_FILE = 'matrix.npy'
CAMERA_IMAGE = 'camera_view.png'
MAP_IMAGE = 'top_down_view.png'
# --------------

def click_test(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # 1. Get the point you clicked on the Camera View
        print(f"Clicked Camera at: {x}, {y}")
        
        # 2. Load the Matrix
        h_matrix = param['matrix']
        map_img = param['map_img']
        map_display = map_img.copy() # Refresh map to clear old dots
        
        # 3. THE MATH (Transform Pixel -> Map)
        # We format the point as a vector [[x, y]]
        point_vector = np.array([[[x, y]]], dtype=np.float32)
        transformed_point = cv2.perspectiveTransform(point_vector, h_matrix)
        
        # Extract new coordinates
        map_x = int(transformed_point[0][0][0])
        map_y = int(transformed_point[0][0][1])
        print(f"Mapped to Digital Twin: {map_x}, {map_y}")

        # 4. VISUALIZE
        # Draw a Green Circle on Camera View (where you clicked)
        cv2.circle(param['cam_img'], (x, y), 5, (0, 255, 0), -1)
        
        # Draw a Red Circle on Map View (where it landed)
        cv2.circle(map_display, (map_x, map_y), 10, (0, 0, 255), -1)
        
        cv2.imshow("Digital Twin (Map)", map_display)
        cv2.imshow("Camera Source", param['cam_img'])

def main():
    try:
        h_matrix = np.load(MATRIX_FILE)
    except FileNotFoundError:
        print("Error: matrix.npy not found! Run calibration.py first.")
        return

    cam_img = cv2.imread(CAMERA_IMAGE)
    map_img = cv2.imread(MAP_IMAGE)

    cv2.namedWindow("Camera Source")
    cv2.namedWindow("Digital Twin (Map)")

    # Set up the mouse listener
    params = {'matrix': h_matrix, 'cam_img': cam_img, 'map_img': map_img}
    cv2.setMouseCallback("Camera Source", click_test, params)

    print("TEST STARTED: Click anywhere on the 'Camera Source' window.")
    print("Watch the 'Digital Twin' window to see the corresponding point appear.")
    print("Press 'q' to exit.")

    cv2.imshow("Camera Source", cam_img)
    cv2.imshow("Digital Twin (Map)", map_img)

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()