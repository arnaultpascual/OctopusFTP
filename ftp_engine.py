"""
🐙 OctopusFTP Engine - Multi-connection FTP/FTPS download logic with connection rotation
"""

import ftplib
import os
import threading
import time
import random
import ssl
from typing import Callable, Optional, List, Tuple, Dict
from dataclasses import dataclass


class SessionReuseFTP_TLS(ftplib.FTP_TLS):
    """
    FTP_TLS subclass that reuses SSL sessions (required by some servers)

    Many FTPS servers require SSL session reuse for security reasons.
    This class ensures that data connections reuse the SSL session from
    the control connection, preventing "TLS session reuse required" errors.
    """

    def ntransfercmd(self, cmd, rest=None):
        """
        Override to reuse SSL session for data connection

        This method is called before establishing a data connection.
        We extract the SSL session from the control connection and
        apply it to the new data connection, ensuring session continuity.
        """
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            # Get the session from the control connection
            session = self.sock.session
            # Wrap the data connection with SSL using the SAME context and session
            # This prevents "TLS session reuse required" errors from strict FTPS servers
            conn = self.context.wrap_socket(conn,
                                           server_hostname=self.host,
                                           session=session)
        return conn, size


@dataclass
class FileInfo:
    """Information about a remote file"""
    name: str
    path: str
    size: int
    is_dir: bool
    modified: str


