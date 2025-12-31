"""
/***************************************************************************
 popLing
                                 A QGIS plugin
 Plots points within a polygon based on density values from a raster file
                             -------------------
        begin                : 2024-01-01
        copyright            : (C) 2024
        email                : your.email@example.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 * ***************************************************************************/
"""

# #region agent log - Module level logging
try:
    import os
    import json
    import traceback
    from datetime import datetime
    PLUGIN_DIR_TEMP = os.path.dirname(os.path.abspath(__file__))
    DEBUG_LOG_PATH_TEMP = os.path.join(PLUGIN_DIR_TEMP, '.cursor', 'debug.log')
    def _early_log(msg):
        try:
            log_dir = os.path.dirname(DEBUG_LOG_PATH_TEMP)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            with open(DEBUG_LOG_PATH_TEMP, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"timestamp": int(datetime.now().timestamp() * 1000), "location": "module_init", "message": msg, "plugin": "popLing"}) + '\n')
        except:
            pass
    _early_log("Module import starting")
except:
    pass
# #endregion

try:
    from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QVariant
    # #region agent log
    _early_log("QtCore imported successfully")
    # #endregion
except Exception as e:
    # #region agent log
    _early_log(f"QtCore import failed: {str(e)}")
    # #endregion
    raise

try:
    from qgis.PyQt.QtGui import QIcon
    # #region agent log
    _early_log("QtGui imported successfully")
    # #endregion
except Exception as e:
    # #region agent log
    _early_log(f"QtGui import failed: {str(e)}")
    # #endregion
    raise

try:
    from qgis.PyQt.QtWidgets import QAction, QMessageBox, QFileDialog, QDialog
    # #region agent log
    _early_log("QtWidgets imported successfully")
    # #endregion
except Exception as e:
    # #region agent log
    _early_log(f"QtWidgets import failed: {str(e)}")
    # #endregion
    raise

try:
    try:
        from .popLing_dialog import popLingDialog
        # #region agent log
        _early_log("popLing_dialog imported (relative)")
        # #endregion
    except ImportError:
        from popLing_dialog import popLingDialog
        # #region agent log
        _early_log("popLing_dialog imported (absolute)")
        # #endregion
except Exception as e:
    # #region agent log
    _early_log(f"popLing_dialog import failed: {str(e)} | {traceback.format_exc()}")
    # #endregion
    raise

try:
    from qgis.core import (
        QgsProject, QgsVectorLayer, QgsRasterLayer, QgsPointXY, 
        QgsFeature, QgsGeometry, QgsField, QgsWkbTypes, QgsCoordinateTransform,
        QgsCoordinateReferenceSystem, QgsRaster, QgsRectangle, QgsPoint, QgsRasterBandStats
    )
    # #region agent log
    _early_log("qgis.core imported successfully")
    # #endregion
except Exception as e:
    # #region agent log
    _early_log(f"qgis.core import failed: {str(e)}")
    # #endregion
    raise

try:
    from qgis.utils import iface
    # #region agent log
    _early_log("qgis.utils imported successfully")
    # #endregion
except Exception as e:
    # #region agent log
    _early_log(f"qgis.utils import failed: {str(e)}")
    # #endregion
    # iface might not be available during import, that's OK
    iface = None

import random
import math

# #region agent log
_early_log("All imports completed successfully")
# #endregion

# Debug logging configuration
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG_LOG_PATH = os.path.join(PLUGIN_DIR, '.cursor', 'debug.log')
PLUGIN_NAME = 'popLing'

def _safe_write_file(path, content):
    """Safely write to file with all error handling"""
    try:
        log_dir = os.path.dirname(path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content + '\n')
        return True
    except Exception:
        return False

