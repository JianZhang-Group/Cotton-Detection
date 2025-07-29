# Cotton-Detection

## Overview
This project is a server application that utilizes a camera to recognize objects in real-time and sends their coordinates to a client. It is designed to be modular, with separate components for camera handling, object recognition, and network communication.

## Setup Instructions
1. **Clone the repository**:
   ```
   git clone https://github.com/JianZhang-Group/Cotton-Detection
   cd Cotton-Detection
   ```

2. **Install dependencies**:
   Ensure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

   Then, you can follow the instruction on [pyorbbecsdk](https://orbbec.github.io/pyorbbecsdk/index.html) to setup the environment.

3. **Configure the application**:
   Edit the `config.yaml` file to set your camera parameters.

## Usage
To run the application, execute the following command:
```
python main.py
```

The application will initialize the server.

## Packaged
Run the following command:
```
pyinstaller main.py --contents-directory . --add-data "models;models" --add-data "config.yaml;." -n Cotton-Detection
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.