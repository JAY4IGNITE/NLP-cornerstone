import re

def patch_glass_css():
    path = 'c:/Users/ramuv/NLP-cornerstone/src/index.css'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # We will redefine the root variables for the glass theme
    css_vars = """@import "tailwindcss";

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  font-family: 'Outfit', system-ui, -apple-system, sans-serif;
  color: #1a1a1c;
  
  /* Luxury light background with subtle gradient */
  background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
  background-attachment: fixed;
  
  font-synthesis: none;
  -webkit-font-smoothing: antialiased;
  
  --bg: transparent; /* Rely on body background */
  --sidebar: rgba(245, 245, 244, 0.5); /* Glass */
  --surface: rgba(255, 255, 255, 0.65); /* Glass */
  --surface-hover: rgba(255, 255, 255, 0.9);
  --ink: #1a1a1c;
  --muted: #6b7280;
  --subtle: #9ca3af;
  --line: rgba(0, 0, 0, 0.06);
  --accent: #2563eb; /* Royal blue for luxury */
  --accent-hover: #1d4ed8;
  --accent-soft: rgba(37, 99, 235, 0.1);
  --green: #0ea5e9;
  --shadow: 0 12px 32px 0 rgba(31, 38, 135, 0.07);
  --glass-blur: blur(20px);
  --glass-border: 1px solid rgba(255, 255, 255, 0.4);
  
  color-scheme: light;
}

[data-theme="dark"] {
  /* Luxury dark background with deep gradient */
  background: linear-gradient(135deg, #0f1115 0%, #171822 100%);
  background-attachment: fixed;
  
  --bg: transparent;
  --sidebar: rgba(15, 17, 21, 0.4);
  --surface: rgba(30, 32, 40, 0.45);
  --surface-hover: rgba(45, 48, 60, 0.6);
  --ink: #f3f4f6;
  --muted: #9ca3af;
  --subtle: #6b7280;
  --line: rgba(255, 255, 255, 0.06);
  --accent: #3b82f6; 
  --accent-hover: #60a5fa;
  --accent-soft: rgba(59, 130, 246, 0.15);
  --green: #38bdf8;
  --shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  --glass-border: 1px solid rgba(255, 255, 255, 0.05);
  
  color-scheme: dark;
}

* { box-sizing: border-box; scrollbar-width: thin; scrollbar-color: var(--line) transparent; }
body { margin: 0; font-family: 'Outfit', sans-serif; letter-spacing: -0.01em; }"""
    
    # Replace the existing root and dark variables
    content = re.sub(r'@import "tailwindcss";.*?body \{ margin: 0; font-family: \'Outfit\', sans-serif; letter-spacing: -0\.01em; \}', css_vars, content, flags=re.DOTALL)
    
    # Replace normal styles with Glassmorphism and extreme roundness
    
    # Make sidebar glass
    content = re.sub(r'\.sidebar \{.*?\}', '.sidebar { width: 268px; margin-left: -268px; padding: 26px 18px 16px; flex: none; display: flex; flex-direction: column; background: var(--sidebar); backdrop-filter: var(--glass-blur); border-right: var(--glass-border); transition: margin-left .22s; overflow: hidden; }', content, flags=re.DOTALL)
    
    # Make composer very round and glass
    content = re.sub(r'\.composer \{.*?\}', '.composer { background: var(--surface); backdrop-filter: var(--glass-blur); border: var(--glass-border); border-radius: 28px; padding: 18px 18px 12px; box-shadow: var(--shadow); transition: border-color .15s, box-shadow .15s; }', content, flags=re.DOTALL)
    
    # Buttons round
    content = re.sub(r'\.new-chat-button \{.*?\}', '.new-chat-button { display: flex; align-items: center; gap: 10px; padding: 12px 20px; border: none; background: var(--accent); color: #ffffff; border-radius: 999px; font-size: 14px; font-weight: 500; min-height: 44px; box-shadow: 0 4px 14px 0 rgba(0, 118, 255, 0.2); transition: all 0.2s ease; }', content, flags=re.DOTALL)
    content = re.sub(r'\.primary-button, \.secondary-button, \.danger-button \{.*?\}', '.primary-button, .secondary-button, .danger-button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 20px; border-radius: 999px; font-size: 13px; font-weight: 500; transition: all 0.2s ease; }', content, flags=re.DOTALL)
    
    # Icon buttons perfectly round
    content = re.sub(r'\.icon-button \{.*?\}', '.icon-button { display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; flex-shrink: 0; border-radius: 50%; color: var(--muted); transition: all 0.2s ease; }', content, flags=re.DOTALL)
    content = re.sub(r'\.send-button \{.*?\}', '.send-button { display: grid; place-items: center; width: 38px; height: 38px; border-radius: 50%; background: var(--accent); color: #ffffff; box-shadow: 0 2px 10px rgba(37,99,235,0.3); transition: all 0.2s; }', content, flags=re.DOTALL)
    
    # Dialogs glass
    content = re.sub(r'\.dialog \{.*?\}', '.dialog { background: var(--surface); backdrop-filter: var(--glass-blur); border: var(--glass-border); color: var(--ink); padding: 0; border-radius: 28px; width: min(480px, calc(100% - 32px)); max-height: calc(100dvh - 48px); margin: auto; box-shadow: var(--shadow); }', content, flags=re.DOTALL)
    
    # Suggestions glass
    content = re.sub(r'\.suggestion \{.*?\}', '.suggestion { text-align: left; background: var(--surface); backdrop-filter: var(--glass-blur); border: var(--glass-border); border-radius: 20px; padding: 18px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }', content, flags=re.DOTALL)
    
    # User message bubble glass/round
    content = re.sub(r'\.user-message > div \{.*?\}', '.user-message > div { background: var(--surface); backdrop-filter: var(--glass-blur); border: var(--glass-border); color: var(--ink); border-radius: 24px 24px 6px 24px; max-width: 86%; padding: 15px 22px; font-size: 15px; font-weight: 400; line-height: 1.6; white-space: pre-wrap; overflow-wrap: anywhere; box-shadow: var(--shadow); }', content, flags=re.DOTALL)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

patch_glass_css()
print("Glass theme applied.")
