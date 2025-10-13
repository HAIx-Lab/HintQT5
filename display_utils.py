import os

# --- CONFIGURATION ---
# IMPORTANT: This must match the package name you define in your buildozer.spec file.
KIVY_APP_PACKAGE_NAME = "com.mycompany.hintoverlay"

def show_hint(bounds: list, hint_text: str):
    """
    Constructs and executes an ADB command to launch the Kivy overlay app on the device.
    """
    if not all(isinstance(p, int) for p in bounds) or len(bounds) != 4:
        print(f"Error: Invalid bounds provided for hint '{hint_text}'. Got: {bounds}")
        return

    # Format the hint text for the command line (replace spaces with a placeholder)
    hint_text_formatted = hint_text.replace(' ', '-')
    bounds_str = ",".join(map(str, bounds))

    # Construct the adb command
    # This command starts an activity by its full component name and passes data via 'extras' (-e)
    cmd = (
        f"adb shell am start -n {KIVY_APP_PACKAGE_NAME}/org.kivy.android.PythonActivity "
        f"-e text '{hint_text_formatted}' "
        f"-e bounds '{bounds_str}'"
    )

    print(f"Executing display command: {cmd}")
    try:
        os.system(cmd)
    except Exception as e:
        print(f"Error executing ADB command to display hint: {e}")

