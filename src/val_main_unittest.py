import unittest
from PyQt5.QtWidgets import QApplication
from val import Val

class TestVal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.browser = Val()

    def test_initial_home_url(self):
        self.assertEqual(self.browser.home_url, 'https://www.google.com')

    def test_add_new_tab(self):
        initial_tab_count = self.browser.tab_widget.count()
        self.browser.add_new_tab('https://www.example.com')
        self.assertEqual(self.browser.tab_widget.count(), initial_tab_count + 1)

    def test_navigate_to_url(self):
        self.browser.url_bar.setText('https://www.example.com')
        self.browser.navigate_to_url()
        self.assertEqual(self.browser.browser.url().toString(), 'https://www.example.com')

    def test_go_home(self):
        self.browser.go_home()
        self.assertEqual(self.browser.browser.url().toString(), self.browser.home_url)

    def test_add_bookmark(self):
        self.browser.browser.setUrl(QUrl('https://www.example.com'))
        self.browser.add_bookmark()
        self.assertIn('https://www.example.com', self.browser.bookmarks)

    def test_toggle_private_browsing(self):
        initial_state = self.browser.is_private_browsing
        self.browser.toggle_private_browsing()
        self.assertNotEqual(self.browser.is_private_browsing, initial_state)

    def test_set_homepage(self):
        self.browser.set_homepage()
        self.assertEqual(self.browser.home_url, 'https://www.example.com')

    def test_update_status_bar(self):
        url = QUrl('https://www.example.com')
        self.browser.update_status_bar(url)
        self.assertEqual(self.browser.status_bar.currentMessage(), url.toString())

    def test_show_loading_status(self):
        self.browser.show_loading_status()
        self.assertEqual(self.browser.status_bar.currentMessage(), "Loading...")

    def test_show_ready_status(self):
        self.browser.show_ready_status()
        self.assertEqual(self.browser.status_bar.currentMessage(), "Ready")

    def test_update_sidebar(self):
        self.browser.bookmarks = ['https://www.example.com']
        self.browser.history = ['https://www.example.com']
        self.browser.update_sidebar()
        self.assertIn('https://www.example.com', [self.browser.sidebar_widget.item(i).text() for i in range(self.browser.sidebar_widget.count())])

if __name__ == '__main__':
    unittest.main()