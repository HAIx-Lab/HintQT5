import os
# Set Kivy environment variables to ensure it works correctly as an overlay
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_BORDERLESS'] = '1'

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.logger import Logger

# This will only be available when running on Android
try:
    from jnius import autoclass
    ANDROID_ENVIRONMENT = True
except ImportError:
    ANDROID_ENVIRONMENT = False

class HintOverlayApp(App):
    """
    A Kivy app that displays a temporary, transparent overlay with hint text.
    It's designed to be launched remotely by an ADB command.
    """
    def build(self):
        hint_text = "Default Hint"
        x1, y1, x2, y2 = 100, 100, 400, 200

        if ANDROID_ENVIRONMENT:
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                intent = PythonActivity.mActivity.getIntent()
                
                # Retrieve data passed from the ADB command
                hint_text_from_intent = intent.getStringExtra('text')
                bounds_str_from_intent = intent.getStringExtra('bounds')
                
                if hint_text_from_intent:
                    hint_text = hint_text_from_intent.replace('-', ' ') # Restore spaces
                if bounds_str_from_intent:
                    bounds = [int(p) for p in bounds_str_from_intent.split(',')]
                    x1, y1, x2, y2 = bounds
                
                Logger.info(f"KivyApp: Received text='{hint_text}', bounds={bounds}")
            except Exception as e:
                Logger.error(f"KivyApp: Could not read intent extras: {e}")
        else:
            Logger.info("KivyApp: Not running on Android, using default values.")

        # Make the window transparent and borderless
        Window.clearcolor = (0, 0, 0, 0)
        
        layout = FloatLayout()
        
        # Kivy's Y-coordinate starts from the bottom, Android's from the top. Convert it.
        display_height = Window.height 
        kivy_y = display_height - y2

        # Create the label for the hint
        hint_label = Label(
            text=hint_text,
            size_hint=(None, None),
            size=(x2 - x1, y2 - y1),
            pos=(x1, kivy_y),
            color=get_color_from_hex('#FFFFFF'),
            outline_color=get_color_from_hex('#000000'),
            outline_width=2,
            font_size='18sp',
            halign='center',
            valign='middle',
            padding=(10, 10)
        )
        hint_label.bind(size=hint_label.setter('text_size'))
        
        # Add a semi-transparent background for readability
        with hint_label.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.1, 0.1, 0.1, 0.85)
            self.bg_rect = RoundedRectangle(pos=hint_label.pos, size=hint_label.size, radius=[10])
        
        def update_rect(instance, value):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
        
        hint_label.bind(pos=update_rect, size=update_rect)

        layout.add_widget(hint_label)
        
        # Schedule the app to close automatically after 5 seconds
        Clock.schedule_once(self.stop_app, 5) 
        
        return layout

    def stop_app(self, dt):
        """Safely closes the Kivy application."""
        Logger.info("KivyApp: Timeout reached, closing application.")
        App.get_running_app().stop()

if __name__ == '__main__':
    HintOverlayApp().run()

