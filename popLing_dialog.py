"""
Dialog for popLing plugin
"""

from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject, QgsVectorLayer, QgsRasterLayer, QgsWkbTypes


class popLingDialog(QDialog):
    """Dialog for selecting layers and parameters"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("popLing - Plot Points from Raster Density")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Layer selection group
        layer_group = QGroupBox("Layer Selection")
        layer_layout = QVBoxLayout()
        
        # Polygon layer selection
        polygon_layout = QHBoxLayout()
        polygon_layout.addWidget(QLabel("Polygon Layer:"))
        self.polygon_combo = QComboBox()
        self.polygon_combo.setMinimumWidth(250)
        polygon_layout.addWidget(self.polygon_combo)
        layer_layout.addLayout(polygon_layout)
        
        # Raster layer selection
        raster_layout = QHBoxLayout()
        raster_layout.addWidget(QLabel("Raster Layer:"))
        self.raster_combo = QComboBox()
        self.raster_combo.setMinimumWidth(250)
        raster_layout.addWidget(self.raster_combo)
        layer_layout.addLayout(raster_layout)
        
        layer_group.setLayout(layer_layout)
        layout.addWidget(layer_group)
        
        # Parameters group
        params_group = QGroupBox("Generation Parameters")
        params_layout = QVBoxLayout()
        
        # Minimum points per cell
        min_points_layout = QHBoxLayout()
        min_points_layout.addWidget(QLabel("Min Points per Cell:"))
        self.min_points_spin = QSpinBox()
        self.min_points_spin.setMinimum(1)
        self.min_points_spin.setMaximum(100)
        self.min_points_spin.setValue(5)
        min_points_layout.addWidget(self.min_points_spin)
        min_points_layout.addStretch()
        params_layout.addLayout(min_points_layout)
        
        # Maximum points per cell
        max_points_layout = QHBoxLayout()
        max_points_layout.addWidget(QLabel("Max Points per Cell:"))
        self.max_points_spin = QSpinBox()
        self.max_points_spin.setMinimum(1)
        self.max_points_spin.setMaximum(1000)
        self.max_points_spin.setValue(10)
        max_points_layout.addWidget(self.max_points_spin)
        max_points_layout.addStretch()
        params_layout.addLayout(max_points_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Populate layer combos
        self.populate_layers()
    
    def populate_layers(self):
        """Populate combo boxes with available layers"""
        self.polygon_combo.clear()
        self.raster_combo.clear()
        
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                    self.polygon_combo.addItem(layer.name(), layer)
            elif isinstance(layer, QgsRasterLayer):
                self.raster_combo.addItem(layer.name(), layer)
    
    def get_polygon_layer(self):
        """Get selected polygon layer"""
        index = self.polygon_combo.currentIndex()
        if index >= 0:
            return self.polygon_combo.itemData(index)
        return None
    
    def get_raster_layer(self):
        """Get selected raster layer"""
        index = self.raster_combo.currentIndex()
        if index >= 0:
            return self.raster_combo.itemData(index)
        return None
    
    def get_min_points(self):
        """Get minimum points per cell"""
        return self.min_points_spin.value()
    
    def get_max_points(self):
        """Get maximum points per cell"""
        return self.max_points_spin.value()

