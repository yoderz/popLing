"""
popLing - A QGIS plugin for plotting points within polygons based on raster density
"""

def classFactory(iface):
    """Load popLing class from file popLing.
    
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    # #region agent log - Early logging in classFactory
    try:
        import os
        import json
        from datetime import datetime
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(plugin_dir, '.cursor', 'debug.log')
        log_dir = os.path.dirname(log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": int(datetime.now().timestamp() * 1000),
                "location": "__init__.classFactory",
                "message": "classFactory called",
                "data": {"iface_type": str(type(iface))},
                "plugin": "popLing"
            }) + '\n')
    except Exception:
        pass
    # #endregion
    
    try:
        # #region agent log
        try:
            import os
            import json
            from datetime import datetime
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(plugin_dir, '.cursor', 'debug.log')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "__init__.classFactory",
                    "message": "About to import popLing",
                    "plugin": "popLing"
                }) + '\n')
        except:
            pass
        # #endregion
        
        from .popLing import popLing
        
        # #region agent log
        try:
            import os
            import json
            from datetime import datetime
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(plugin_dir, '.cursor', 'debug.log')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "__init__.classFactory",
                    "message": "popLing imported, creating instance",
                    "plugin": "popLing"
                }) + '\n')
        except:
            pass
        # #endregion
        
        instance = popLing(iface)
        
        # #region agent log
        try:
            import os
            import json
            from datetime import datetime
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(plugin_dir, '.cursor', 'debug.log')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "__init__.classFactory",
                    "message": "popLing instance created successfully",
                    "plugin": "popLing"
                }) + '\n')
        except:
            pass
        # #endregion
        
        return instance
    except Exception as e:
        # #region agent log
        try:
            import os
            import json
            import traceback
            from datetime import datetime
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(plugin_dir, '.cursor', 'debug.log')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "__init__.classFactory",
                    "message": "ERROR in classFactory",
                    "data": {"error": str(e), "traceback": traceback.format_exc()},
                    "plugin": "popLing"
                }) + '\n')
        except:
            pass
        # #endregion
        raise