class MultiConnectionFTP:
    """Multi-connection FTP downloader with connection rotation"""

    def __init__(self, host: str, user: str, password: str, port: int = 21, use_ssl: bool = False):
        """
        Initialize FTP connection parameters

        Args:
            host: FTP server hostname
            user: Username
            password: Password
            port: FTP port (default 21)
            use_ssl: Use FTPS (FTP over SSL/TLS)
        """
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self._stop_flag = threading.Event()
        self._pause_flag = threading.Event()
        self._active_threads = []

    def _create_connection(self) -> ftplib.FTP:
        """Create and return a new FTP connection"""
        try:
            if self.use_ssl:
                ftp = SessionReuseFTP_TLS()  # Use custom class with SSL session reuse
            else:
                ftp = ftplib.FTP()

            print(f"[DEBUG] Connecting to {self.host}:{self.port}...")
            ftp.connect(self.host, self.port, timeout=30)

            print(f"[DEBUG] Logging in as {self.user}...")
            ftp.login(self.user, self.password)

            # Enable passive mode BEFORE prot_p (some servers require this order)
            ftp.set_pasv(True)
            print(f"[DEBUG] Passive mode enabled")

            if self.use_ssl:
                # Try encrypted data channel first, fallback to clear if it fails
                try:
                    ftp.prot_p()  # Enable encrypted data connection
                    print(f"[DEBUG] Data channel encryption enabled (PROT P)")
                except Exception as prot_ex:
                    print(f"[DEBUG] PROT P failed ({prot_ex}), trying clear data channel...")
                    try:
                        ftp.prot_c()  # Use clear text data channel
                        print(f"[DEBUG] Using clear text data channel (PROT C)")
                    except Exception as prot_c_ex:
                        print(f"[DEBUG] PROT C also failed: {prot_c_ex}")
                        # Continue anyway, some servers work without explicit PROT command

            # Set binary mode
            ftp.sendcmd('TYPE I')
            print(f"[DEBUG] Binary mode set")

            return ftp
        except Exception as e:
            print(f"[DEBUG] Connection failed: {e}")
            raise ConnectionError(f"Failed to connect to FTP server: {e}")

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test the FTP connection

        Returns:
            Tuple of (success, message)
        """
        try:
            ftp = self._create_connection()
            welcome = ftp.getwelcome()
            ftp.quit()
            return True, f"Connected successfully: {welcome}"
        except Exception as e:
            return False, str(e)

    def list_directory(self, remote_path: str = '/') -> List[FileInfo]:
        """
        List files and directories in the remote path

        Args:
            remote_path: Remote directory path

        Returns:
            List of FileInfo objects
        """
        ftp = None
        try:
            ftp = self._create_connection()

            # Get current directory for debugging
            try:
                current_dir = ftp.pwd()
                print(f"[DEBUG] Current directory: {current_dir}")
            except Exception as pwd_ex:
                print(f"[DEBUG] Failed to get PWD: {pwd_ex}")

            # Change to target directory
            try:
                ftp.cwd(remote_path)
                print(f"[DEBUG] Changed to directory: {remote_path}")
            except Exception as cwd_ex:
                if ftp:
                    try:
                        ftp.quit()
                    except:
                        pass  # Connection might already be closed
                raise ValueError(f"Cannot access directory '{remote_path}': {cwd_ex}")

            items = []

            # Try MLSD first (more reliable)
            mlsd_failed = False
            mlsd_error = None
            try:
                print(f"[DEBUG] Trying MLSD...")
                for name, facts in ftp.mlsd():
                    if name in ['.', '..']:
                        continue

                    is_dir = facts.get('type', '') == 'dir'
                    size = int(facts.get('size', 0))
                    modified = facts.get('modify', '')

                    items.append(FileInfo(
                        name=name,
                        path=os.path.join(remote_path, name).replace('\\', '/'),
                        size=size,
                        is_dir=is_dir,
                        modified=modified
                    ))
                print(f"[DEBUG] MLSD succeeded, found {len(items)} items")
            except Exception as mlsd_ex:
                # Fallback to LIST parsing
                print(f"[DEBUG] MLSD failed: {mlsd_ex}")
                mlsd_failed = True
                mlsd_error = mlsd_ex
                lines = []
                try:
                    print(f"[DEBUG] Trying LIST...")
                    ftp.dir(lines.append)
                    print(f"[DEBUG] LIST returned {len(lines)} lines")
                except Exception as list_ex:
                    if ftp:
                        try:
                            ftp.quit()
                        except:
                            pass  # Connection might already be closed
                    raise RuntimeError(f"Both MLSD and LIST failed. MLSD: {mlsd_ex}, LIST: {list_ex}")

                if len(lines) == 0:
                    print(f"[DEBUG] Warning: LIST returned no lines")

                for line in lines:
                    parts = line.split(None, 8)
                    if len(parts) < 9:
                        continue

                    permissions = parts[0]
                    size = int(parts[4]) if parts[4].isdigit() else 0
                    name = parts[8]

                    if name in ['.', '..']:
                        continue

                    is_dir = permissions.startswith('d')
                    modified = ' '.join(parts[5:8])

                    items.append(FileInfo(
                        name=name,
                        path=os.path.join(remote_path, name).replace('\\', '/'),
                        size=size,
                        is_dir=is_dir,
                        modified=modified
                    ))

            if ftp:
                try:
                    ftp.quit()
                    print(f"[DEBUG] Connection closed cleanly")
                except Exception as quit_ex:
                    print(f"[DEBUG] Error closing connection: {quit_ex}")
                    pass  # Connection might already be closed

            print(f"[DEBUG] Successfully listed directory, returning {len(items)} items")
            return items

        except Exception as e:
            print(f"[DEBUG] Exception in list_directory: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            if ftp:
                try:
                    ftp.quit()
                except:
                    pass
            raise RuntimeError(f"Failed to list directory: {type(e).__name__}: {e}")

    def list_files_recursive(self, remote_path: str) -> List[FileInfo]:
        """
        Recursively list all files in a directory

        Args:
            remote_path: Remote directory path

        Returns:
            List of FileInfo objects (files only, no directories)
        """
        all_files = []

        try:
            items = self.list_directory(remote_path)

            for item in items:
                if item.is_dir:
                    # Recursively get files from subdirectory
                    all_files.extend(self.list_files_recursive(item.path))
                else:
                    all_files.append(item)

            return all_files

        except Exception as e:
            raise RuntimeError(f"Failed to list files recursively: {e}")

    def get_file_size(self, remote_file: str) -> int:
        """
        Get the size of a remote file

        Args:
            remote_file: Remote file path

        Returns:
            File size in bytes
        """
        try:
            ftp = self._create_connection()
            size = ftp.size(remote_file)
            ftp.quit()
            return size
        except Exception as e:
            raise RuntimeError(f"Failed to get file size: {e}")

    def download_chunk(
        self,
        remote_file: str,
        start: int,
        end: int,
        chunk_file: str,
        thread_id: int,
        progress_callback: Optional[Callable[[int, int, float], None]] = None,
        rotate_interval: int = 30
    ):
        """
        Download a chunk of a file with connection rotation

        This method downloads a specific byte range of a file using multiple
        short-lived connections that are rotated at regular intervals. This helps
        avoid server-side connection timeouts and bandwidth throttling.

        Args:
            remote_file: Remote file path
            start: Start byte position
            end: End byte position
            chunk_file: Local chunk file path
            thread_id: Thread identifier
            progress_callback: Callback function(thread_id, bytes_downloaded, speed)
            rotate_interval: Seconds before rotating connection (default 30s)

        Flow:
            1. Create new FTP connection
            2. Resume from current position using REST command
            3. Download data for up to rotate_interval seconds
            4. Close connection and create a new one
            5. Repeat until chunk is complete
        """
        bytes_downloaded = 0
        current_position = start
        chunk_size = end - start

        try:
            with open(chunk_file, 'wb') as f:
                while current_position < end and not self._stop_flag.is_set():
                    # Create new connection
                    ftp = self._create_connection()

                    # Random delay to appear natural
                    time.sleep(random.uniform(0.1, 0.5))

                    # Resume from current position
                    ftp.sendcmd(f'REST {current_position}')

                    rotation_start = time.time()
                    chunk_start_time = time.time()
                    chunk_bytes = 0

                    def write_callback(data):
                        """
                        Callback function invoked for each chunk of data received

                        This function handles:
                        - Pause/resume functionality
                        - Connection rotation timing
                        - Progress tracking and speed calculation
                        - Byte range boundary enforcement
                        """
                        nonlocal current_position, bytes_downloaded, chunk_bytes

                        # Check pause flag - wait while paused
                        while self._pause_flag.is_set():
                            if self._stop_flag.is_set():
                                raise StopIteration("Download stopped")
                            time.sleep(0.1)  # Check every 100ms

                        # Check if we should rotate connection
                        # This prevents timeouts and can help avoid bandwidth throttling
                        elapsed = time.time() - rotation_start
                        if elapsed >= rotate_interval:
                            raise StopIteration("Time to rotate connection")

                        # Check stop flag
                        if self._stop_flag.is_set():
                            raise StopIteration("Download stopped")

                        # Don't write beyond end position
                        # Each thread is responsible for a specific byte range
                        remaining = end - current_position
                        if remaining <= 0:
                            raise StopIteration("Chunk complete")

                        data_to_write = data[:remaining]
                        f.write(data_to_write)

                        written = len(data_to_write)
                        current_position += written
                        bytes_downloaded += written
                        chunk_bytes += written

                        # Calculate speed and report progress
                        if progress_callback:
                            chunk_elapsed = time.time() - chunk_start_time
                            speed = chunk_bytes / chunk_elapsed if chunk_elapsed > 0 else 0
                            progress_callback(thread_id, bytes_downloaded, speed)

                    try:
                        # Start retrieval
                        ftp.retrbinary(f'RETR {remote_file}', write_callback, blocksize=8192)
                    except StopIteration:
                        pass  # Normal rotation or completion
                    except Exception as e:
                        if "Time to rotate" not in str(e):
                            raise
                    finally:
                        try:
                            ftp.quit()
                        except:
                            pass

                    # Check if chunk is complete
                    if current_position >= end:
                        break

        except Exception as e:
            if not self._stop_flag.is_set():
                raise RuntimeError(f"Thread {thread_id} failed: {e}")

    def download(
        self,
        remote_file: str,
        local_file: str,
        num_connections: int = 4,
        progress_callback: Optional[Callable[[int, int, float], None]] = None,
        complete_callback: Optional[Callable[[bool, str], None]] = None,
        rotate_interval: int = 30
    ):
        """
        Download a file using multiple parallel connections with connection rotation

        This is the main download method that orchestrates multi-threaded downloads.
        The file is split into equal chunks, each downloaded by a separate thread
        with its own FTP connection. Connections are rotated at regular intervals.

        Args:
            remote_file: Remote file path
            local_file: Local file path
            num_connections: Number of parallel connections (default 4)
            progress_callback: Callback function(thread_id, bytes_downloaded, speed)
            complete_callback: Callback function(success, message)
            rotate_interval: Seconds before rotating connections (default 30s)

        Process:
            1. Get remote file size
            2. Split file into equal chunks
            3. Create download threads (one per chunk)
            4. Wait for all threads to complete
            5. Reassemble chunks into final file
            6. Clean up temporary chunk files
        """
        self._stop_flag.clear()
        self._pause_flag.clear()

        try:
            # Get file size
            file_size = self.get_file_size(remote_file)

            if file_size == 0:
                raise ValueError("Remote file is empty or size unavailable")

            # Calculate chunk size
            chunk_size = file_size // num_connections

            # Create chunk files
            chunk_files = []
            threads = []

            for i in range(num_connections):
                start = i * chunk_size
                end = file_size if i == num_connections - 1 else (i + 1) * chunk_size
                chunk_file = f"{local_file}.part{i}"
                chunk_files.append(chunk_file)

                # Create thread
                thread = threading.Thread(
                    target=self.download_chunk,
                    args=(remote_file, start, end, chunk_file, i, progress_callback, rotate_interval)
                )
                thread.daemon = True
                threads.append(thread)
                self._active_threads.append(thread)

            # Start all threads
            for thread in threads:
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Check if stopped
            if self._stop_flag.is_set():
                if complete_callback:
                    complete_callback(False, "Download cancelled")
                return

            # Reassemble file
            with open(local_file, 'wb') as outfile:
                for chunk_file in chunk_files:
                    if os.path.exists(chunk_file):
                        with open(chunk_file, 'rb') as infile:
                            outfile.write(infile.read())
                        os.remove(chunk_file)

            if complete_callback:
                complete_callback(True, f"Downloaded successfully: {local_file}")

        except Exception as e:
            # Clean up chunk files
            for i in range(num_connections):
                chunk_file = f"{local_file}.part{i}"
                if os.path.exists(chunk_file):
                    try:
                        os.remove(chunk_file)
                    except:
                        pass

            if complete_callback:
                complete_callback(False, f"Download failed: {e}")
        finally:
            self._active_threads.clear()

    def pause(self):
        """Pause all active downloads"""
        self._pause_flag.set()

    def resume(self):
        """Resume all paused downloads"""
        self._pause_flag.clear()

    def is_paused(self):
        """Check if downloads are paused"""
        return self._pause_flag.is_set()

    def stop(self):
        """Stop all active downloads"""
        self._stop_flag.set()
        self._pause_flag.clear()  # Clear pause flag to prevent deadlock

        # Wait for threads to finish
        for thread in self._active_threads:
            if thread.is_alive():
                thread.join(timeout=2)
