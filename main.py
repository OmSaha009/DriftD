import argparse
import sys
import signal
from datetime import datetime, timedelta

from config import Config
from analyzer import Analyzer
from tracker import WindowTracker
from controller import SystemController


class DriftdCLI:
    """Main CLI application - Three modes only"""
    def __init__(self):
        self.config = Config()
        self.tracker = None
        self.running = False

    def setup_signal_handlers(self):
        """Handle Ctrl+C"""
        def handler(signum, frame):
            if self.tracker:
                self.tracker.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def mode_daemon(self):
        """Mode 1: Background tracking."""
        print("Driftd - Tracking Mode (Daemon)")
        print("Press Ctrl+C to stop\n")

        self.tracker = WindowTracker(self.config)
        self.tracker.start()

        self.setup_signal_handlers()
        self.running = True

        try:
            while self.running:
                signal.pause()
        except AttributeError:
            import time
            while self.running:
                time.sleep(1)

    def mode_analyzer(self):
        """Mode 2: Show usage report"""
        analyzer = Analyzer(self.config)

        print("\n" + "="*50)
        print("DRIFTD - USAGE REPORT")
        print("\n" + "="*50)

        print(analyzer.report_today())

        print("\n" + "="*50)
        print("Weekly Summary:")
        print("\n" + "="*50)

        print(analyzer.report_week())

    def mode_listener(self):
        try:
            import keyboard
            from recorder import WhisperController, CommandParser
        except ImportError as e:
            print(f"❌ Missing dependencies: {e}")
            print("Run: pip install keyboard openai-whisper sounddevice")
            return
        

        print("=" * 50)
        print("🎤 DRIFTD - Push to Talk with Whisper")
        print("=" * 50)
        
        # Initialize
        print("\nInitializing...")
        controller = SystemController()
        voice = WhisperController(model_size="base")  # Try "tiny" if "base" is slow
        parser = CommandParser(controller)
        
        print("\n" + "=" * 50)
        print("📖 HOW TO USE")
        print("=" * 50)
        print("Hold ' ` ' key and speak a command")
        print("Release when done")
        print("\n🎯 Example commands:")
        print("  • 'volume up' / 'volume down'")
        print("  • 'mute'")
        print("  • 'unmute'")
        print("  • 'brightness up' / 'brightness down'")
        print("  • 'focus mode on' / 'focus mode off'")
        print("\nPress 'esc' to quit\n")
        
        def on_push_to_talk():
            """Called when hotkey is pressed."""
            text = voice.listen_once(duration=2.5)
            
            if text:
                response = parser.execute(text)
                print(f"→ {response}\n")
            else:
                print("❌ Nothing recognized. Try again.\n")
        
        # Set up hotkey
        keyboard.add_hotkey('`', on_push_to_talk)
        self.setup_signal_handlers()

        # Keep running until ESC
        keyboard.wait('esc')
        print("\n👋 Goodbye!")
def main():
    print(f"DEBUG: sys.argv = {sys.argv}")
    parser = argparse.ArgumentParser(
        prog="driftd",
        description="Driftd - Track time and control your system",
        epilog="""
Modes:
  (no args)     Run background tracker (daemon mode)
  --report, -r  Show usage report
  --listen, -l  Push-to-talk voice control

Examples:
  driftd               # Start tracking in background
  driftd -r            # See your time usage
  driftd --listen      # Voice control (hold F8)
  driftd -l            # Same as above
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Short and long versions for each flag
    parser.add_argument(
        "--report", "-r",
        action="store_true",
        help="Show usage report"
    )
    
    parser.add_argument(
        "--listen", "-l",
        action="store_true",
        help="Start push-to-talk voice control"
    )
    
    # No --track flag needed - it's the default
    
    args = parser.parse_args()
    
    app = DriftdCLI()
    
    if args.report:
        app.mode_analyzer()
    elif args.listen:
        app.mode_listener()
    else:
        app.mode_daemon()

main()