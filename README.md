# popLing - QGIS Plugin

A QGIS plugin that generates point features within a polygon layer based on density values from a raster layer. Higher density values in the raster will result in more points being generated in those areas.

## Features

- Select polygon and raster layers from your QGIS project
- Configure minimum and maximum points per cell
- Automatically generates points based on raster density values
- Creates a new point layer in your project
- Handles coordinate reference system transformations automatically

## Installation

### Method 1: Manual Installation

1. Copy the entire `popLing` folder to your QGIS plugins directory:
   - **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

2. Restart QGIS or go to **Plugins → Manage and Install Plugins → Installed** and enable "popLing"

### Method 2: Development Installation (Symlink)

For development, you can create a symlink from the plugin directory to your development folder:

**Windows (PowerShell as Administrator):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\popLing" -Target "C:\Users\ZAALANYODER\Documents\GitHub\popLing"
```

**Linux/macOS:**
```bash
ln -s /path/to/popLing ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/popLing
```

## Usage

1. **Prepare your data:**
   - Load a polygon layer into QGIS (the area where you want points generated)
   - Load a raster layer into QGIS (containing density values)

2. **Run the plugin:**
   - Click the popLing icon in the toolbar, or
   - Go to **Plugins → popLing → Plot Points from Raster Density**

3. **Configure settings:**
   - Select your polygon layer from the dropdown
   - Select your raster layer from the dropdown
   - Adjust "Min Points per Cell" (default: 5)
   - Adjust "Max Points per Cell" (default: 10)
   - Click **OK**

4. **View results:**
   - A new point layer will be created and added to your project
   - The map will automatically zoom to show the generated points

## How It Works

1. The plugin samples the raster at regular grid points within the polygon
2. For each sample point, it reads the density value from the raster
3. Higher density values result in more points being generated in that area
4. Points are randomly distributed within small cells around each sample point
5. Only points that fall within the polygon boundary are kept

## Requirements

- QGIS 3.0 or higher
- Python 3.x (included with QGIS)

## Troubleshooting

- **No points generated**: Ensure the polygon and raster layers overlap and have valid data
- **Points outside polygon**: This should not happen, but if it does, check coordinate reference systems match
- **Plugin not appearing**: Make sure the plugin folder is in the correct location and QGIS has been restarted

## License

This plugin is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.

## Author

Your Name - your.email@example.com

