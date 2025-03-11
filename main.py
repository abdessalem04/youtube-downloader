import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar,
                             QFileDialog, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import yt_dlp

class DownloaderThread(QThread):
    progress_signal = pyqtSignal(float, str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url, output_path, format_option, quality_option, audio_only):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_option = format_option
        self.quality_option = quality_option
        self.audio_only = audio_only
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            p = p.replace('%', '')
            try:
                percentage = float(p)
                self.progress_signal.emit(percentage, d.get('_eta_str', ''))
            except:
                pass
        elif d['status'] == 'finished':
            self.progress_signal.emit(100, 'Finalizing...')
    
    def run(self):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'no_warnings': False,
                'quiet': False,
                'verbose': False,
                'geo_bypass': True,
                'extractor_retries': 5,
                'socket_timeout': 30,
                'force_generic_extractor': False,
                'cookiefile': None,
            }
            
            if self.audio_only:
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                # Video format selection
                if self.format_option == 'mp4':
                    format_str = 'mp4'
                elif self.format_option == 'flv':
                    format_str = 'flv'
                elif self.format_option == 'avi':
                    format_str = 'avi'
                else:  # Default to mp4
                    format_str = 'mp4'
                
                # Quality selection
                if self.quality_option == '4K':
                    quality_str = '2160'
                elif self.quality_option == '1080p':
                    quality_str = '1080'
                elif self.quality_option == '720p':
                    quality_str = '720'
                elif self.quality_option == '480p':
                    quality_str = '480'
                else:  # Default to best
                    quality_str = 'best'
                
                # Use more reliable format selection that's less likely to be blocked
                if quality_str == 'best':
                    ydl_opts['format'] = f'best[ext={format_str}]/best'
                else:
                    ydl_opts['format'] = f'bestvideo[height<={quality_str}]+bestaudio/best[height<={quality_str}]/best'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                filename = ydl.prepare_filename(info)
                self.finished_signal.emit(filename)
                
        except Exception as e:
            self.error_signal.emit(str(e))

class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(100, 100, 600, 400)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel('YouTube URL:')
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_label = QLabel('Format:')
        self.format_combo = QComboBox()
        self.format_combo.addItems(['mp4', 'flv', 'avi'])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        main_layout.addLayout(format_layout)
        
        # Quality selection
        quality_layout = QHBoxLayout()
        quality_label = QLabel('Quality:')
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(['Best', '4K', '1080p', '720p', '480p'])
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        main_layout.addLayout(quality_layout)
        
        # Audio only option
        audio_layout = QHBoxLayout()
        self.audio_only = QCheckBox('Audio Only (MP3)')
        audio_layout.addWidget(self.audio_only)
        main_layout.addLayout(audio_layout)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        output_label = QLabel('Save to:')
        self.output_path = QLineEdit()
        self.output_path.setText(os.path.expanduser('~/Downloads'))
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_output)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(browse_button)
        main_layout.addLayout(output_layout)
        
        # Progress bar
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_label = QLabel('Ready')
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        main_layout.addLayout(progress_layout)
        
        # Download button
        self.download_button = QPushButton('Download')
        self.download_button.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_button)
        
        # Set the main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Initialize downloader thread
        self.downloader_thread = None
    
    def browse_output(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if directory:
            self.output_path.setText(directory)
    
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, 'Error', 'Please enter a YouTube URL')
            return
        
        output_path = self.output_path.text()
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not create output directory: {str(e)}')
                return
        
        format_option = self.format_combo.currentText()
        quality_option = self.quality_combo.currentText()
        audio_only = self.audio_only.isChecked()
        
        # Disable UI elements during download
        self.download_button.setEnabled(False)
        self.url_input.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.quality_combo.setEnabled(False)
        self.audio_only.setEnabled(False)
        self.output_path.setEnabled(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_label.setText('Starting download...')
        
        # Create and start the downloader thread
        self.downloader_thread = DownloaderThread(
            url, output_path, format_option, quality_option, audio_only
        )
        self.downloader_thread.progress_signal.connect(self.update_progress)
        self.downloader_thread.finished_signal.connect(self.download_finished)
        self.downloader_thread.error_signal.connect(self.download_error)
        self.downloader_thread.start()
    
    def update_progress(self, percentage, eta):
        self.progress_bar.setValue(int(percentage))
        if eta:
            self.progress_label.setText(f'Downloading... ETA: {eta}')
        else:
            self.progress_label.setText('Downloading...')
    
    def download_finished(self, filename):
        self.progress_bar.setValue(100)
        self.progress_label.setText('Download complete!')
        QMessageBox.information(self, 'Success', f'Download completed successfully!\nSaved to: {filename}')
        self.reset_ui()
    
    def download_error(self, error_message):
        self.progress_label.setText('Error occurred')
        QMessageBox.critical(self, 'Error', f'Download failed: {error_message}')
        self.reset_ui()
    
    def reset_ui(self):
        # Re-enable UI elements
        self.download_button.setEnabled(True)
        self.url_input.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.quality_combo.setEnabled(True)
        self.audio_only.setEnabled(True)
        self.output_path.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()