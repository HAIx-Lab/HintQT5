# HintQT5
Repository for the paper: "Adaptive Text Inputs: Contextual Hint-Text Generation for Enhancing Mobile Apps Accessibility using Text-to-Text Transformer Language Models and Q-learning"

HintQT5 is an intelligent system designed to automatically generate context-aware hint text for input fields within Android applications. It uses a fine-tuned language models to suggest hints and employs Reinforcement Learning to improve its suggestions based on real-time user feedback.

This project features two distinct feedback mechanisms for learning, located in separate directories:

1.  **Binary Feedback (main directory):** A simple "yes/no" confirmation from the user.
2.  **Graded Feedback (multiRL directory):** A more nuanced approach where the AI's suggestion is compared to a user-provided ideal hint, and a reward is calculated based on their semantic similarity.

## Architecture

The system operates with two main components that communicate with each other:

1.  **Main Controller (Your Computer):**
    * Runs the core Python scripts (`main.py`, `rl_agent.py`, etc.).
    * Analyzes the device's UI layout using `uiautomator2`.
    * Generates hints using the language model.
    * Processes user feedback from the terminal to train the RL agent.

2.  **Kivy Helper App (On the Android Device):**
    * A small, separate application (`hint_display_kivy.py`) that is installed on the target Android device.
    * Its sole purpose is to receive commands from the Main Controller and display the generated hint text as an overlay on the screen.

Communication between the two is handled by the **Android Debug Bridge (ADB)**, which sends commands from the computer to the device over a USB connection.

## Project Structure

* `main.py`: The central script that orchestrates the entire process.
* `rl_agent.py`: Contains the `RLAgent` class, which handles the model's learning logic.
* `ui_utils.py`: A set of functions for parsing and analyzing the Android UI hierarchy XML.
* `prompt_generator.py`: Constructs the detailed prompts that are fed into the model.
* `feedback_manager.py`: Manages saving and loading the feedback history to a JSON file.
* `display_utils.py`: A utility to construct and send the `adb` command that launches the Kivy overlay.
* `similarity_utils.py`: (Only in the `multiRL` version) Calculates the semantic similarity between hints.
* `hint_display_kivy.py`: The source code for the Kivy Android application that displays the overlays.
* `requirements.txt`: A list of all Python dependencies for the main controller.

## Setup and Installation

Follow these steps carefully to set up the project.

### Part A: Setting Up the Computer Environment

1.  **Prerequisites:**
    * Python 3.8 or newer.
    * [Android Debug Bridge (ADB)](https://developer.android.com/studio/command-line/adb) installed and accessible from your terminal.

2.  **Create a Project Folder:**
    * Create a new folder and place all the Python files (`main.py`, `rl_agent.py`, etc.) inside it.

3.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  **Install Dependencies:**
    * Install all required Python libraries using the provided `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

5.  **Place Your Language Model:**
    * Fine-tune your Language model using the 'Fine_tuning.ipynb'.
    * Place the model files in a known directory.
    * Open `main.py` in both the main directory and the `multiRL` directory and **update the `MODEL_PATH` variable** to point to this directory.

### Part B: Building and Installing the Kivy Helper App

This process packages the `hint_display_kivy.py` script into an Android app (`.apk`).

1.  **Prerequisites:**
    * It's recommended to do this in a separate folder and virtual environment to avoid dependency conflicts.

2.  **Install Buildozer:**
    ```bash
    pip install buildozer
    ```

3.  **Initialize Buildozer:**
    * Create a new folder (e.g., `KivyHelper`).
    * Place `hint_display_kivy.py` inside it.
    * Navigate into the folder in your terminal and run:
    ```bash
    buildozer init
    ```
    * This will create a `buildozer.spec` file.

4.  **Configure `buildozer.spec`:**
    * Open the `buildozer.spec` file and edit the following lines. **These must be set correctly.**
    ```ini
    # (section) App Description
    title = Hint Overlay
    package.name = hintoverlay
    package.domain = com.mycompany

    # (section) Requirements
    # Add pyjnius to the requirements
    requirements = python3,kivy,pyjnius

    # (section) Permissions
    # No special permissions are needed for this app.
    ```
    * The final package name will be `com.mycompany.hintoverlay`.

5.  **Build and Deploy the App:**
    * Connect your Android device to your computer via USB.
    * Enable **USB Debugging** in the Developer Options on the device.
    * Run the following command. This will build the `.apk`, install it on your device, and run it once.
    ```bash
    buildozer -v android debug deploy run
    ```

### Part C: Final Configuration

1.  **Verify ADB Connection:**
    * Ensure your device is recognized by running `adb devices`. You should see your device listed.

2.  **Match Package Names:**
    * Open `display_utils.py` on your computer.
    * Ensure the `KIVY_APP_PACKAGE_NAME` variable exactly matches the package name from `buildozer.spec` (`com.mycompany.hintoverlay`).

## How to Run the Project

This project contains two separate implementations based on the feedback mechanism used for Reinforcement Learning.

1.  **Connect Your Device:** Make sure your Android device or emulator is connected and unlocked.
2.  **Activate Your Environment:** Activate the Python virtual environment you created during setup.
    ```bash
    source venv/bin/activate
    ```

### Running the Binary Feedback Version

This version uses a simple "yes/no" feedback loop.

* Navigate to the root `HintQT5` project folder and run the main script:
    ```bash
    python main.py
    ```

### Running the Graded Feedback Version (multiRL)

This version compares the AI's hint to your ideal hint to generate a graded reward.

* Navigate into the `multiRL` subdirectory and run its main script:
    ```bash
    cd multiRL
    python main.py
    ```

After starting one of the scripts, you can begin interacting with your Android device. The terminal will show logs and prompt you for feedback when necessary.

## Troubleshooting

* **Error: Activity class {...} does not exist:** This means the package name in `display_utils.py` does not match the one installed on the device, or the app is not installed correctly. Double-check your `buildozer.spec` and `display_utils.py` files, then rebuild and reinstall the Kivy app.
* **Kivy App Crashes / `jnius` is not defined:** You forgot to add `pyjnius` to the `requirements` line in the `buildozer.spec` file. Add it and rebuild.
* **Slow Feedback Loop:** The agent uses batch training to avoid retraining after every hint. You can adjust the `TRAIN_AFTER_N_HINTS` variable in `main.py` to change the frequency.

## 📚 Citation

If you use **HintQT5** in your research or project, please cite it as:

**Sanvi Shukla. (2025).** *HintQT5: Context-Aware Hint Text Generation using Reinforcement Learning.*  
_In Proceedings of India HCI 2025 – The 16th International Conference of Human-Computer Interaction (HCI) Design & Research (IndiaHCI ’25), November 7–9, 2025, Delhi, India._  
Association for Computing Machinery. https://doi.org/10.1145/3768633.3770136
