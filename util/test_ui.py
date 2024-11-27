from PyQt5.QtWidgets import QApplication
import sys
from ui.main_window import MainWindow

def test_ui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Basic UI presence tests
    assert window.tabs.count() == 2
    assert window.tabs.tabText(0) == "Map Generation"
    assert window.tabs.tabText(1) == "Simulation"
    
    # Test Map Editor components
    map_editor = window.map_editor
    assert map_editor.cell_info is not None
    
    # Test Simulation components
    simulation = window.simulation
    assert simulation.play_button.text() == "Play"
    assert simulation.pause_button.text() == "Pause"
    assert simulation.step_button.text() == "Step"
    
    print("All basic UI tests passed!")
    return app, window

if __name__ == "__main__":
    app, window = test_ui()
    sys.exit(app.exec_())