def debug_log(location, message, data=None, hypothesis_id=None, run_id='run1'):
    """Write debug log entry to both QGIS message log and debug.log file - completely crash-safe"""
    # Always try to write to file first (doesn't require QGIS)
    try:
        log_entry = {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "location": location,
            "message": message,
            "sessionId": "debug-session",
            "runId": run_id,
            "plugin": PLUGIN_NAME
        }
        if data is not None:
            # Convert data to JSON-serializable format
            try:
                json.dumps(data)  # Test if serializable
                log_entry["data"] = data
            except (TypeError, ValueError):
                log_entry["data"] = str(data)
        if hypothesis_id:
            log_entry["hypothesisId"] = hypothesis_id
        
        # Write to file (this should never crash)
        _safe_write_file(DEBUG_LOG_PATH, json.dumps(log_entry))
    except Exception:
        # If even file writing fails, try a simple text log
        try:
            simple_log = f"[{datetime.now().isoformat()}] {location}: {message}\n"
            simple_path = os.path.join(PLUGIN_DIR, 'error.log')
            _safe_write_file(simple_path, simple_log)
        except Exception:
            pass  # Give up - can't log
    
    # Try QGIS message log (may not be available during import)
    try:
        from qgis.core import QgsMessageLog
        msg = f"{location}: {message}"
        if data:
            try:
                msg += f" | Data: {json.dumps(data)}"
            except:
                msg += f" | Data: {str(data)}"
        QgsMessageLog.logMessage(msg, PLUGIN_NAME, QgsMessageLog.INFO)
    except Exception:
        pass  # QGIS not available or not initialized yet


