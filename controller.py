import subprocess
import os

class SystemController:
    def __init__(self):
        self.hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        self.blocked_sites = [
            "instagram.com", "www.instagram.com",
            "twitter.com", "x.com",
            "reddit.com", "www.reddit.com",
            "facebook.com", "www.facebook.com"
        ]
    
    def volume_up(self, amount=10):
        """Increase volume. Each press = ~2% change."""
        presses = amount // 2
        for _ in range(presses):
            subprocess.run(
                ["powershell", "-Command", "$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys([char]175)"],
                capture_output=True
            )
    
    def volume_down(self, amount=10):
        """Decrease volume."""
        presses = amount // 2
        for _ in range(presses):
            subprocess.run(
                ["powershell", "-Command", "$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys([char]174)"],
                capture_output=True
            )
    
    def mute(self):
        """Toggle mute."""
        subprocess.run(
            ["powershell", "-Command", "$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys([char]173)"],
            capture_output=True
        )
    
    def _get_brightness(self):
        """Get current brightness (0-100)."""
        result = subprocess.run(
            ["powershell", "-Command", "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
            capture_output=True,
            text=True
        )
        try:
            return int(result.stdout.strip())
        except:
            return 50  # Default fallback
    
    def _set_brightness(self, level):
        """Set brightness (0-100)."""
        subprocess.run(
            ["powershell", "-Command", f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"],
            capture_output=True
        )
    
    def brightness_up(self, amount=10):
        current = self._get_brightness()
        new_value = min(current + amount, 100)
        self._set_brightness(new_value)
        print(f"Brightness: {current}% → {new_value}%")
    
    def brightness_down(self, amount=10):
        current = self._get_brightness()
        new_value = max(current - amount, 0)
        self._set_brightness(new_value)
        print(f"Brightness: {current}% → {new_value}%")
    
    def focus_mode_on(self):
        """Block distracting websites via hosts file."""
        entries = []
        for site in self.blocked_sites:
            # Block IPv4
            entries.append(f"127.0.0.1 {site}")
            entries.append(f"127.0.0.1 www.{site}")
            # Block IPv6
            entries.append(f"::1 {site}")
            entries.append(f"::1 www.{site}")

        try:
            with open(self.hosts_path, 'r') as f:
                content = f.read()
            
            if any(site in content for site in self.blocked_sites):
                print("⚠️ Focus mode already active")
                return
            
            with open(self.hosts_path, 'a') as f:
                f.write("\n# Driftd Focus Mode - Blocked Sites\n")
                f.write("\n".join(entries))
                f.write("\n")
            
            print("✅ Focus mode ON")
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
        
        except Exception as e:
            print(f"❌ Error: {e}")

    def focus_mode_off(self):
        """Unblock websites."""
        try:
            with open(self.hosts_path, 'r') as f:
                lines = f.readlines()
            
            with open(self.hosts_path, 'w') as f:
                skip_until_next_section = False
                for line in lines:
                    if "# Driftd Focus Mode" in line:
                        skip_until_next_section = True
                        continue
                    if skip_until_next_section and line.strip() == "":
                        skip_until_next_section = False
                        continue
                    if not skip_until_next_section:
                        f.write(line)
            
            print("✅ Focus mode OFF")
            
            # Flush DNS cache
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
            print("   DNS cache flushed")
            
        except Exception as e:
            print(f"❌ Error: {e}")