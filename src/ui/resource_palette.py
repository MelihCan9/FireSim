from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QFrame, QLabel
from src.firefighting.base import ResourceType
from src.firefighting.resources import FireStation, Helicopter, UAV, WaterTanker, WorkMachine

class ResourcePalette(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setup_ui()
        self.selected_resource_type = None
        self.resource_class = None
        self.is_remove_mode = False

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Resources"))
        
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(False)
        
        resource_types = {
            ResourceType.FIRE_STATION: ("Fire Station", FireStation),
            ResourceType.HELICOPTER: ("Helicopter", Helicopter),
            ResourceType.UAV: ("UAV", UAV),
            ResourceType.WATER_TANKER: ("Water Tanker", WaterTanker),
            ResourceType.WORK_MACHINE: ("Work Machine", WorkMachine),
        }

        for resource_type, (label, resource_class) in resource_types.items():
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.resource_type = resource_type
            btn.resource_class = resource_class
            btn.clicked.connect(self.on_button_clicked)
            layout.addWidget(btn)
            self.button_group.addButton(btn)

        # Add separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        # Add remove button
        self.remove_btn = QPushButton("Remove Resource")
        self.remove_btn.setCheckable(True)
        self.remove_btn.clicked.connect(self.on_remove_selected)
        layout.addWidget(self.remove_btn)

        layout.addStretch()
        self.setLayout(layout)

    def on_resource_selected(self, resource_type, resource_class):
        # If clicking the same resource button again, deselect it
        if self.selected_resource_type == resource_type:
            self.selected_resource_type = None
            self.resource_class = None
            # Uncheck the button
            for button in self.button_group.buttons():
                if button.isChecked():
                    button.setChecked(False)
        else:
            self.selected_resource_type = resource_type
            self.resource_class = resource_class
            self.is_remove_mode = False
            self.remove_btn.setChecked(False)

    def on_remove_selected(self, checked):
        if checked:
            self.selected_resource_type = None
            self.resource_class = None
            self.is_remove_mode = True
            # Uncheck any selected resource button
            for button in self.button_group.buttons():
                if button.isChecked():
                    button.setChecked(False)
        else:
            self.is_remove_mode = False 

    def on_button_clicked(self):
        button = self.sender()
        if button.isChecked():
            self.selected_resource_type = button.resource_type
            self.resource_class = button.resource_class
            self.is_remove_mode = False
            self.remove_btn.setChecked(False)
        else:
            self.selected_resource_type = None
            self.resource_class = None