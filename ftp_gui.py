"""
OctopusFTP GUI - Modern CustomTkinter interface for multi-connection FTP downloader
"""

import sys
import os

# Add lib directory to path for local customtkinter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from ftp_engine import MultiConnectionFTP, FileInfo
from bandwidth_chart import CompactBandwidthChart
from checksum_utils import ChecksumCalculator

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"


class FTPDownloaderGUI:
    """Main GUI application for FTP downloader"""

    def __init__(self):
        """Initialize the GUI"""
        self.root = ctk.CTk()
        self.root.title("🐙 OctopusFTP - Multi-Connection FTP Downloader")
        self.root.geometry("1100x750")
        self.root.minsize(1100, 650)

        # FTP connection
        self.ftp: Optional[MultiConnectionFTP] = None
        self.connected = False
        self.current_path = "/"

        # Download tracking
        self.active_downloads: Dict[str, Dict] = {}

        # Settings and connection presets
        self.config_dir = Path.home() / ".octopusftp"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.connections_file = self.config_dir / "connections.json"
        self.settings_file = self.config_dir / "settings.json"

        self.saved_connections = self._load_connections()
        self.settings = self._load_settings()

        # Load last download folder or use default
        self.download_destination = self.settings.get("last_download_folder",
                                                       os.path.expanduser("~/Downloads"))

        # Create UI
        self._create_widgets()

        # Update timer
        self._schedule_update()

    def _create_widgets(self):
        """Create all UI widgets"""
        # Main container
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Main frame
        main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=60, uniform="cols")  # Remote Files - 60%
        main_frame.grid_columnconfigure(1, weight=40, uniform="cols")  # Downloads - 40%
        main_frame.grid_rowconfigure(2, weight=1)  # Row 2 (browser/downloads) expands

        # Top section: Connection + Config
        self._create_connection_frame(main_frame)
        self._create_config_frame(main_frame)

        # Middle section: 2 columns
        # LEFT: Remote Files
        self._create_browser_content(main_frame)

        # RIGHT: Downloads
        self._create_downloads_section(main_frame)

        # Status bar
        self._create_status_bar(main_frame)

    def _create_connection_frame(self, parent):
        """Create connection configuration frame"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        # Title
        title = ctk.CTkLabel(frame, text="📡 FTP/FTPS Connection", font=ctk.CTkFont(size=14, weight="bold"))
        title.grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(10, 5))

        # Row 0.5: Saved connections selector
        ctk.CTkLabel(frame, text="Saved:").grid(row=1, column=0, sticky="w", padx=(10, 5), pady=5)
        self.connection_selector = ctk.CTkComboBox(frame, values=self._get_connection_names(),
                                                   command=self._load_selected_connection,
                                                   width=200, state="readonly")
        self.connection_selector.set("-- Select Connection --")
        self.connection_selector.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Save/Delete buttons
        self.save_btn = ctk.CTkButton(frame, text="💾 Save", width=80,
                                     command=self._save_current_connection,
                                     fg_color="#4CAF50", hover_color="#45a049")
        self.save_btn.grid(row=1, column=2, sticky="w", padx=5, pady=5)

        self.delete_btn = ctk.CTkButton(frame, text="🗑️ Delete", width=80,
                                       command=self._delete_selected_connection,
                                       fg_color="#f44336", hover_color="#da190b")
        self.delete_btn.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Row 2: Server, Port
        ctk.CTkLabel(frame, text="Server:").grid(row=2, column=0, sticky="w", padx=(10, 5), pady=5)
        self.server_entry = ctk.CTkEntry(frame, placeholder_text="ftp.example.com")
        self.server_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(frame, text="Port:").grid(row=2, column=2, sticky="w", padx=(10, 5), pady=5)
        self.port_entry = ctk.CTkEntry(frame, width=80, placeholder_text="21")
        self.port_entry.insert(0, "21")
        self.port_entry.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # Row 3: Username, Password, SSL
        ctk.CTkLabel(frame, text="Username:").grid(row=3, column=0, sticky="w", padx=(10, 5), pady=5)
        self.user_entry = ctk.CTkEntry(frame, placeholder_text="username")
        self.user_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(frame, text="Password:").grid(row=3, column=2, sticky="w", padx=(10, 5), pady=5)
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="password", show="•")
        self.password_entry.grid(row=3, column=3, sticky="ew", padx=5, pady=5)

        # SSL checkbox and Connect button
        self.ssl_var = ctk.BooleanVar(value=True)
        self.ssl_checkbox = ctk.CTkCheckBox(frame, text="🔒 SSL/TLS", variable=self.ssl_var)
        self.ssl_checkbox.grid(row=2, column=4, sticky="w", padx=10, pady=5)

        self.connect_btn = ctk.CTkButton(frame, text="Connect", width=120,
                                         command=self._toggle_connection,
                                         fg_color="#2196F3", hover_color="#1976D2")
        self.connect_btn.grid(row=3, column=4, sticky="ew", padx=10, pady=5)

    def _create_config_frame(self, parent):
        """Create download configuration frame"""
        # Config options in horizontal layout (compact, inside connection frame)
        config_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=("#E0E0E0", "#2B2B2B"))
        config_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

        ctk.CTkLabel(config_frame, text="⚙️ Config:",
                    font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=10)

        ctk.CTkLabel(config_frame, text="Connections:").pack(side="left", padx=(20, 5))
        self.connections_var = ctk.IntVar(value=4)
        ctk.CTkEntry(config_frame, width=50, textvariable=self.connections_var).pack(side="left", padx=5)

        ctk.CTkLabel(config_frame, text="Rotation (sec):").pack(side="left", padx=(20, 5))
        self.rotation_var = ctk.IntVar(value=30)
        ctk.CTkEntry(config_frame, width=50, textvariable=self.rotation_var).pack(side="left", padx=5)

        ctk.CTkLabel(config_frame, text="Max Speed (MB/s):").pack(side="left", padx=(20, 5))
        self.speed_limit_var = ctk.StringVar(value="0")  # 0 = unlimited
        speed_entry = ctk.CTkEntry(config_frame, width=50, textvariable=self.speed_limit_var, placeholder_text="0")
        speed_entry.pack(side="left", padx=5)

        # Add tooltip label
        ctk.CTkLabel(config_frame, text="(0 = unlimited)", text_color="gray",
                    font=ctk.CTkFont(size=9)).pack(side="left", padx=(0, 10))

    def _create_browser_content(self, parent):
        """Create file browser frame"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=2, column=0, sticky="nsew", padx=(5, 2), pady=5)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_propagate(False)  # Don't resize based on content

        # Title
        title = ctk.CTkLabel(frame, text="📁 Remote Files", font=ctk.CTkFont(size=14, weight="bold"))
        title.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        # Navigation
        nav_frame = ctk.CTkFrame(frame, fg_color="transparent")
        nav_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        nav_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(nav_frame, text="↑ Parent", width=80, command=self._go_parent).grid(row=0, column=0, padx=2)
        ctk.CTkButton(nav_frame, text="🔄 Refresh", width=80, command=self._refresh_list).grid(row=0, column=1, padx=2)

        self.path_label = ctk.CTkLabel(nav_frame, text="/", anchor="w",
                                       fg_color=("#CCCCCC", "#333333"), corner_radius=5, padx=10)
        self.path_label.grid(row=0, column=2, sticky="ew", padx=(10, 0))

        # File list (using scrollable frame)
        self.file_listbox = ctk.CTkScrollableFrame(frame, label_text="")
        self.file_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.file_listbox.grid_columnconfigure(0, weight=1)

        # FORCE mousewheel scroll to work on macOS
        self._bind_mousewheel(self.file_listbox)

        # Store file items
        self.file_items = []

    def _create_downloads_section(self, parent):
        """Create downloads section (destination + active downloads)"""
        container = ctk.CTkFrame(parent, corner_radius=10)
        container.grid(row=2, column=1, sticky="nsew", padx=(2, 5), pady=5)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_propagate(False)  # Don't resize based on content

        # Destination frame
        dest_frame = ctk.CTkFrame(container, corner_radius=8, fg_color=("#E0E0E0", "#2B2B2B"))
        dest_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        dest_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(dest_frame, text="💾 Download Destination",
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 0))

        self.dest_label = ctk.CTkLabel(dest_frame, text=self.download_destination, anchor="w",
                                      fg_color=("#CCCCCC", "#333333"), corner_radius=5, padx=10)
        self.dest_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 5))

        btn_frame = ctk.CTkFrame(dest_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        ctk.CTkButton(btn_frame, text="📁 Choose Folder", width=140,
                     command=self._choose_destination).pack(side="left", padx=(0, 5))

        self.download_btn = ctk.CTkButton(btn_frame, text="⬇ Download Selected", width=140,
                                         command=self._start_download, state="disabled",
                                         fg_color="#4CAF50", hover_color="#45a049",
                                         text_color="white", text_color_disabled="white")
        self.download_btn.pack(side="left")

        # Active downloads
        dl_title = ctk.CTkLabel(container, text="📊 Active Downloads",
                               font=ctk.CTkFont(size=14, weight="bold"))
        dl_title.grid(row=1, column=0, sticky="nw", padx=10, pady=(10, 0))

        self.downloads_frame = ctk.CTkScrollableFrame(container, label_text="", fg_color="transparent")
        self.downloads_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(35, 10))
        self.downloads_frame.grid_columnconfigure(0, weight=1)

        # FORCE mousewheel scroll to work on macOS
        self._bind_mousewheel(self.downloads_frame)

        # Store download widgets
        self.download_widgets = {}

    def _create_status_bar(self, parent):
        """Create status bar"""
        self.status_label = ctk.CTkLabel(parent, text="🔴 Not connected", anchor="w",
                                        fg_color=("#DDDDDD", "#2B2B2B"), corner_radius=5,
                                        padx=10, pady=5)
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

    def _bind_mousewheel(self, scrollable_frame):
        """
        Bind mousewheel scrolling to a CTkScrollableFrame (macOS trackpad fix)

        CustomTkinter's scrollable frames don't always respond to mousewheel
        events on macOS. This method manually binds the mousewheel to the
        underlying canvas for smooth scrolling.
        """
        def on_mousewheel(event):
            # Scroll the canvas directly using the event delta
            # Negative delta = scroll down, positive = scroll up
            scrollable_frame._parent_canvas.yview_scroll(int(-1 * (event.delta)), "units")

        # Bind to both the canvas and the frame for maximum compatibility
        scrollable_frame._parent_canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)

    # Connection preset management

    def _load_connections(self) -> Dict:
        """Load saved connections from JSON file"""
        if not self.connections_file.exists():
            return {}

        try:
            with open(self.connections_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading connections: {e}")
            return {}

    def _save_connections(self):
        """Save connections to JSON file"""
        try:
            with open(self.connections_file, 'w') as f:
                json.dump(self.saved_connections, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save connections: {e}")

    def _load_settings(self) -> Dict:
        """Load application settings from JSON file"""
        if not self.settings_file.exists():
            return {}

        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def _save_settings(self):
        """Save application settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def _get_connection_names(self) -> List[str]:
        """Get list of saved connection names"""
        return list(self.saved_connections.keys()) if self.saved_connections else [""]

    def _load_selected_connection(self, choice: str):
        """Load a selected connection from dropdown"""
        if choice == "-- Select Connection --" or not choice:
            return

        if choice in self.saved_connections:
            conn = self.saved_connections[choice]
            self.server_entry.delete(0, "end")
            self.server_entry.insert(0, conn.get("host", ""))
            self.port_entry.delete(0, "end")
            self.port_entry.insert(0, str(conn.get("port", 21)))
            self.user_entry.delete(0, "end")
            self.user_entry.insert(0, conn.get("user", ""))
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, conn.get("password", ""))
            self.ssl_var.set(conn.get("ssl", True))

    def _save_current_connection(self):
        """Save current connection settings"""
        host = self.server_entry.get().strip()
        user = self.user_entry.get().strip()

        if not host or not user:
            messagebox.showerror("Error", "Please enter at least server and username")
            return

        # Ask for connection name
        from tkinter import simpledialog
        name = simpledialog.askstring("Save Connection",
                                     "Enter a name for this connection:",
                                     initialvalue=f"{user}@{host}")
        if not name:
            return

        # Ask if user wants to save password
        save_password = messagebox.askyesno("Save Password?",
                                           "Do you want to save the password?\n\n"
                                           "⚠️ Warning: Password will be stored in plain text!")

        # Save connection
        self.saved_connections[name] = {
            "host": host,
            "port": int(self.port_entry.get() or 21),
            "user": user,
            "password": self.password_entry.get() if save_password else "",
            "ssl": self.ssl_var.get()
        }

        self._save_connections()

        # Update dropdown
        self.connection_selector.configure(values=self._get_connection_names())
        self.connection_selector.set(name)

        messagebox.showinfo("Success", f"Connection '{name}' saved!")

    def _delete_selected_connection(self):
        """Delete the selected connection"""
        choice = self.connection_selector.get()

        if choice == "-- Select Connection --" or not choice:
            messagebox.showwarning("Warning", "Please select a connection to delete")
            return

        if choice in self.saved_connections:
            if messagebox.askyesno("Confirm Delete",
                                  f"Delete connection '{choice}'?"):
                del self.saved_connections[choice]
                self._save_connections()

                # Update dropdown
                self.connection_selector.configure(values=self._get_connection_names())
                self.connection_selector.set("-- Select Connection --")

                messagebox.showinfo("Success", f"Connection '{choice}' deleted!")

    # Connection methods

    def _toggle_connection(self):
        """Toggle FTP connection"""
        if self.connected:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        """Connect to FTP server"""
        host = self.server_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.password_entry.get()

        if not host or not user:
            messagebox.showerror("Error", "Please enter server and username")
            return

        try:
            port = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return

        use_ssl = self.ssl_var.get()

        def connect_thread():
            try:
                # Get speed limit (0 = unlimited)
                try:
                    max_speed = float(self.speed_limit_var.get())
                    max_speed = max_speed if max_speed > 0 else None
                except (ValueError, AttributeError):
                    max_speed = None

                ftp = MultiConnectionFTP(host, user, password, port, use_ssl, max_speed)
                success, message = ftp.test_connection()

                if success:
                    self.ftp = ftp
                    self.connected = True
                    self.current_path = "/"
                    self.root.after(0, lambda: self._on_connect_success(message))
                else:
                    self.root.after(0, lambda: self._on_connect_failure(message))
            except Exception as e:
                self.root.after(0, lambda: self._on_connect_failure(str(e)))

        threading.Thread(target=connect_thread, daemon=True).start()
        self._update_status("🔄 Connecting...")

    def _on_connect_success(self, message):
        """Handle successful connection"""
        self.connect_btn.configure(text="Disconnect", fg_color="#f44336", hover_color="#d32f2f")
        self.download_btn.configure(state="normal")
        self._update_status(f"🟢 Connected to {self.server_entry.get()}")
        self._refresh_list()

    def _on_connect_failure(self, message):
        """Handle connection failure"""
        messagebox.showerror("Connection Failed", message)
        self._update_status("🔴 Not connected")

    def _disconnect(self):
        """Disconnect from FTP server"""
        if self.ftp:
            self.ftp.stop()
            self.ftp = None

        self.connected = False
        self.connect_btn.configure(text="Connect", fg_color="#2196F3", hover_color="#1976D2")
        self.download_btn.configure(state="disabled")
        self._clear_file_list()
        self._update_status("🔴 Disconnected")

    # File browser methods

    def _refresh_list(self):
        """Refresh file list"""
        if not self.connected:
            return

        def list_thread():
            try:
                items = self.ftp.list_directory(self.current_path)
                self.root.after(0, lambda: self._populate_file_list(items))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", f"Failed to list directory: {msg}"))

        threading.Thread(target=list_thread, daemon=True).start()
        self._update_status("🔄 Loading...")

    def _populate_file_list(self, items: List[FileInfo]):
        """Populate file list with items"""
        self._clear_file_list()

        # Reset scroll position to top
        self.file_listbox._parent_canvas.yview_moveto(0)

        # Sort: directories first, then files
        items.sort(key=lambda x: (not x.is_dir, x.name.lower()))

        for item in items:
            self._create_file_item(item)

        self.path_label.configure(text=self.current_path)
        self._update_status(f"🟢 Connected - {len(items)} items in {self.current_path}")

    def _create_file_item(self, item: FileInfo):
        """Create a file/folder item widget"""
        # Item frame
        item_frame = ctk.CTkFrame(self.file_listbox, corner_radius=5, fg_color=("#F5F5F5", "#2B2B2B"))
        item_frame.pack(fill="x", pady=2, padx=2)
        item_frame.grid_columnconfigure(0, weight=1)

        # Icon and name
        icon = "📁" if item.is_dir else "📄"
        name_text = f"{icon} {item.name}"

        item_label = ctk.CTkLabel(item_frame, text=name_text, anchor="w")
        item_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        # Size
        size_text = "-" if item.is_dir else self._format_size(item.size)
        size_label = ctk.CTkLabel(item_frame, text=size_text, width=100)
        size_label.grid(row=0, column=1, padx=10, pady=5)

        # Store reference
        item_frame.item_data = item
        self.file_items.append(item_frame)

        # Click events
        # Single click: select (both files and folders)
        item_frame.bind("<Button-1>", lambda e, f=item_frame: self._toggle_file_selection(f))
        item_label.bind("<Button-1>", lambda e, f=item_frame: self._toggle_file_selection(f))
        size_label.bind("<Button-1>", lambda e, f=item_frame: self._toggle_file_selection(f))

        # Double click on folders: navigate
        if item.is_dir:
            item_frame.bind("<Double-Button-1>", lambda e, path=item.path: self._navigate_to(path))
            item_label.bind("<Double-Button-1>", lambda e, path=item.path: self._navigate_to(path))
            size_label.bind("<Double-Button-1>", lambda e, path=item.path: self._navigate_to(path))

    def _toggle_file_selection(self, item_frame):
        """Toggle selection state of a file item"""
        if not hasattr(item_frame, 'selected'):
            item_frame.selected = False

        item_frame.selected = not item_frame.selected

        if item_frame.selected:
            item_frame.configure(fg_color=("#2196F3", "#1565C0"))
        else:
            item_frame.configure(fg_color=("#F5F5F5", "#2B2B2B"))

    def _clear_file_list(self):
        """Clear all file items"""
        for item in self.file_items:
            item.destroy()
        self.file_items.clear()

    def _navigate_to(self, path):
        """Navigate to directory"""
        self.current_path = path
        self._refresh_list()

    def _go_parent(self):
        """Navigate to parent directory"""
        if not self.connected or self.current_path == "/":
            return

        self.current_path = os.path.dirname(self.current_path.rstrip('/'))
        if not self.current_path:
            self.current_path = "/"
        self._refresh_list()

    # Download methods

    def _choose_destination(self):
        """Choose download destination"""
        directory = filedialog.askdirectory(initialdir=self.download_destination,
                                           title="Choose Download Destination")
        if directory:
            self.download_destination = directory
            # Truncate for display
            display_text = directory if len(directory) <= 50 else "..." + directory[-47:]
            self.dest_label.configure(text=display_text)

            # Save the last used folder to settings
            self.settings["last_download_folder"] = directory
            self._save_settings()

    def _start_download(self):
        """Start downloading selected items"""
        if not self.connected:
            return

        # Get selected items
        selected_items = [item.item_data for item in self.file_items if hasattr(item, 'selected') and item.selected]

        if not selected_items:
            messagebox.showinfo("Info", "Please select files or folders to download")
            return

        # Convert to (path, is_dir) tuples
        items_to_download = [(item.path, item.is_dir) for item in selected_items]

        # Confirm if many items
        if len(items_to_download) > 10:
            if not messagebox.askyesno("Confirm", f"Download {len(items_to_download)} items?"):
                return

        # Start download in background
        def download_thread():
            """
            Background thread that prepares and initiates file downloads

            This thread:
            1. Recursively expands any selected directories
            2. Creates the local directory structure
            3. Initiates individual file downloads
            """
            try:
                files_to_download = []

                # Expand directories recursively to get all files
                for path, is_dir in items_to_download:
                    if is_dir:
                        # Directory: get all files inside recursively
                        recursive_files = self.ftp.list_files_recursive(path)
                        files_to_download.extend(recursive_files)
                    else:
                        # Single file: add directly
                        name = os.path.basename(path)
                        size = self.ftp.get_file_size(path)
                        files_to_download.append(FileInfo(name, path, size, False, ""))

                # Download each file
                for file_info in files_to_download:
                    # Skip if already downloading
                    if file_info.path in self.active_downloads:
                        continue

                    # Preserve directory structure in local destination
                    relative_path = os.path.relpath(file_info.path, self.current_path)
                    local_path = os.path.join(self.download_destination, relative_path)
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)

                    self._download_file(file_info, local_path)

            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", f"Download failed: {msg}"))

        threading.Thread(target=download_thread, daemon=True).start()

    def _download_file(self, file_info: FileInfo, local_path: str):
        """Download a single file"""
        download_id = file_info.path
        num_connections = self.connections_var.get()

        # Create a dedicated FTP instance for this download
        # This ensures pause/stop controls work independently for each file
        # Get speed limit from current settings
        try:
            max_speed = float(self.speed_limit_var.get())
            max_speed = max_speed if max_speed > 0 else None
        except (ValueError, AttributeError):
            max_speed = None

        dedicated_ftp = MultiConnectionFTP(
            self.ftp.host,
            self.ftp.user,
            self.ftp.password,
            self.ftp.port,
            self.ftp.use_ssl,
            max_speed
        )

        # Initialize tracking
        self.active_downloads[download_id] = {
            "name": file_info.name,
            "path": file_info.path,
            "local_path": local_path,
            "size": file_info.size,
            "progress": [0] * num_connections,
            "speeds": [0.0] * num_connections,
            "start_time": time.time(),
            "status": "downloading",
            "last_update": time.time(),
            "ftp_instance": dedicated_ftp,  # Each download has its own FTP instance
            "speed_history": [],  # List of (timestamp, total_speed_mbps) tuples
            "max_history_duration": 120,  # Keep last 120 seconds of history
            "checksum": None,  # Will be calculated after download completes
            "checksum_algorithm": "SHA-256",  # Default algorithm
            "checksum_status": None  # None, "calculating", "verified", "failed"
        }

        # Create download widget
        self._create_download_widget(download_id, file_info, num_connections)

        def progress_callback(thread_id, bytes_downloaded, speed):
            if download_id in self.active_downloads:
                self.active_downloads[download_id]["progress"][thread_id] = bytes_downloaded
                self.active_downloads[download_id]["speeds"][thread_id] = speed
                self.active_downloads[download_id]["last_update"] = time.time()

        def complete_callback(success, message):
            if download_id in self.active_downloads:
                if success:
                    self.active_downloads[download_id]["status"] = "complete"
                    elapsed = time.time() - self.active_downloads[download_id]["start_time"]
                    avg_speed = self.active_downloads[download_id]["size"] / elapsed if elapsed > 0 else 0
                    final_msg = f"✓ Complete! {self._format_size(file_info.size)} • Avg: {self._format_speed(avg_speed)}"
                    self.root.after(0, lambda msg=final_msg: self._update_download_status(download_id, msg, "complete"))

                    # Calculate checksum in background
                    threading.Thread(
                        target=self._calculate_checksum_async,
                        args=(download_id,),
                        daemon=True
                    ).start()
                else:
                    self.active_downloads[download_id]["status"] = "error"
                    error_msg = f"✗ Error: {message}"
                    self.root.after(0, lambda msg=error_msg: self._update_download_status(download_id, msg, "error"))

        # Start download using the dedicated FTP instance
        threading.Thread(
            target=dedicated_ftp.download,
            args=(file_info.path, local_path),
            kwargs={
                "num_connections": num_connections,
                "progress_callback": progress_callback,
                "complete_callback": complete_callback,
                "rotate_interval": self.rotation_var.get()
            },
            daemon=True
        ).start()

    def _create_download_widget(self, download_id, file_info, num_connections):
        """Create a modern download card widget"""
        # Card frame
        card = ctk.CTkFrame(self.downloads_frame, corner_radius=10,
                           fg_color=("#FFFFFF", "#1E1E1E"), border_width=1,
                           border_color=("#CCCCCC", "#444444"))
        card.pack(fill="x", pady=5, padx=5)
        card.grid_columnconfigure(0, weight=1)

        # Filename
        filename_display = file_info.name if len(file_info.name) <= 40 else file_info.name[:37] + "..."
        title = ctk.CTkLabel(card, text=f"📥 {filename_display}",
                           font=ctk.CTkFont(size=11, weight="bold"), anchor="w")
        title.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Progress label
        status = ctk.CTkLabel(card, text=f"Starting... ({num_connections} connections)",
                            font=ctk.CTkFont(size=9), anchor="w", text_color="#00A8E8")
        status.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Bandwidth chart (compact version)
        chart = CompactBandwidthChart(card, width=280, height=80,
                                     fg_color="transparent")
        chart.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Checksum label
        checksum_label = ctk.CTkLabel(card, text="🔒 Checksum will be calculated after download",
                                      font=ctk.CTkFont(size=8), anchor="w", text_color="#888888")
        checksum_label.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Center buttons
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(4, weight=1)

        pause_btn = ctk.CTkButton(btn_frame, text="⏸ Pause", width=90, height=28,
                                  command=lambda: self._toggle_pause_download(download_id))
        pause_btn.grid(row=0, column=1, padx=3)

        stop_btn = ctk.CTkButton(btn_frame, text="⏹ Stop", width=90, height=28,
                                fg_color="#f44336", hover_color="#d32f2f",
                                command=lambda: self._stop_download(download_id))
        stop_btn.grid(row=0, column=2, padx=3)

        clear_btn = ctk.CTkButton(btn_frame, text="🗑 Clear", width=90, height=28,
                                 state="disabled", fg_color="#757575", hover_color="#616161",
                                 command=lambda: self._clear_download(download_id))
        clear_btn.grid(row=0, column=3, padx=3)

        # Store references
        self.download_widgets[download_id] = {
            "card": card,
            "title": title,
            "status": status,
            "chart": chart,
            "checksum_label": checksum_label,
            "pause_btn": pause_btn,
            "stop_btn": stop_btn,
            "clear_btn": clear_btn
        }

    def _toggle_pause_download(self, download_id):
        """Toggle pause/resume"""
        if download_id in self.active_downloads:
            info = self.active_downloads[download_id]
            widgets = self.download_widgets[download_id]

            if info["status"] == "downloading":
                info["ftp_instance"].pause()
                info["status"] = "paused"
                widgets["pause_btn"].configure(text="▶ Resume", fg_color="#FF9800", hover_color="#F57C00")
                widgets["status"].configure(text="⏸ Paused", text_color="#FF6B35")

            elif info["status"] == "paused":
                info["ftp_instance"].resume()
                info["status"] = "downloading"
                widgets["pause_btn"].configure(text="⏸ Pause", fg_color="#1f538d", hover_color="#14375e")

    def _stop_download(self, download_id):
        """Stop download and delete partial file"""
        if download_id in self.active_downloads:
            info = self.active_downloads[download_id]
            if info["status"] in ["downloading", "paused"]:
                info["ftp_instance"].stop()
                info["status"] = "stopped"

                # Delete partial file if it exists
                local_path = info.get("local_path")
                if local_path and os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                    except Exception as e:
                        print(f"Could not delete partial file {local_path}: {e}")

                widgets = self.download_widgets[download_id]
                widgets["status"].configure(text="⏹ Stopped", text_color="#FF6B35")
                widgets["pause_btn"].configure(state="disabled")
                widgets["stop_btn"].configure(state="disabled")
                widgets["clear_btn"].configure(state="normal")

    def _clear_download(self, download_id):
        """Clear download from list and delete partial file if incomplete"""
        # Delete partial file if download was not completed
        if download_id in self.active_downloads:
            info = self.active_downloads[download_id]
            if info["status"] not in ["complete"]:
                local_path = info.get("local_path")
                if local_path and os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                    except Exception as e:
                        print(f"Could not delete partial file {local_path}: {e}")
            del self.active_downloads[download_id]

        if download_id in self.download_widgets:
            self.download_widgets[download_id]["card"].destroy()
            del self.download_widgets[download_id]

    def _calculate_checksum_async(self, download_id):
        """Calculate checksum for downloaded file in background"""
        if download_id not in self.active_downloads:
            return

        info = self.active_downloads[download_id]
        local_path = info.get("local_path")
        algorithm = info.get("checksum_algorithm", "SHA-256")

        if not local_path or not os.path.exists(local_path):
            return

        try:
            # Update status to calculating
            info["checksum_status"] = "calculating"
            self.root.after(0, lambda: self._update_checksum_display(download_id))

            # Calculate checksum
            checksum = ChecksumCalculator.calculate_file_hash(local_path, algorithm)
            info["checksum"] = checksum
            info["checksum_status"] = "verified"

            # Update UI
            self.root.after(0, lambda: self._update_checksum_display(download_id))

        except Exception as e:
            print(f"Checksum calculation failed: {e}")
            info["checksum_status"] = "failed"
            info["checksum"] = f"Error: {str(e)}"
            self.root.after(0, lambda: self._update_checksum_display(download_id))

    def _update_checksum_display(self, download_id):
        """Update checksum display in download widget"""
        if download_id not in self.download_widgets or download_id not in self.active_downloads:
            return

        widgets = self.download_widgets[download_id]
        info = self.active_downloads[download_id]

        if "checksum_label" not in widgets:
            return

        checksum = info.get("checksum")
        status = info.get("checksum_status")
        algorithm = info.get("checksum_algorithm", "SHA-256")

        if status == "calculating":
            widgets["checksum_label"].configure(
                text=f"🔒 Calculating {algorithm}...",
                text_color="#FFA500"
            )
        elif status == "verified" and checksum:
            # Truncate checksum for display
            display_hash = checksum[:16] + "..." if len(checksum) > 16 else checksum
            widgets["checksum_label"].configure(
                text=f"🔒 {algorithm}: {display_hash}",
                text_color="#4CAF50"
            )
        elif status == "failed":
            widgets["checksum_label"].configure(
                text=f"🔒 {algorithm}: Calculation failed",
                text_color="#f44336"
            )

    def _update_download_status(self, download_id, text, status):
        """Update download status"""
        if download_id not in self.download_widgets:
            return

        widgets = self.download_widgets[download_id]
        widgets["status"].configure(text=text)

        # Update bandwidth chart if downloading
        if status == "downloading" and download_id in self.active_downloads:
            speed_history = self.active_downloads[download_id].get("speed_history", [])
            if "chart" in widgets:
                widgets["chart"].update(speed_history)

        # Color coding
        if status == "complete":
            widgets["status"].configure(text_color="#00D084")
            widgets["pause_btn"].configure(state="disabled")
            widgets["stop_btn"].configure(state="disabled")
            widgets["clear_btn"].configure(state="normal")
            # Clear chart on completion
            if "chart" in widgets:
                widgets["chart"].clear()
        elif status == "error":
            widgets["status"].configure(text_color="#E63946")
            widgets["pause_btn"].configure(state="disabled")
            widgets["stop_btn"].configure(state="disabled")
            widgets["clear_btn"].configure(state="normal")
            # Clear chart on error
            if "chart" in widgets:
                widgets["chart"].clear()
        elif status == "downloading":
            widgets["status"].configure(text_color="#00A8E8")
        elif status == "paused":
            widgets["status"].configure(text_color="#FF6B35")

    def _update_progress_display(self):
        """
        Update all download progress displays

        Called every 500ms to refresh download statistics including:
        - Progress percentage
        - Download speed
        - ETA (estimated time remaining)
        - Active connection count
        """
        if not self.active_downloads:
            return

        total_downloads = 0
        total_speed_all = 0

        for download_id, info in list(self.active_downloads.items()):
            if info["status"] == "paused":
                total_bytes = sum(info["progress"])
                percentage = (total_bytes / info["size"] * 100) if info["size"] > 0 else 0
                status_line = f"⏸ Paused • {percentage:.1f}% • {self._format_size(total_bytes)}/{self._format_size(info['size'])}"
                self._update_download_status(download_id, status_line, "paused")
                continue

            if info["status"] != "downloading":
                continue

            # Calculate stats
            total_bytes = sum(info["progress"])
            total_speed = sum(info["speeds"])
            elapsed = time.time() - info["start_time"]
            percentage = (total_bytes / info["size"] * 100) if info["size"] > 0 else 0
            remaining = info["size"] - total_bytes
            eta = remaining / total_speed if total_speed > 0 else 0
            active_conns = sum(1 for s in info["speeds"] if s > 0)

            # Update speed history for bandwidth graphs
            current_time = time.time()
            speed_mbps = total_speed / (1024 * 1024)  # Convert bytes/s to MB/s
            info["speed_history"].append((current_time, speed_mbps))

            # Clean up old history entries (keep only last max_history_duration seconds)
            cutoff_time = current_time - info["max_history_duration"]
            info["speed_history"] = [(t, s) for t, s in info["speed_history"] if t >= cutoff_time]

            # Modern status line
            status_line = (
                f"{percentage:.1f}% • {self._format_size(total_bytes)}/{self._format_size(info['size'])} • "
                f"⚡ {self._format_speed(total_speed)} ({active_conns}/{len(info['speeds'])}) • "
                f"⏱ {int(elapsed)}s • ETA: {int(eta)}s"
            )

            self._update_download_status(download_id, status_line, "downloading")

            total_downloads += 1
            total_speed_all += total_speed

        if total_downloads > 0:
            self._update_status(f"🟢 Connected • {total_downloads} active download(s) • ⚡ {self._format_speed(total_speed_all)}")

    # Utility methods

    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def _format_speed(self, speed_bps: float) -> str:
        """Format speed"""
        speed_mbps = speed_bps / (1024 * 1024)
        return f"{speed_mbps:.1f} MB/s"

    def _update_status(self, message: str):
        """Update status bar"""
        self.status_label.configure(text=message)

    def _schedule_update(self):
        """Schedule periodic updates"""
        self._update_progress_display()
        self.root.after(500, self._schedule_update)

    def run(self):
        """Run the application"""
        self.root.mainloop()
