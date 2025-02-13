# Copyright 2025 the Val authors
# This project is governed under the GNU General Public License, v2.0. See in the LICENSE file.

#imports
import sys
import requests
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QHBoxLayout, QTabWidget, QAction, QMessageBox, QMenuBar, QInputDialog, QRadioButton, QDialog, QProgressBar, QStatusBar, QDockWidget, QListWidget, QLabel, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl, Qt, QTimer, QEventLoop, QThread
from PyQt5.QtGui import QIcon
from datetime import datetime, time

class Val(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Orange Valium')
        self.setGeometry(100, 100, 1200, 800)
        self.browser = QWebEngineView(self)
        self.theme = 'light'
        self.set_style(self.theme)
        self.channel = 'stable'
        self.set_channel(self.channel)
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Nav 
        self.nav_bar = QWidget(self)
        self.nav_layout = QHBoxLayout(self.nav_bar)
        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText("Enter a URL and hit Enter...")
        self.url_bar.setFixedHeight(35) # See here: https://github.com/owgydz/valium/issues/3
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_layout.addWidget(self.url_bar)

        # Icons
        icon_dir = os.path.join(os.path.dirname(__file__), 'icons')
        back_icon = QIcon(os.path.join(icon_dir, 'back.png'))
        forward_icon = QIcon(os.path.join(icon_dir, 'forward.png'))
        refresh_icon = QIcon(os.path.join(icon_dir, 'refresh.png'))
        home_icon = QIcon(os.path.join(icon_dir, 'home.png'))

        self.back_button = QPushButton(back_icon, "")
        self.forward_button = QPushButton(forward_icon, "")
        self.refresh_button = QPushButton(refresh_icon, "")
        self.home_button = QPushButton(home_icon, "")

        self.back_button.setToolTip("Go Back")
        self.forward_button.setToolTip("Go Forward")
        self.refresh_button.setToolTip("Refresh Page")
        self.home_button.setToolTip("Go Home")

        self.nav_layout.addWidget(self.back_button)
        self.nav_layout.addWidget(self.forward_button)
        self.nav_layout.addWidget(self.refresh_button)
        self.nav_layout.addWidget(self.home_button)

        self.layout.addWidget(self.nav_bar)

        # Create a tab widget for multiple tabs
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.tabBarDoubleClicked.connect(self.pin_tab)
        self.tab_widget.currentChanged.connect(self.update_url_bar)
        self.layout.addWidget(self.tab_widget)

        # Default home URL
        self.home_url = 'https://www.google.com'

        # Connect button signals AFTER initializing self.browser
        self.back_button.clicked.connect(lambda: self.browser.back())
        self.forward_button.clicked.connect(lambda: self.browser.forward())
        self.refresh_button.clicked.connect(lambda: self.browser.reload())
        self.home_button.clicked.connect(self.go_home)

        # Bookmarks, history, private browsing
        self.bookmarks = []
        self.history = []
        self.is_private_browsing = False

        # First tab
        self.add_new_tab(self.home_url)

        # Set up menu
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('File')
        self.bookmarks_menu = self.menu_bar.addMenu('Bookmarks')
        self.history_menu = self.menu_bar.addMenu('History')
        self.settings_menu = self.menu_bar.addMenu('Settings')
        self.help_menu = self.menu_bar.addMenu('Help')

        # Actions for menu items
        self.add_bookmark_action = QAction('Add Bookmark', self)
        self.add_bookmark_action.triggered.connect(self.add_bookmark)
        self.bookmarks_menu.addAction(self.add_bookmark_action)

        self.view_bookmarks_action = QAction('View Bookmarks', self)
        self.view_bookmarks_action.triggered.connect(self.view_bookmarks)
        self.bookmarks_menu.addAction(self.view_bookmarks_action)

        self.view_history_action = QAction('View History', self)
        self.view_history_action.triggered.connect(self.view_history)
        self.history_menu.addAction(self.view_history_action)

        self.set_homepage_action = QAction('Set Homepage', self)
        self.set_homepage_action.triggered.connect(self.set_homepage)
        self.settings_menu.addAction(self.set_homepage_action)

        self.toggle_private_browsing_action = QAction('Toggle Private Browsing', self)
        self.toggle_private_browsing_action.triggered.connect(self.toggle_private_browsing)
        self.settings_menu.addAction(self.toggle_private_browsing_action)

        # Add Theme Customization action
        self.theme_customization_action = QAction('Change Theme', self)
        self.theme_customization_action.triggered.connect(self.change_theme)
        self.settings_menu.addAction(self.theme_customization_action)

        # Version info action
        self.version_info_action = QAction('Version Info', self)
        self.version_info_action.triggered.connect(self.show_version_info)
        self.help_menu.addAction(self.version_info_action)

        # Auto version checking
        self.check_for_updates_action = QAction('Check for Updates', self)
        self.check_for_updates_action.triggered.connect(self.check_for_updates)
        self.help_menu.addAction(self.check_for_updates_action)

        # Download manager action
        self.download_manager_action = QAction('Download Manager', self)
        self.download_manager_action.triggered.connect(self.open_download_manager)
        self.file_menu.addAction(self.download_manager_action)

        # Channel selection action
        self.channel_selection_action = QAction('Select Channel', self)
        self.channel_selection_action.triggered.connect(self.select_channel)
        self.settings_menu.addAction(self.channel_selection_action)

        # Dark Mode Scheduling
        self.dark_mode_timer = QTimer(self)
        self.dark_mode_timer.timeout.connect(self.check_dark_mode_schedule)
        self.dark_mode_timer.start(60000)  # Check every minute

        # Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.browser.urlChanged.connect(self.update_status_bar)
        self.browser.loadStarted.connect(self.show_loading_status)
        self.browser.loadFinished.connect(self.show_ready_status)

        # Sidebar for Bookmarks and History
        self.sidebar = QDockWidget("Bookmarks & History", self)
        self.sidebar.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.sidebar_widget = QListWidget()
        self.sidebar.setWidget(self.sidebar_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)
        self.update_sidebar()

        # Load session if available
        self.load_session()

    def add_new_tab(self, url):
        new_browser = QWebEngineView(self)
        new_browser.setUrl(QUrl(url))

        # Set request interceptor properly
        interceptor = RequestInterceptor()
        new_browser.page().profile().setRequestInterceptor(interceptor)

        new_tab_index = self.tab_widget.addTab(new_browser, 'New Tab')
        self.tab_widget.setCurrentIndex(new_tab_index)
        self.browser = new_browser  # Update active browser

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        self.browser.setUrl(QUrl(url))
        if not self.is_private_browsing:
            self.history.append(url)
        self.update_sidebar()

    def go_home(self):
        self.browser.setUrl(QUrl(self.home_url))

    def close_tab(self, index):
        self.tab_widget.removeTab(index)

    def pin_tab(self, index):
        if self.tab_widget.tabText(index) != "Pinned":
            self.tab_widget.setTabText(index, "Pinned")
        else:
            self.tab_widget.setTabText(index, "New Tab")

    def update_url_bar(self, index):
        current_browser = self.tab_widget.widget(index)
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())

    def update_status_bar(self, url):
        self.status_bar.showMessage(url.toString())

    def show_loading_status(self):
        self.status_bar.showMessage("Loading...")

    def show_ready_status(self):
        self.status_bar.showMessage("Ready")

    def add_bookmark(self):
        url = self.browser.url().toString()
        if url not in self.bookmarks:
            self.bookmarks.append(url)
            QMessageBox.information(self, 'Bookmark Added', f'{url} has been added to your bookmarks.')
        self.update_sidebar()

    def view_bookmarks(self):
        bookmarks_str = "\n".join(self.bookmarks) if self.bookmarks else "No bookmarks available."
        QMessageBox.information(self, 'Bookmarks', bookmarks_str)

    def view_history(self):
        history_str = "\n".join(self.history) if self.history else "No browsing history."
        QMessageBox.information(self, 'History', history_str)

    def set_homepage(self):
        homepage, ok = QInputDialog.getText(self, 'Set Homepage', 'Enter your homepage URL:')
        if ok and homepage:
            self.home_url = homepage
            QMessageBox.information(self, 'Homepage Set', f'Your homepage has been set to {homepage}.')

    def toggle_private_browsing(self):
        self.is_private_browsing = not self.is_private_browsing
        if self.is_private_browsing:
            QMessageBox.information(self, 'Private Browsing', 'Private browsing mode is now ON. History and cookies will not be saved.')
        else:
            QMessageBox.information(self, 'Private Browsing', 'Private browsing mode is now OFF.')

    def check_for_updates(self):
        try:
            response = requests.get(f'https://api.github.com/repos/owgydz/val/releases/latest?channel={self.channel}')
            latest_version = response.json()['tag_name']
            current_version = '14.0.1528.15'

            if latest_version != current_version:
                QMessageBox.information(self, 'Update Available', f'A new version ({latest_version}) is available.')
            else:
                QMessageBox.information(self, 'Up-to-date', 'You are using the latest version.')
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, 'Error', 'Unable to check for updates at the moment.')

    def show_version_info(self):
        QMessageBox.information(self, 'Version', f'Val Browser version: v14.0.1528.15, {self.channel} channel.\nCopyright (c) 2025 the Val Browser authors, under Orange, Inc.')

    def open_download_manager(self):
        self.download_manager_dialog = DownloadManager(self.downloads)
        self.download_manager_dialog.exec_()
  
    def set_style(self, theme):
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow { background-color: #2c2c2c; color: white; }
                QLineEdit { background-color: #4d4d4d; color: white; border: 1px solid #666; }
                QPushButton { background-color: #5c5c5c; color: white; border-radius: 5px; }
                QTabWidget { background-color: #3c3c3c; }
            """)
            if hasattr(self, 'browser') and self.browser:
                self.browser.page().runJavaScript("""
                    document.documentElement.style.backgroundColor = '#2c2c2c';
                    document.documentElement.style.color = 'white';
                    if (document.querySelector('body.ntp')) {
                        document.querySelector('body.ntp').style.backgroundColor = '#2c2c2c';
                        document.querySelector('body.ntp').style.color = 'white';
                    }
                """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: white; color: black; }
                QLineEdit { background-color: #f0f0f0; color: black; border: 1px solid #ccc; }
                QPushButton { background-color: #e0e0e0; color: black; border-radius: 5px; }
                QTabWidget { background-color: #f7f7f7; }
            """)
            if hasattr(self, 'browser') and self.browser:
                self.browser.page().runJavaScript("""
                    document.documentElement.style.backgroundColor = '';
                    document.documentElement.style.color = '';
                    if (document.querySelector('body.ntp')) {
                        document.querySelector('body.ntp').style.backgroundColor = '';
                        document.querySelector('body.ntp').style.color = '';
                    }
                """)

    def change_theme(self):
        dialog = ThemeDialog(self)
        dialog.exec_()

    def check_dark_mode_schedule(self):
        current_time = datetime.now().time()
        if current_time >= time(18, 0) or current_time < time(6, 0):  # Between 6 PM and 6 AM
            self.set_style('dark')
        else:
            self.set_style('light')

    def update_sidebar(self):
        self.sidebar_widget.clear()
        self.sidebar_widget.addItem("Bookmarks:")
        self.sidebar_widget.addItems(self.bookmarks)
        self.sidebar_widget.addItem("History:")
        self.sidebar_widget.addItems(self.history)

    def set_channel(self, channel):
        self.channel = channel
        QMessageBox.information(self, 'Channel Set', f'The channel has been set to {channel}.')

    def select_channel(self):
        dialog = ChannelDialog(self)
        dialog.exec_()

    def save_session(self):
        session = {
            'tabs': [self.tab_widget.widget(i).url().toString() for i in range(self.tab_widget.count())],
            'current_tab': self.tab_widget.currentIndex()
        }
        with open('session.json', 'w') as f:
            json.dump(session, f)

    def load_session(self):
        if os.path.exists('session.json'):
            with open('session.json', 'r') as f:
                session = json.load(f)
                for url in session['tabs']:
                    self.add_new_tab(url)
                self.tab_widget.setCurrentIndex(session['current_tab'])

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Save Session', 'Do you want to save your session?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_session()
        event.accept()

class ThemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Choose your theme')
        self.setGeometry(400, 200, 300, 150)

        self.light_radio = QRadioButton('Light Theme', self)
        self.light_radio.setChecked(True)
        self.dark_radio = QRadioButton('Dark Theme', self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.light_radio)
        layout.addWidget(self.dark_radio)

        button = QPushButton('Apply', self)
        button.clicked.connect(self.apply_theme)
        layout.addWidget(button)

    def apply_theme(self):
        if self.light_radio.isChecked():
            self.parent().set_style('light')
        else:
            self.parent().set_style('dark')
        self.accept()

class ChannelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Channel')
        self.setGeometry(400, 200, 300, 150)

        self.dev_radio = QRadioButton('Dev Channel', self)
        self.beta_radio = QRadioButton('Beta Channel', self)
        self.stable_radio = QRadioButton('Stable Channel', self)
        self.stable_radio.setChecked(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.dev_radio)
        layout.addWidget(self.beta_radio)
        layout.addWidget(self.stable_radio)

        button = QPushButton('Apply', self)
        button.clicked.connect(self.apply_channel)
        layout.addWidget(button)

    def apply_channel(self):
        if self.dev_radio.isChecked():
            self.parent().set_channel('dev')
        elif self.beta_radio.isChecked():
            self.parent().set_channel('beta')
        else:
            self.parent().set_channel('stable')
        self.accept()

class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        if "popup" in url or url.startswith("about:blank"):
            info.block(True)  # Block the request
        else:
            info.block(False)  # Allow the request
class DownloadManager(QDialog):
    def __init__(self, downloads, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Download Manager')
        self.setGeometry(400, 200, 400, 300)
        self.layout = QVBoxLayout(self)

        self.downloads = downloads
        self.progress_bars = {}

        for download in self.downloads:
            progress_bar = QProgressBar(self)
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            self.layout.addWidget(progress_bar)
            self.progress_bars[download['url']] = progress_bar

    def update_progress(self, download):
        progress_bar = self.progress_bars.get(download['url'])
        if progress_bar:
            progress_bar.setValue(download['progress'])

    def add_download(self, url):
        self.downloads.append({'url': url, 'progress': 0})
        self.update_progress(self.downloads[-1])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = Val()
    browser.show()
    sys.exit(app.exec_())
