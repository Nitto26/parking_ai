import cv2
import uvicorn
from fastapi import FastAPI
from threading import Thread
import numpy as np

# --- CONFIGURATION ---
IMAGE_PATH = 'camera_view.png'  # The angled CCTV screenshot
HOST = "0.0.0.0"
PORT = 5000                     # The port backend_brain checks
# ---------------------

app = FastAPI()

# Global State for Virtual Cars
# We store them as a dict: {id: [x, y]}
virtual_cars = {}
active_car_id = 1  # Which car are we driving with arrow keys?

@app.get("/detections")
def get_detections():
    """
    Returns strictly the JSON format expected by the backend.
    Format: [{"x": 200, "y": 450, "type": "car"}, ...]
    """
    output_list = []
    
    # Loop through all virtual cars on screen
    for car_id, coords in virtual_cars.items():
        output_list.append({
            "x": int(coords[0]),  # Force integer
            "y": int(coords[1]),  # Force integer
            "type": "car"         # Default type
        })
    
    # DEBUG PRINT: Uncomment this to see exactly what is being sent in the terminal
    # print(f"Sending: {output_list}")
    
    return output_list

def mouse_callback(event, x, y, flags, param):
    global active_car_id
    
    # Left Click = Drive Car 1
    if event == cv2.EVENT_LBUTTONDOWN:
        virtual_cars[1] = [x, y]
        active_car_id = 1
        
    # Right Click = Drive Car 2
    elif event == cv2.EVENT_RBUTTONDOWN:
        virtual_cars[2] = [x, y]
        active_car_id = 2

def run_gui():
    """
    OpenCV GUI Loop to handle mouse/keyboard inputs
    """
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print(f"Error: Could not load {IMAGE_PATH}")
        return

    cv2.namedWindow("Edge Simulator")
    cv2.setMouseCallback("Edge Simulator", mouse_callback)

    print("--- SIMULATOR RUNNING ---")
    print(f"API Active at: http://localhost:{PORT}/detections")
    print("CONTROLS:")
    print("  [Left Click]  -> Move Car 1 (Blue)")
    print("  [Right Click] -> Move Car 2 (Red)")
    print("  [Arrow Keys]  -> Fine-tune position of active car")
    print("  [Spacebar]    -> Clear all cars")
    print("  [q]           -> Quit")
    
    while True:
        display_img = img.copy()
        
        # Draw all virtual cars
        for car_id, coords in virtual_cars.items():
            cx, cy = coords
            
            # Color: Blue for Car 1, Red for Car 2
            color = (255, 0, 0) if car_id == 1 else (0, 0, 255)
            
            # Draw the 'Footprint' dot (The point being sent to API)
            cv2.circle(display_img, (cx, cy), 6, color, -1)
            
            # Draw a fake bounding box (for realism)
            cv2.rectangle(display_img, (cx - 20, cy - 40), (cx + 20, cy), color, 2)
            
            # Label
            cv2.putText(display_img, f"Car {car_id}", (cx-20, cy-45), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.imshow("Edge Simulator", display_img)
        
        # Keyboard Controls
        key = cv2.waitKey(20) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord(' '): # Spacebar to clear
            virtual_cars.clear()
        
        # Arrow Keys logic (moves active car)
        if active_car_id in virtual_cars:
            x, y = virtual_cars[active_car_id]
            if key == 82: y -= 2  # Up (Keycodes vary by OS, usually 82/84/81/83)
            elif key == 84: y += 2  # Down
            elif key == 81: x -= 2  # Left
            elif key == 83: x += 2  # Right
            virtual_cars[active_car_id] = [x, y]

    cv2.destroyAllWindows()

# Run FastAPI in a separate thread so it doesn't block the GUI
if __name__ == "__main__":
    server_thread = Thread(target=uvicorn.run, args=(app,), kwargs={"host": HOST, "port": PORT, "log_level": "error"}, daemon=True)
    server_thread.start()
    
    # Run GUI in main thread
    run_gui()