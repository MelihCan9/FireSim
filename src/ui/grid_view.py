from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPointF
from PyQt5.QtGui import QColor, QPen, QBrush, QPainter

class GridScene(QGraphicsScene):
    cell_clicked = pyqtSignal(int, int)  # Signal for cell selection
    area_selected = pyqtSignal(list)  # Signal for area selection

    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.cell_size = 30
        self.cell_items = {}
        self.selected_cell = None
        self.selection_rect = None
        self.selection_start = None
        self.setup_grid()

    def mousePressEvent(self, event):
        pos = event.scenePos()
        i = int(pos.y() // self.cell_size)
        j = int(pos.x() // self.cell_size)
        
        # Get grid dimensions
        rows = len(self.grid.cells)
        cols = len(self.grid.cells[0])
        
        if event.button() == Qt.LeftButton:
            # Only select cell if within grid boundaries
            if 0 <= i < rows and 0 <= j < cols:
                self.selection_start = (i, j)
                self.select_cell(i, j)
                self.cell_clicked.emit(i, j)
        elif event.button() == Qt.RightButton:
            # For area selection, store starting point
            self.selection_start = (i, j)

    def mouseMoveEvent(self, event):
        if self.selection_start and event.buttons() == Qt.LeftButton:
            pos = event.scenePos()
            i = int(pos.y() // self.cell_size)
            j = int(pos.x() // self.cell_size)
            self.update_selection_rect(self.selection_start, (i, j))

    def mouseReleaseEvent(self, event):
        if self.selection_start:
            pos = event.scenePos()
            i = int(pos.y() // self.cell_size)
            j = int(pos.x() // self.cell_size)
            self.finalize_selection(self.selection_start, (i, j))
            self.selection_start = None

    def update_selection_rect(self, start, end):
        if self.selection_rect:
            self.removeItem(self.selection_rect)
        
        x1, y1 = start
        x2, y2 = end
        
        # Get grid dimensions
        rows = len(self.grid.cells)
        cols = len(self.grid.cells[0])
        
        # Constrain coordinates to grid bounds
        min_x = max(0, min(x1, x2))
        max_x = min(rows - 1, max(x1, x2))
        min_y = max(0, min(y1, y2))
        max_y = min(cols - 1, max(y1, y2))
        
        rect = QRectF(
            min_y * self.cell_size,  # x coordinate (columns)
            min_x * self.cell_size,  # y coordinate (rows)
            (max_y - min_y + 1) * self.cell_size,  # width
            (max_x - min_x + 1) * self.cell_size   # height
        )
        
        self.selection_rect = QGraphicsRectItem(rect)
        self.selection_rect.setPen(QPen(Qt.blue, 2, Qt.DashLine))
        self.addItem(self.selection_rect)

    def finalize_selection(self, start, end):
        if self.selection_rect:
            self.removeItem(self.selection_rect)
            self.selection_rect = None
        
        x1, y1 = start
        x2, y2 = end
        
        # Get grid dimensions
        rows = len(self.grid.cells)
        cols = len(self.grid.cells[0])
        
        # Ensure coordinates are within grid bounds
        min_x = max(0, min(x1, x2))
        max_x = min(rows - 1, max(x1, x2))
        min_y = max(0, min(y1, y2))
        max_y = min(cols - 1, max(y1, y2))
        
        # Generate list of valid cell coordinates
        selected_cells = [
            (i, j)
            for i in range(min_x, max_x + 1)
            for j in range(min_y, max_y + 1)
        ]
        
        if selected_cells:  # Only emit if we have valid cells
            self.area_selected.emit(selected_cells)

    def select_cell(self, i, j):
        # Check if indices are valid for current grid
        if not (0 <= i < len(self.grid.cells) and 0 <= j < len(self.grid.cells[0])):
            return
        # Reset previous selection
        if self.selected_cell:
            prev_i, prev_j = self.selected_cell
            self.cell_items[(prev_i, prev_j)].setPen(QPen(Qt.black, 1))

        # Highlight new selection
        self.selected_cell = (i, j)
        self.cell_items[(i, j)].setPen(QPen(Qt.blue, 2))

    def setup_grid(self):
        for i, row in enumerate(self.grid.cells):
            for j, cell in enumerate(row):
                rect = QGraphicsRectItem(
                    j * self.cell_size,
                    i * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                color = QColor(cell.land_type.get_color())
                rect.setBrush(QBrush(color))
                rect.setPen(QPen(Qt.black, 1))
                self.addItem(rect)
                self.cell_items[(i, j)] = rect

    def update_cell(self, i, j, cell):
        if (i, j) in self.cell_items:
            color = QColor(cell.land_type.get_color())
            if cell.state == "igniting":
                color = QColor("orange")
            elif cell.state == "burning":
                color = QColor("red")
            elif cell.state == "burnt":
                color = QColor("gray")
            self.cell_items[(i, j)].setBrush(QBrush(color))

class GridView(QGraphicsView):
    def __init__(self, grid):
        super().__init__()
        self.scene = GridScene(grid)
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setRenderHint(QPainter.Antialiasing)
        
        # Add zoom parameters
        self.zoom_factor = 1.15
        self.current_zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        
        # For right-click drag
        self.setMouseTracking(True)
        self.last_mouse_pos = None
        self.is_dragging = False
        
        # Initial centering
        self.centerOn(self.scene.sceneRect().center())
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.is_dragging = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.is_dragging = False
            self.setCursor(Qt.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging and self.last_mouse_pos is not None:
            delta = event.pos() - self.last_mouse_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y())
            self.last_mouse_pos = event.pos()
        else:
            super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_factor
        else:
            zoom_factor = 1 / self.zoom_factor

        new_zoom = self.current_zoom * zoom_factor
        
        if self.min_zoom <= new_zoom <= self.max_zoom:
            self.current_zoom = new_zoom
            self.scale(zoom_factor, zoom_factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.centerOn(self.scene.sceneRect().center())
        self.current_zoom = 1.0

    def center_view(self):
        """Center the view on the grid"""
        # Reset any existing transformations
        self.resetTransform()
        self.current_zoom = 1.0
        
        # Get the scene rect and view rect
        scene_rect = self.scene.sceneRect()
        view_rect = self.viewport().rect()
        
        # Calculate the scaling factor to fit the grid in view while maintaining aspect ratio
        scale_x = view_rect.width() / scene_rect.width()
        scale_y = view_rect.height() / scene_rect.height()
        scale = min(scale_x, scale_y) * 0.9  # 0.9 to leave some margin
        
        # Apply the scaling
        self.scale(scale, scale)
        self.current_zoom = scale
        
        # Center the view
        self.centerOn(scene_rect.center())