class popLing:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # #region agent log
        debug_log("popLing.__init__", "Plugin initializing", {"iface": str(type(iface))}, run_id="init")
        # #endregion
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr(u'&popLing')
        # #region agent log
        debug_log("popLing.__init__", "Plugin initialized", {"plugin_dir": self.plugin_dir}, run_id="init")
        # #endregion

    def tr(self, message):
        """Get the translation for a string using Qt translation API."""
        return QCoreApplication.translate('popLing', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar."""
        # #region agent log
        debug_log("popLing.add_action", "Function entry", {"icon_path": icon_path, "text": text}, hypothesis_id="E")
        # #endregion

        # Handle None icon_path safely
        icon = None
        if icon_path:
            try:
                icon = QIcon(icon_path)
                # #region agent log
                debug_log("popLing.add_action", "Icon created", {"icon_path": icon_path}, hypothesis_id="E")
                # #endregion
            except Exception as e:
                # #region agent log
                debug_log("popLing.add_action", "Icon creation failed", {"error": str(e), "icon_path": icon_path}, hypothesis_id="E")
                # #endregion
                icon = None  # Use default icon
        
        # QAction constructor: if icon is None, use QAction(text, parent), otherwise QAction(icon, text, parent)
        if icon is not None:
            action = QAction(icon, text, parent)
            # #region agent log
            debug_log("popLing.add_action", "QAction created with icon", {}, hypothesis_id="E")
            # #endregion
        else:
            action = QAction(text, parent)
            # #region agent log
            debug_log("popLing.add_action", "QAction created without icon", {}, hypothesis_id="E")
            # #endregion
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        try:
            if add_to_toolbar:
                self.iface.addToolBarIcon(action)
                # #region agent log
                debug_log("popLing.add_action", "Toolbar icon added", {}, hypothesis_id="E")
                # #endregion

            if add_to_menu:
                self.iface.addPluginToMenu(
                    self.menu,
                    action)
                # #region agent log
                debug_log("popLing.add_action", "Menu item added", {}, hypothesis_id="E")
                # #endregion

            self.actions.append(action)
            # #region agent log
            debug_log("popLing.add_action", "Function exit - success", {}, hypothesis_id="E")
            # #endregion
        except Exception as e:
            # #region agent log
            debug_log("popLing.add_action", "Exception in add_action", {"error": str(e), "traceback": traceback.format_exc()}, hypothesis_id="E")
            # #endregion
            raise

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        # Use icon if it exists, otherwise use None (default icon)
        if not os.path.exists(icon_path):
            icon_path = None
        self.add_action(
            icon_path,
            text=self.tr(u'Plot Points from Raster Density'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&popLing'),
                action)
            self.iface.removeToolBarIcon(action)

    def get_raster_statistics(self, raster_layer, band=1):
        """Get raster statistics (min/max) using QgsRasterBandStats"""
        # #region agent log
        debug_log("popLing.get_raster_statistics", "Function entry", {
            "raster": raster_layer.name(),
            "band": band
        }, hypothesis_id="D")
        # #endregion
        try:
            provider = raster_layer.dataProvider()
            stats = provider.bandStatistics(band, QgsRasterBandStats.Min | QgsRasterBandStats.Max, raster_layer.extent())
            # #region agent log
            debug_log("popLing.get_raster_statistics", "Statistics obtained", {
                "min": stats.minimumValue,
                "max": stats.maximumValue,
                "has_stats": stats.minimumValue is not None and stats.maximumValue is not None
            }, hypothesis_id="D")
            # #endregion
            return {
                "min": stats.minimumValue,
                "max": stats.maximumValue
            }
        except Exception as e:
            # #region agent log
            debug_log("popLing.get_raster_statistics", "Exception caught", {
                "error": str(e),
                "traceback": traceback.format_exc()
            }, hypothesis_id="D")
            # #endregion
            return None
    
    def get_density_range_for_value(self, value, density_ranges):
        """Determine which density range a raster value falls into"""
        # #region agent log
        debug_log("popLing.get_density_range_for_value", "Function entry", {
            "value": value,
            "num_ranges": len(density_ranges)
        }, hypothesis_id="E")
        # #endregion
        if value is None:
            return None
        
        # Check for invalid values (NaN, inf)
        try:
            import math
            if math.isnan(value) or math.isinf(value):
                # #region agent log
                debug_log("popLing.get_density_range_for_value", "Invalid value (NaN/inf)", {
                    "value": value
                }, hypothesis_id="E")
                # #endregion
                return None
        except (TypeError, ValueError):
            # Value might not be a number
            # #region agent log
            debug_log("popLing.get_density_range_for_value", "Value is not a number", {
                "value": value,
                "type": str(type(value))
            }, hypothesis_id="E")
            # #endregion
            return None
        
        for i, range_def in enumerate(density_ranges):
            try:
                min_val = float(range_def["min"])
                max_val = float(range_def["max"])
                # Check if value falls within range (inclusive boundaries)
                if min_val <= value <= max_val:
                    # #region agent log
                    debug_log("popLing.get_density_range_for_value", "Range matched", {
                        "value": value,
                        "range_index": i,
                        "min": min_val,
                        "max": max_val,
                        "points_per_cell": range_def["points_per_cell"]
                    }, hypothesis_id="E")
                    # #endregion
                    return range_def
            except (KeyError, ValueError, TypeError) as e:
                # #region agent log
                debug_log("popLing.get_density_range_for_value", "Error checking range", {
                    "range_index": i,
                    "error": str(e),
                    "range_def": str(range_def)
                }, hypothesis_id="E")
                # #endregion
                continue
        
        # #region agent log
        debug_log("popLing.get_density_range_for_value", "No range matched", {
            "value": value,
            "ranges": [{"min": r.get("min"), "max": r.get("max")} for r in density_ranges]
        }, hypothesis_id="E")
        # #endregion
        return None
    
    def should_place_point(self, probability):
        """Random decision when points_per_cell < 1"""
        if probability <= 0:
            return False
        if probability >= 1:
            return True
        result = random.random() < probability
        # #region agent log
        debug_log("popLing.should_place_point", "Random decision", {
            "probability": probability,
            "result": result
        }, hypothesis_id="F")
        # #endregion
        return result

    def get_raster_value_at_point(self, raster_layer, point):
        """Get raster value at a given point."""
        # #region agent log
        debug_log("popLing.get_raster_value_at_point", "Function entry", {"point": f"({point.x()}, {point.y()})", "raster": raster_layer.name()}, hypothesis_id="A")
        # #endregion
        try:
            provider = raster_layer.dataProvider()
            # #region agent log
            debug_log("popLing.get_raster_value_at_point", "Provider obtained", {"provider_type": str(type(provider))}, hypothesis_id="A")
            # #endregion
            ident = provider.identify(point, QgsRaster.IdentifyFormatValue)
            # #region agent log
            debug_log("popLing.get_raster_value_at_point", "Identify called", {"is_valid": ident.isValid()}, hypothesis_id="A")
            # #endregion
            if ident.isValid():
                results = ident.results()
                # #region agent log
                debug_log("popLing.get_raster_value_at_point", "Results obtained", {"has_results": bool(results), "result_count": len(results) if results else 0}, hypothesis_id="A")
                # #endregion
                if results:
                    # Get the first band value
                    value = list(results.values())[0]
                    # #region agent log
                    debug_log("popLing.get_raster_value_at_point", "Value extracted", {"raw_value": str(value), "value_type": str(type(value))}, hypothesis_id="A")
                    # #endregion
                    if value:
                        result = float(value)
                        # #region agent log
                        debug_log("popLing.get_raster_value_at_point", "Function exit", {"return_value": result}, hypothesis_id="A")
                        # #endregion
                        return result
            # #region agent log
            debug_log("popLing.get_raster_value_at_point", "Function exit - no value", {"return_value": None}, hypothesis_id="A")
            # #endregion
            return None
        except Exception as e:
            # #region agent log
            debug_log("popLing.get_raster_value_at_point", "Exception caught", {"error": str(e), "traceback": traceback.format_exc()}, hypothesis_id="A")
            # #endregion
            return None

    def generate_points_in_polygon(self, polygon_layer, raster_layer, density_ranges, raster_points_per_sample_width=2.0):
        """Generate points within polygon based on raster density ranges."""
        # #region agent log
        debug_log("popLing.generate_points_in_polygon", "Function entry", {
            "polygon_layer": polygon_layer.name(),
            "raster_layer": raster_layer.name(),
            "num_ranges": len(density_ranges),
            "raster_points_per_sample_width": raster_points_per_sample_width
        }, hypothesis_id="B")
        # #endregion
        all_points = []
        
        # Get raster extent and resolution (same for all polygons)
        raster_extent = raster_layer.extent()
        raster_width = raster_layer.width()
        raster_height = raster_layer.height()
        
        # Safety checks for raster dimensions
        if raster_width <= 0 or raster_height <= 0:
            # #region agent log
            debug_log("popLing.generate_points_in_polygon", "Invalid raster dimensions", {
                "raster_width": raster_width,
                "raster_height": raster_height
            }, hypothesis_id="B")
            # #endregion
            return []
        
        x_res = raster_extent.width() / raster_width
        y_res = raster_extent.height() / raster_height
        
        # Check for invalid resolutions
        if not math.isfinite(x_res) or not math.isfinite(y_res) or x_res <= 0 or y_res <= 0:
            # #region agent log
            debug_log("popLing.generate_points_in_polygon", "Invalid raster resolution", {
                "x_res": x_res,
                "y_res": y_res,
                "raster_width": raster_width,
                "raster_height": raster_height,
                "extent_width": raster_extent.width(),
                "extent_height": raster_extent.height()
            }, hypothesis_id="B")
            # #endregion
            return []
        
        # #region agent log
        debug_log("popLing.generate_points_in_polygon", "Raster properties calculated", {
            "raster_width": raster_width,
            "raster_height": raster_height,
            "x_res": x_res,
            "y_res": y_res
        }, hypothesis_id="B")
        # #endregion
        
        # Transform coordinates if needed
        polygon_crs = polygon_layer.crs()
        raster_crs = raster_layer.crs()
        transform = None
        if polygon_crs != raster_crs:
            transform = QgsCoordinateTransform(
                polygon_crs, raster_crs, QgsProject.instance())
            # #region agent log
            debug_log("popLing.generate_points_in_polygon", "Transform created", {}, hypothesis_id="B")
            # #endregion
        
        # Calculate cell size
        raster_cell_size = min(x_res, y_res)
        cell_size = raster_cell_size * raster_points_per_sample_width
        
        # Safety check: ensure cell_size is valid
        if cell_size <= 0 or not math.isfinite(cell_size):
            # #region agent log
            debug_log("popLing.generate_points_in_polygon", "Invalid cell_size, aborting", {
                "raster_cell_size": raster_cell_size,
                "raster_points_per_sample_width": raster_points_per_sample_width,
                "cell_size": cell_size,
                "x_res": x_res,
                "y_res": y_res
            }, hypothesis_id="B")
            # #endregion
            return []
        
        # #region agent log
        debug_log("popLing.generate_points_in_polygon", "Cell size calculated", {
            "raster_cell_size": raster_cell_size,
            "raster_points_per_sample_width": raster_points_per_sample_width,
            "cell_size": cell_size
        }, hypothesis_id="B")
        # #endregion
        
        # Process all polygons
        features = polygon_layer.getFeatures()
        polygon_count = 0
        total_cells_processed = 0
        total_points_generated = 0
        
        for polygon_feature in features:
            polygon_count += 1
            polygon_geom = polygon_feature.geometry()
            
            # Get bounding box of polygon
            bbox = polygon_geom.boundingBox()
            # #region agent log
            debug_log("popLing.generate_points_in_polygon", f"Processing polygon {polygon_count}", {
                "x_min": bbox.xMinimum(),
                "x_max": bbox.xMaximum(),
                "y_min": bbox.yMinimum(),
                "y_max": bbox.yMaximum()
            }, hypothesis_id="B")
            # #endregion
            
            x_min = bbox.xMinimum()
            x_max = bbox.xMaximum()
            y_min = bbox.yMinimum()
            y_max = bbox.yMaximum()
            
            # Create grid of sample points for this polygon
            # Safety check: prevent infinite loops
            if x_max <= x_min or y_max <= y_min:
                # #region agent log
                debug_log("popLing.generate_points_in_polygon", "Invalid bounding box, skipping polygon", {
                    "polygon_count": polygon_count,
                    "x_min": x_min,
                    "x_max": x_max,
                    "y_min": y_min,
                    "y_max": y_max
                }, hypothesis_id="B")
                # #endregion
                continue
            
            # Safety check: prevent processing too many cells
            estimated_cells = ((x_max - x_min) / cell_size) * ((y_max - y_min) / cell_size)
            if estimated_cells > 1000000:  # Limit to 1 million cells per polygon
                # #region agent log
                debug_log("popLing.generate_points_in_polygon", "Polygon too large, skipping", {
                    "polygon_count": polygon_count,
                    "estimated_cells": estimated_cells
                }, hypothesis_id="B")
                # #endregion
                continue
            
            x = x_min
            cells_in_polygon = 0
            max_iterations = int(((x_max - x_min) / cell_size) * ((y_max - y_min) / cell_size)) + 1000
            iteration_count = 0
            
            while x <= x_max and iteration_count < max_iterations:
                y = y_min
                while y <= y_max and iteration_count < max_iterations:
                    iteration_count += 1
                    try:
                        point = QgsPointXY(x, y)
                        
                        # Check if point is within polygon
                        if polygon_geom.contains(point):
                            # Get raster value at this point
                            if transform:
                                try:
                                    raster_point = transform.transform(point)
                                except Exception as e:
                                    # #region agent log
                                    debug_log("popLing.generate_points_in_polygon", "Transform error", {
                                        "error": str(e),
                                        "point": f"({point.x()}, {point.y()})"
                                    }, hypothesis_id="B")
                                    # #endregion
                                    y += cell_size
                                    continue
                            else:
                                raster_point = point
                            
                            raster_value = self.get_raster_value_at_point(raster_layer, raster_point)
                            
                            # Skip if no valid raster value
                            if raster_value is None:
                                y += cell_size
                                continue
                            
                            # Find which density range this value falls into
                            matched_range = self.get_density_range_for_value(raster_value, density_ranges)
                            
                            if matched_range:
                                points_per_cell = matched_range["points_per_cell"]
                                
                                # Handle fractional points_per_cell
                                try:
                                    points_per_cell = float(points_per_cell)
                                except (ValueError, TypeError):
                                    # #region agent log
                                    debug_log("popLing.generate_points_in_polygon", "Invalid points_per_cell", {
                                        "points_per_cell": points_per_cell,
                                        "type": str(type(points_per_cell))
                                    }, hypothesis_id="B")
                                    # #endregion
                                    y += cell_size
                                    continue
                                
                                if points_per_cell >= 1:
                                    # Generate integer number of points
                                    try:
                                        num_points = int(points_per_cell)
                                        if num_points < 0 or num_points > 10000:  # Safety limit
                                            # #region agent log
                                            debug_log("popLing.generate_points_in_polygon", "Points per cell out of safe range", {
                                                "num_points": num_points
                                            }, hypothesis_id="B")
                                            # #endregion
                                            y += cell_size
                                            continue
                                    except (ValueError, OverflowError) as e:
                                        # #region agent log
                                        debug_log("popLing.generate_points_in_polygon", "Error converting points_per_cell to int", {
                                            "points_per_cell": points_per_cell,
                                            "error": str(e)
                                        }, hypothesis_id="B")
                                        # #endregion
                                        y += cell_size
                                        continue
                                    
                                    for _ in range(num_points):
                                        offset_x = random.uniform(-cell_size/2, cell_size/2)
                                        offset_y = random.uniform(-cell_size/2, cell_size/2)
                                        new_point = QgsPointXY(
                                            point.x() + offset_x,
                                            point.y() + offset_y
                                        )
                                        if polygon_geom.contains(new_point):
                                            all_points.append(new_point)
                                            total_points_generated += 1
                                else:
                                    # Fractional: randomly decide whether to place 1 point
                                    if self.should_place_point(points_per_cell):
                                        offset_x = random.uniform(-cell_size/2, cell_size/2)
                                        offset_y = random.uniform(-cell_size/2, cell_size/2)
                                        new_point = QgsPointXY(
                                            point.x() + offset_x,
                                            point.y() + offset_y
                                        )
                                        if polygon_geom.contains(new_point):
                                            all_points.append(new_point)
                                            total_points_generated += 1
                                
                                total_cells_processed += 1
                                cells_in_polygon += 1
                    except Exception as e:
                        # #region agent log
                        debug_log("popLing.generate_points_in_polygon", "Exception in cell processing", {
                            "error": str(e),
                            "traceback": traceback.format_exc(),
                            "x": x,
                            "y": y,
                            "polygon_count": polygon_count,
                            "iteration_count": iteration_count
                        }, hypothesis_id="B")
                        # #endregion
                        # Continue processing other cells
                        y += cell_size
                        continue
                    
                    y += cell_size
                
                if iteration_count >= max_iterations:
                    # #region agent log
                    debug_log("popLing.generate_points_in_polygon", "Max iterations reached, breaking", {
                        "polygon_count": polygon_count,
                        "iteration_count": iteration_count,
                        "max_iterations": max_iterations
                    }, hypothesis_id="B")
                    # #endregion
                    break
                
                x += cell_size
            
            # #region agent log
            debug_log("popLing.generate_points_in_polygon", f"Completed polygon {polygon_count}", {
                "cells_in_polygon": cells_in_polygon
            }, hypothesis_id="B")
            # #endregion
        
        # #region agent log
        debug_log("popLing.generate_points_in_polygon", "Point generation complete", {
            "polygons_processed": polygon_count,
            "cells_processed": total_cells_processed,
            "points_generated": total_points_generated,
            "total_points": len(all_points)
        }, hypothesis_id="B")
        # #endregion
        return all_points

    def run(self):
        """Run method that performs all the real work"""
        # #region agent log
        debug_log("popLing.run", "Function entry - plugin run started", {}, hypothesis_id="C")
        # #endregion
        # Show dialog with stats callback
        dlg = popLingDialog(stats_callback=self.get_raster_statistics)
        
        # Check if we have required layers
        polygon_count = dlg.polygon_combo.count()
        raster_count = dlg.raster_combo.count()
        # #region agent log
        debug_log("popLing.run", "Layer check", {
            "polygon_count": polygon_count,
            "raster_count": raster_count
        }, hypothesis_id="C")
        # #endregion
        
        if polygon_count == 0:
            # #region agent log
            debug_log("popLing.run", "No polygon layers - early exit", {}, hypothesis_id="C")
            # #endregion
            QMessageBox.warning(
                self.iface.mainWindow(),
                "popLing",
                "No polygon layers found in the project. Please add a polygon layer.")
            return
        
        if raster_count == 0:
            # #region agent log
            debug_log("popLing.run", "No raster layers - early exit", {}, hypothesis_id="C")
            # #endregion
            QMessageBox.warning(
                self.iface.mainWindow(),
                "popLing",
                "No raster layers found in the project. Please add a raster layer.")
            return
        
        # Show dialog and get user input
        dialog_result = dlg.exec_()
        # #region agent log
        debug_log("popLing.run", "Dialog result", {"result": "Accepted" if dialog_result == QDialog.Accepted else "Rejected"}, hypothesis_id="C")
        # #endregion
        if dialog_result != QDialog.Accepted:
            return
        
        polygon_layer = dlg.get_polygon_layer()
        raster_layer = dlg.get_raster_layer()
        raster_points_per_sample_width = dlg.get_raster_points_per_sample_width()
        density_ranges = dlg.get_density_ranges()
        
        # #region agent log
        debug_log("popLing.run", "User selections", {
            "polygon_layer": polygon_layer.name() if polygon_layer else None,
            "raster_layer": raster_layer.name() if raster_layer else None,
            "raster_points_per_sample_width": raster_points_per_sample_width,
            "density_ranges": density_ranges
        }, hypothesis_id="C")
        # #endregion
        
        if not polygon_layer or not raster_layer:
            # #region agent log
            debug_log("popLing.run", "Invalid layer selection - early exit", {}, hypothesis_id="C")
            # #endregion
            QMessageBox.warning(
                self.iface.mainWindow(),
                "popLing",
                "Please select both a polygon and raster layer.")
            return
        
        # Validate raster_points_per_sample_width
        if raster_points_per_sample_width <= 0:
            # #region agent log
            debug_log("popLing.run", "Invalid raster_points_per_sample_width - early exit", {
                "raster_points_per_sample_width": raster_points_per_sample_width
            }, hypothesis_id="C")
            # #endregion
            QMessageBox.warning(
                self.iface.mainWindow(),
                "popLing",
                "Raster Points per Sample Width must be greater than 0.")
            return
        
        # Validate density ranges
        is_valid, error_msg = dlg.validate_density_ranges()
        if not is_valid:
            # #region agent log
            debug_log("popLing.run", "Invalid density ranges - early exit", {
                "error": error_msg
            }, hypothesis_id="C")
            # #endregion
            QMessageBox.warning(
                self.iface.mainWindow(),
                "popLing",
                f"Invalid density ranges: {error_msg}")
            return
        
        if len(density_ranges) == 0:
            # #region agent log
            debug_log("popLing.run", "No density ranges defined - early exit", {}, hypothesis_id="C")
            # #endregion
            QMessageBox.warning(
                self.iface.mainWindow(),
                "popLing",
                "Please define at least one density range.")
            return
        
        # Get and display raster statistics
        stats = self.get_raster_statistics(raster_layer)
        if stats:
            # #region agent log
            debug_log("popLing.run", "Raster statistics", {
                "min": stats["min"],
                "max": stats["max"]
            }, hypothesis_id="C")
            # #endregion
        
        # Generate points
        self.iface.messageBar().pushMessage(
            "popLing",
            "Generating points... This may take a moment.",
            duration=3)
        
        # #region agent log
        debug_log("popLing.run", "Starting point generation", {}, hypothesis_id="C")
        # #endregion
        points = self.generate_points_in_polygon(
            polygon_layer, 
            raster_layer,
            density_ranges,
            raster_points_per_sample_width=raster_points_per_sample_width
        )
        # #region agent log
        debug_log("popLing.run", "Point generation completed", {"points_count": len(points)}, hypothesis_id="C")
        # #endregion
        
        if not points:
            # #region agent log
            debug_log("popLing.run", "No points generated - early exit", {}, hypothesis_id="C")
            # #endregion
            QMessageBox.warning(
                self.iface.mainWindow(),
                "popLing",
                "No points were generated. Check that the polygon and raster overlap.")
            return
        
        # Create new point layer
        crs = polygon_layer.crs()
        # #region agent log
        debug_log("popLing.run", "Creating point layer", {"crs": crs.authid()}, hypothesis_id="C")
        # #endregion
        point_layer = QgsVectorLayer(
            f"Point?crs={crs.authid()}",
            f"Points_from_{raster_layer.name()}",  
            "memory"
        )
        
        # Add fields
        provider = point_layer.dataProvider()
        provider.addAttributes([QgsField("id", QVariant.Int)])
        point_layer.updateFields()
        # #region agent log
        debug_log("popLing.run", "Point layer fields added", {}, hypothesis_id="C")
        # #endregion
        
        # Add features
        features = []
        for i, point in enumerate(points):
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(point))
            feat.setAttributes([i + 1])
            features.append(feat)
        
        provider.addFeatures(features)
        point_layer.updateExtents()
        # #region agent log
        debug_log("popLing.run", "Features added to layer", {"feature_count": len(features)}, hypothesis_id="C")
        # #endregion
        
        # Add layer to project
        QgsProject.instance().addMapLayer(point_layer)
        # #region agent log
        debug_log("popLing.run", "Layer added to project", {}, hypothesis_id="C")
        # #endregion
        
        # Zoom to layer
        self.iface.mapCanvas().setExtent(point_layer.extent())
        self.iface.mapCanvas().refresh()
        
        # #region agent log
        debug_log("popLing.run", "Function exit - success", {"total_points": len(points)}, hypothesis_id="C")
        # #endregion
        self.iface.messageBar().pushMessage(
            "popLing",
            f"Successfully generated {len(points)} points!",
            duration=5)

