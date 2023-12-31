import cv2
from ultralytics import YOLO
from sort  import Sort
import numpy as np

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')

# Open the video file
video_path = "los_angeles.mp4"
cap = cv2.VideoCapture(video_path)

# Initialize the SORT tracker
sort_tracker = Sort(max_age=5, min_hits=5, iou_threshold=0.2)


# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 inference on the frame
        result = model(frame)

        boxes = result[0].boxes.cpu().numpy()                                  # get boxes on cpu in numpy
        detections = []

        for box in boxes:
            if result[0].names[int(box.cls[0])] == 'car':                   
                (x1,y1,x2,y2) = box.xyxy[0].astype(int)                     
                score = box.conf[0].astype(float)                             
                detections.append([x1,y1,x2,y2,score])
        
        detections = np.array(detections)
 
        # Update the SORT tracker with detections
        tracked_objects = sort_tracker.update(detections)

        for d in tracked_objects:
            object_id, x1, y1, x2, y2 = int(d[4]), int(d[0]), int(d[1]), int(d[2]), int(d[3])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'ID: {object_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                 
        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()



