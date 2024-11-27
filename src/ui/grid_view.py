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
        
        if event.button() == Qt.LeftButton:
            self.selection_start = (i, j)
            self.select_cell(i, j)
            self.cell_clicked.emit(i, j)

    def mouseMoveEvent(self, event):
        if self.selection_start:
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
        
        start_i, start_j = start
        end_i, end_j = end
        
        # Create rectangle using scene coordinates
        rect = QRectF(
            min(start_j, end_j) * self.cell_size,  # x coordinate (columns)
            min(start_i, end_i) * self.cell_size,  # y coordinate (rows)
            (abs(end_j - start_j) + 1) * self.cell_size,  # width
            (abs(end_i - start_i) + 1) * self.cell_size   # height
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
        selected_cells = [
            (i, j)
            for i in range(min(x1, x2), max(x1, x2) + 1)
            for j in range(min(y1, y2), max(y1, y2) + 1)
        ]
        self.area_selected.emit(selected_cells)

    def select_cell(self, i, j):
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)