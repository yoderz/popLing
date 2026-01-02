"""
Dialog for popLing plugin
"""

from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject, QgsVectorLayer, QgsRasterLayer, QgsWkbTypes


class popLingDialog(QDialog):
    """Dialog for selecting layers and parameters"""

    def __init__(self, parent=None, stats_callback=None):
        super().__init__(parent)
        self.stats_callback = stats_callback  # Callback to get raster statistics
        self.setWindowTitle("popLing - Plot Points from Raster Density")
        self.setMinimumWidth(500)
        
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
        self.raster_combo.currentIndexChanged.connect(self.on_raster_changed)
        raster_layout.addWidget(self.raster_combo)
        layer_layout.addLayout(raster_layout)
        
        # Raster statistics display
        self.raster_stats_label = QLabel("Raster Min/Max: Not loaded")
        self.raster_stats_label.setStyleSheet("color: gray; font-style: italic;")
        layer_layout.addWidget(self.raster_stats_label)
        
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
        
        # Raster points per sample width
        raster_points_layout = QHBoxLayout()
        raster_points_layout.addWidget(QLabel("Raster Points per Sample Width:"))
        self.raster_points_spin = QDoubleSpinBox()
        self.raster_points_spin.setMinimum(0.1)
        self.raster_points_spin.setMaximum(10.0)
        self.raster_points_spin.setSingleStep(0.1)
        self.raster_points_spin.setValue(2.0)
        self.raster_points_spin.setToolTip("Number of raster cell widths per sampling grid cell. Smaller values = finer grid, larger values = coarser grid.")
        raster_points_layout.addWidget(self.raster_points_spin)
        raster_points_layout.addStretch()
        params_layout.addLayout(raster_points_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Density ranges group
        density_group = QGroupBox("Density Ranges")
        density_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("Define three density ranges. For each range, specify min/max raster values and points per cell.")
        instructions.setWordWrap(True)
        density_layout.addWidget(instructions)
        
        # Table for density ranges
        self.density_table = QTableWidget()
        self.density_table.setColumnCount(3)
        self.density_table.setRowCount(3)
        self.density_table.setHorizontalHeaderLabels(["Min Value", "Max Value", "Points per Cell"])
        self.density_table.horizontalHeader().setStretchLastSection(True)
        self.density_table.setMinimumHeight(120)
        
        # Set default values for the three ranges
        # Range 1: Low density
        self.density_table.setItem(0, 0, QTableWidgetItem("10"))
        self.density_table.setItem(0, 1, QTableWidgetItem("200"))
        self.density_table.setItem(0, 2, QTableWidgetItem(".3"))
        
        # Range 2: Medium density
        self.density_table.setItem(1, 0, QTableWidgetItem("200"))
        self.density_table.setItem(1, 1, QTableWidgetItem("4000"))
        self.density_table.setItem(1, 2, QTableWidgetItem("1.0"))
        
        # Range 3: High density
        self.density_table.setItem(2, 0, QTableWidgetItem("4000"))
        self.density_table.setItem(2, 1, QTableWidgetItem("25000"))
        self.density_table.setItem(2, 2, QTableWidgetItem("5.0"))
        
        density_layout.addWidget(self.density_table)
        density_group.setLayout(density_layout)
        layout.addWidget(density_group)
        
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
    
    def get_raster_points_per_sample_width(self):
        """Get raster points per sample width"""
        return self.raster_points_spin.value()
    
    def on_raster_changed(self, index):
        """Update raster statistics display when raster layer changes"""
        if index >= 0 and self.stats_callback:
            raster_layer = self.raster_combo.itemData(index)
            if raster_layer:
                self.raster_stats_label.setText("Raster Min/Max: Calculating...")
                # Get statistics using callback
                stats = self.stats_callback(raster_layer)
                if stats:
                    self.update_raster_stats(stats["min"], stats["max"])
                else:
                    self.raster_stats_label.setText("Raster Min/Max: Unable to calculate")
                    self.raster_stats_label.setStyleSheet("color: red; font-style: italic;")
        else:
            self.raster_stats_label.setText("Raster Min/Max: Not loaded")
            self.raster_stats_label.setStyleSheet("color: gray; font-style: italic;")
    
    def update_raster_stats(self, min_val, max_val):
        """Update the raster statistics display"""
        if min_val is not None and max_val is not None:
            self.raster_stats_label.setText(f"Raster Min/Max: {min_val:.2f} / {max_val:.2f}")
            self.raster_stats_label.setStyleSheet("color: black; font-style: normal;")
        else:
            self.raster_stats_label.setText("Raster Min/Max: Unable to calculate")
            self.raster_stats_label.setStyleSheet("color: red; font-style: italic;")
    
    def get_density_ranges(self):
        """Get density ranges from the table"""
        ranges = []
        for row in range(3):
            min_item = self.density_table.item(row, 0)
            max_item = self.density_table.item(row, 1)
            points_item = self.density_table.item(row, 2)
            
            if min_item and max_item and points_item:
                try:
                    min_val = float(min_item.text())
                    max_val = float(max_item.text())
                    points_per_cell = float(points_item.text())
                    
                    ranges.append({
                        "min": min_val,
                        "max": max_val,
                        "points_per_cell": points_per_cell
                    })
                except ValueError:
                    # Skip invalid rows
                    pass
        
        return ranges
    
    def validate_density_ranges(self):
        """Validate that density ranges are properly configured"""
        ranges = self.get_density_ranges()
        if len(ranges) == 0:
            return False, "No valid density ranges defined"
        
        # Check for overlapping or invalid ranges
        for i, range1 in enumerate(ranges):
            if range1["min"] >= range1["max"]:
                return False, f"Range {i+1}: Min must be less than Max"
            if range1["points_per_cell"] < 0:
                return False, f"Range {i+1}: Points per cell cannot be negative"
        
        return True, ""

