import cv2
import os

# Directory to save captured images
save_dir = "captures"
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open webcam")
    exit()

print("Press 'c' to capture an image, 'q' to quit.")
count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Webcam Feed - Press 'c' to capture", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        filename = os.path.join(save_dir, f"img_{count:03d}.png")
        cv2.imwrite(filename, frame)
        print(f"Captured {filename}")
        count += 1
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
