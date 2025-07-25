# Camera Object Recognition Client

## Overview
This project is a client application that utilizes a camera to recognize objects in real-time and sends their coordinates to a server. It is designed to be modular, with separate components for camera handling, object recognition, and network communication.

## Project Structure
```
camera-object-client
├── src
│   ├── main.py                # Entry point of the application
│   ├── camera
│   │   ├── __init__.py        # Camera module initialization
│   │   └── capture.py         # Handles camera initialization and frame capturing
│   ├── recognition
│   │   ├── __init__.py        # Recognition module initialization
│   │   └── detector.py        # Processes frames and detects objects
│   ├── network
│   │   ├── __init__.py        # Network module initialization
│   │   └── client.py          # Manages communication with the server
│   └── utils
│       ├── __init__.py        # Utility module initialization
│       └── helpers.py         # Contains utility functions
├── requirements.txt            # Lists project dependencies
├── README.md                   # Project documentation
└── config.yaml                 # Configuration settings
```

## Setup Instructions
1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd camera-object-client
   ```

2. **Install dependencies**:
   Ensure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Configure the application**:
   Edit the `config.yaml` file to set your camera parameters and server address.

## Usage
To run the application, execute the following command:
```
python src/main.py
```

The application will initialize the camera, start capturing frames, detect objects, and send their coordinates to the specified server.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.