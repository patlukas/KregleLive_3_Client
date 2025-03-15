![GitHub release (latest by date)](https://img.shields.io/github/v/release/patlukas/KregleLive_3_Client?label=Latest%20Release)
![GitHub file count](https://img.shields.io/github/directory-file-count/patlukas/KregleLive_3_Client)
![GitHub issues](https://img.shields.io/github/issues/patlukas/KregleLive_3_Client)

# KregleLive_3_Client

KregleLive_3_Client is part of a bigger project. Together with [KregleLive_3_Server](https://github.com/patlukas/KregleLive_3_Server), it creates a system for generating live score tables. This application was tested and works with Python 3.13. The requirements are listed in `requirements.txt`.

KregleLive_3_Client receives data from KregleLive_3_Server over TCP. KregleLive_3_Server gets this data from bowling lanes.

## Features
- Receives live data from KregleLive_3_Server.
- Generates score tables for live events.
- Easy to configure and use.

## Requirements
- Windows
- Python 3.13
- Libraries listed in `requirements.txt`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/patlukas/KregleLive_3_Client
   ```
2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
1. Make sure KregleLive_3_Server is running and configured.
2. Run the KregleLive_3_Client:
   ```bash
   python main.py
   ```

## Building the Application
You can build the application yourself using `pyinstaller`:
```bash
pyinstaller pyinstaller.spec
```
Or you can download the pre-built `.exe` file from the [Releases](https://github.com/patlukas/KregleLive_3_Client/releases) section.

## Configuration
The project comes with a pre-prepared configuration. You don’t need to change anything to start using it.

## Directory with Logs
The log directory is located at: `%PROGRAMDATA%\KL3_C\logs\`

## 📌 Version History

| Version          | Release Date      | Commits | Changes                                      |
|------------------|-------------------|---------|----------------------------------------------|
| **v1.1.4.0**     | 🚧 In Development | 77+     |                                              |
| **v1.1.3.3**     | 2025-02-23        | 69      | Add new table                                |
| **v1.1.3.2**     | 2025-02-23        | 68      | Fix small bug                                |
| **v1.1.3.1**     | 2025-02-15        | 67      | Add new table                                |
| **v1.1.3.0**     | 2025-02-14        | 65      | Increasing the functionality of classic mode |
| **v1.1.2.1**     | 2025-02-07        | 59      | 🐍Added support for Python 13                |
| **v1.1.2.0**     | 2025-02-07        | 56      | Added support for individual competitions    |
| **v1.1.1.1**     | 2025-02-06        | 46      | Add README.md                                |
| **v1.1.1.0**     | 2025-02-05        | 44      | More tables to choose                        |
| **v1.1.0.0**     | 2025-02-04        | 40      | Add splashscreen                             |
| **v1.0.3**       | 2024-11-22        | 30      | Fix critical bug                             |
| **v1.0.1**       | 2024-11-02        | 27      | 🎉 Initial stable release                    |
| **First commit** | 2024-08-13        | 1       |                                              |

## Screenshots
Here are some screenshots of the application:

### Application Interface
<img src="screenshots/SS_1.png" width="500">

### Example Generated Tables
<img src="screenshots/SS_2.png" width="500">

### System Diagram (this project is "Application 2"0)
<img src="screenshots/SS_3.png" width="500">
