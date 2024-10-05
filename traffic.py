import cv2
import numpy as np
from ultralytics import YOLO
import sqlite3
from datetime import datetime
import streamlit as st
import tempfile
import os
import subprocess

# Load the best fine-tuned YOLOv8 model
best_model = YOLO(r"C:\Users\joshu\trafficapp\runs\detect\train\weights\best.pt")

# Database connection setup
conn = sqlite3.connect('traffic_analysis.db')
cursor = conn.cursor()

# Create tables
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS traffic_data (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      video_name TEXT NOT NULL,
                      timestamp TEXT NOT NULL,
                      vehicles_in_left_lane INTEGER NOT NULL,
                      vehicles_in_right_lane INTEGER NOT NULL,
                      traffic_intensity_left TEXT NOT NULL,
                      traffic_intensity_right TEXT NOT NULL,
                      latitude REAL,
                      longitude REAL,
                      street_name TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS traffic_summary (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      video_name TEXT NOT NULL,
                      date TEXT NOT NULL,
                      average_vehicles_left_lane REAL NOT NULL,
                      average_vehicles_right_lane REAL NOT NULL,
                      peak_intensity_left TEXT NOT NULL,
                      peak_intensity_right TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS traffic_incidents (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      video_name TEXT NOT NULL,
                      timestamp TEXT NOT NULL,
                      incident_type TEXT NOT NULL,
                      description TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS video_processing_status (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      video_name TEXT NOT NULL,
                      processed BOOLEAN NOT NULL)''')

    conn.commit()

# Create indices for better query performance
def create_indices():
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON traffic_data (timestamp);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicles_in_left_lane ON traffic_data (vehicles_in_left_lane);')
    conn.commit()

create_tables()
create_indices()

# Traffic analysis configuration
heavy_traffic_threshold = 10
vertices1 = np.array([(465, 350), (609, 350), (510, 630), (2, 630)], dtype=np.int32)
vertices2 = np.array([(678, 350), (815, 350), (1203, 630), (743, 630)], dtype=np.int32)
lane_threshold = 609

# Function to check if the video has already been processed
def is_video_processed(video_name):
    cursor.execute("SELECT processed FROM video_processing_status WHERE video_name=?", (video_name,))
    result = cursor.fetchone()
    return result is not None and result[0]

# Function to mark the video as processed
def mark_video_as_processed(video_name):
    cursor.execute("INSERT INTO video_processing_status (video_name, processed) VALUES (?, ?)", (video_name, True))
    conn.commit()

# Function to insert traffic data into the database
def insert_traffic_data(video_name, timestamp, vehicles_in_left_lane, vehicles_in_right_lane, traffic_intensity_left, traffic_intensity_right, latitude, longitude, street_name):
    cursor.execute("INSERT INTO traffic_data (video_name, timestamp, vehicles_in_left_lane, vehicles_in_right_lane, traffic_intensity_left, traffic_intensity_right, latitude, longitude, street_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   (video_name, timestamp, vehicles_in_left_lane, vehicles_in_right_lane, traffic_intensity_left, traffic_intensity_right, latitude, longitude, street_name))
    conn.commit()

# Function to insert traffic incidents into the database
def insert_traffic_incident(video_name, timestamp, incident_type, description):
    cursor.execute("INSERT INTO traffic_incidents (video_name, timestamp, incident_type, description) VALUES (?, ?, ?, ?)", 
                   (video_name, timestamp, incident_type, description))
    conn.commit()

# Function to convert AVI to MP4 using ffmpeg
def convert_to_mp4(input_path):
    output_path = input_path.rsplit('.', 1)[0] + '.mp4'  # Change the extension to mp4
    command = ['ffmpeg', '-i', input_path, '-vcodec', 'h264', '-acodec', 'aac', output_path]
    subprocess.run(command, check=True)
    return output_path

# Function to process video and return processed video path
def process_video(video_path):
    # Open the video
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Write the output as AVI

    # Create a temporary file for the output video
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.avi').name
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    video_name = os.path.basename(video_path)

    # Check if the video has already been processed
    if is_video_processed(video_name):
        return None

    # Process the video frame by frame
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            detection_frame = frame.copy()
            detection_frame[:325, :] = 0  
            detection_frame[635:, :] = 0  

            results = best_model.predict(detection_frame, imgsz=640, conf=0.4)
            processed_frame = results[0].plot(line_width=1)
            processed_frame[:325, :] = frame[:325, :].copy()
            processed_frame[635:, :] = frame[635:, :].copy()

            # Draw lanes
            cv2.polylines(processed_frame, [vertices1], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.polylines(processed_frame, [vertices2], isClosed=True, color=(255, 0, 0), thickness=2)

            bounding_boxes = results[0].boxes
            vehicles_in_left_lane = 0
            vehicles_in_right_lane = 0
            for box in bounding_boxes.xyxy:
                if box[0] < lane_threshold:
                    vehicles_in_left_lane += 1
                else:
                    vehicles_in_right_lane += 1

            traffic_intensity_left = "Heavy" if vehicles_in_left_lane > heavy_traffic_threshold else "Smooth"
            traffic_intensity_right = "Heavy" if vehicles_in_right_lane > heavy_traffic_threshold else "Smooth"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            latitude, longitude = 12.9716, 77.5946  # Example coordinates
            street_name = "MG Road"
            insert_traffic_data(video_name, timestamp, vehicles_in_left_lane, vehicles_in_right_lane, traffic_intensity_left, traffic_intensity_right, latitude, longitude, street_name)

            # Detect traffic incident
            if vehicles_in_left_lane > 20:  # Arbitrary condition for incident detection
                insert_traffic_incident(video_name, timestamp, "Congestion", "Heavy congestion detected in the left lane.")

            # Write the processed frame to the output video
            out.write(processed_frame)
        else:
            break

    cap.release()
    out.release()

    # Convert the processed video to MP4 format
    mp4_output_path = convert_to_mp4(output_path)

    # Mark the video as processed
    mark_video_as_processed(video_name)

    return mp4_output_path

# Streamlit app interface
import streamlit as st
import tempfile

st.set_page_config(page_title="Traffic Analysis Dashboard", page_icon="🚦", layout="wide")

# Enhanced Header Design with Animation
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    /* Set background for the main container */
    .stApp {
        background: linear-gradient(to right, #2C3E50, #34495E); 
        min-height: 100vh; /* Ensure it covers the full height */
        transition: background-color 0.5s;
    }
    
    body {
        font-family: 'Roboto', sans-serif;
    }
    
    .main-header {
        font-size: 36px;
        text-align: center;
        color: #FDFEFE; /* Off-white color for text */
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        animation: slideIn 0.5s ease-in-out;
    }
    
    .section-title {
        font-size: 28px;
        font-weight: bold;
        margin-top: 30px;
        color: black; /* Vibrant orange */
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Subtle shadow for depth */
        animation: fadeIn 1s ease-in-out;
    }
    
    .uploaded-video {
        display: flex;
        justify-content: center;
        margin: 20px 0;
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    }
    
    .uploaded-video:hover {
        transform: scale(1.05); /* Slight scale on hover */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3); /* Elevation effect */
    }
    
    .video-container {
        text-align: center;
        border-radius: 10px;
        overflow: hidden;
        border: 2px solid #FDFEFE; /* Off-white border for video */
        background-color: rgba(255, 255, 255, 0.8); /* Semi-transparent background */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .warning {
        color: #E74C3C; /* Bright red for warnings */
        font-weight: bold;
        animation: shake 0.5s ease-in-out;
    }
    
    .success {
        color: #27AE60; /* Green for success messages */
        font-weight: bold;
        animation: bounce 0.5s ease-in-out;
    }
    
    @keyframes slideIn {
        from {
            transform: translateY(-20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        50% { transform: translateX(5px); }
        75% { transform: translateX(-5px); }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Traffic Analysis Dashboard</div>', unsafe_allow_html=True)

# File upload section
st.markdown('<div class="section-title">Upload Video for Analysis</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a video...", type=["mp4", "avi"])

if uploaded_file is not None:
    # Save uploaded video to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        temp_video.write(uploaded_file.read())
        temp_video_path = temp_video.name

    # Video container for uploaded video
    st.markdown('<div class="uploaded-video">', unsafe_allow_html=True)
    st.video(temp_video_path)
    st.markdown('</div>', unsafe_allow_html=True)

    # Process the video and display results
    st.markdown('<div class="section-title">Processing Results</div>', unsafe_allow_html=True)
    processed_video_path = process_video(temp_video_path)

    if processed_video_path:
        st.markdown('<div class="success">Processed video is available for download and viewing:</div>', unsafe_allow_html=True)
        st.video(processed_video_path)
    else:
        st.markdown('<div class="warning">This video has already been processed.</div>', unsafe_allow_html=True)

else:
    st.write("Please upload a video file to proceed.")
