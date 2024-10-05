# Traffic Analysis Dashboard

🚦 **Traffic Analysis Dashboard** is a Streamlit application designed to analyze traffic video data. Users can upload traffic videos, and the application processes these videos to extract relevant information for analysis.

## About the Project
The Traffic Analysis Dashboard is a comprehensive web application developed using Streamlit, designed to assist in traffic management and analysis. This project utilizes video processing to analyze traffic patterns, identify congestion points, and gather data for improved traffic flow management.

Key Features
Traffic Video Analysis: Users can upload traffic videos, which the application processes to extract valuable insights into vehicle movement, density, and flow rates. This analysis helps in understanding traffic behaviors during different times of the day.

Database Management: The application leverages SQLite for efficient database management, enabling the storage and retrieval of processed data, traffic patterns, and historical analysis results. This functionality allows for easy querying and reporting, facilitating informed decision-making.

Traffic Management Insights: By analyzing the collected data, the dashboard provides insights into traffic congestion, accident-prone areas, and peak traffic times. These insights can help local authorities and urban planners devise strategies to optimize traffic management, such as implementing traffic signal adjustments, road expansions, or improved public transport options.

## Features

- **Video Upload**: Users can upload `.mp4` or `.avi` video files for analysis.
- **Video Processing**: The uploaded video is processed to extract and analyze traffic patterns.
- **Results Display**: After processing, users can view the processed video directly in the dashboard.

## Technologies Used

- [Streamlit](https://streamlit.io/) - Framework for building interactive web applications in Python.
- [OpenCV](https://opencv.org/) - Library for computer vision and video processing.
- [NumPy](https://numpy.org/) - Library for numerical operations.
- [Pandas](https://pandas.pydata.org/) - Data manipulation and analysis library.

## Installation

1. Clone the repository:
2.Install required packages via requirements.txt
3. Run the app : streamlit run app.py

Note: Conda Environment file and runs folder could not be uploaded due to large size.

<img width="1280" alt="results2traffic" src="https://github.com/user-attachments/assets/565f9a84-8bc6-4bc9-8e52-727fd1a8c83b">
<img width="1271" alt="results1traffic" src="https://github.com/user-attachments/assets/c2535b3a-9daa-4bf1-9f80-f9c17b6ac608">
