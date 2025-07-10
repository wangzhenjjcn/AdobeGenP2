import webview
import os
from pathlib import Path

class AdobeDesktopApp:
    """Adobe Download Center Desktop Application"""
    
    def __init__(self):
        self.setup_app()
        
    def setup_app(self):
        """Setup the desktop application"""
        # Get the path to index.html
        current_dir = Path(__file__).parent
        index_path = current_dir / "index.html"
        
        if not index_path.exists():
            self.create_placeholder_html(index_path)
        
        # Convert to absolute path and file URL
        file_url = f"file:///{index_path.absolute().as_posix()}"
        
        # Create webview window with custom settings
        webview.create_window(
            'Adobe Download Center',
            file_url,
            width=1200,
            height=800,
            resizable=True,
            minimized=False,
            on_top=False,
            shadow=False,
            fullscreen=False,
            min_size=(600, 400),
            js_api=self.JSApi(),
            debug=False
        )
        
    class JSApi:
        """JavaScript API for the webview"""
        
        def disable_context_menu(self):
            """Disable right-click context menu"""
            return True
            
    def create_placeholder_html(self, path):
        """Create a placeholder HTML file if index.html doesn't exist"""
        placeholder_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adobe Download Center</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .container {
            max-width: 600px;
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #fff;
        }
        
        p {
            font-size: 1.2em;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        
        .status {
            background: rgba(255, 255, 255, 0.2);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: #ff6b6b;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s ease;
            font-weight: bold;
            cursor: pointer;
        }
        
        .btn:hover {
            background: #ff5252;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Adobe Download Center</h1>
        <p>Welcome to the Adobe Download Center desktop application!</p>
        
        <div class="status">
            <h3>⚠️ Setup Required</h3>
            <p>Please run <code>python app.py</code> first to generate the download links and create the index.html file.</p>
        </div>
        
        <p>This application provides a desktop interface for browsing and downloading Adobe software packages.</p>
        
        <button class="btn" onclick="location.reload()">🔄 Refresh</button>
    </div>
    
    <script>
        // Disable right-click context menu
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });
        
        // Disable developer tools shortcuts
        document.addEventListener('keydown', function(e) {
            // Disable F12
            if (e.key === 'F12') {
                e.preventDefault();
                return false;
            }
            // Disable Ctrl+Shift+I (Developer Tools)
            if (e.ctrlKey && e.shiftKey && e.key === 'I') {
                e.preventDefault();
                return false;
            }
            // Disable Ctrl+U (View Source)
            if (e.ctrlKey && e.key === 'U') {
                e.preventDefault();
                return false;
            }
            // Disable Ctrl+Shift+C (Element Inspector)
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                return false;
            }
        });
        
        // Auto-refresh every 60 seconds to check for updates
        setTimeout(function() {
            location.reload();
        }, 60000);
    </script>
</body>
</html>"""
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
            
    def run(self):
        """Start the desktop application"""
        # Start webview with custom settings
        webview.start(
            debug=False,
            http_server=False,
            user_agent='Adobe Download Center Desktop App v1.0'
        )

def main():
    """Main function to start the application"""
    print("Starting Adobe Download Center Desktop App...")
    
    # Check if pywebview is installed
    try:
        import webview
    except ImportError:
        print("Error: pywebview is required but not installed.")
        print("Please install it with: pip install pywebview")
        return
    
    # Create and run the app
    app = AdobeDesktopApp()
    app.run()

if __name__ == "__main__":
    main() 