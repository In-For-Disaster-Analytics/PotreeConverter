#!/usr/bin/env python3
"""
Potree Scene Generator - JSON5 Scene File Post-Processor

This script generates JSON5 scene configuration files from PotreeConverter output,
enabling complete 3D scene definitions with camera settings, point cloud metadata,
and interactive elements.

Usage:
    python potree_scene_generator.py <metadata.json> [options]
    python potree_scene_generator.py /path/to/output/metadata.json --scene-name my_scene
"""

import json
import argparse
import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple


class PotreeSceneGenerator:
    """Generates JSON5 scene files from PotreeConverter metadata."""
    
    def __init__(self):
        self.default_classifications = {
            0: {"name": "Created", "color": [0.5, 0.5, 0.5], "visible": True},
            1: {"name": "Unclassified", "color": [0.5, 0.5, 0.5], "visible": True},
            2: {"name": "Ground", "color": [0.63, 0.32, 0.18], "visible": True},
            3: {"name": "Low Vegetation", "color": [0.0, 1.0, 0.0], "visible": True},
            4: {"name": "Medium Vegetation", "color": [0.0, 0.8, 0.0], "visible": True},
            5: {"name": "High Vegetation", "color": [0.0, 0.6, 0.0], "visible": True},
            6: {"name": "Building", "color": [1.0, 0.66, 0.0], "visible": True},
            7: {"name": "Low Point", "color": [1.0, 0.0, 1.0], "visible": True},
            8: {"name": "Model Key-point", "color": [1.0, 0.0, 0.0], "visible": True},
            9: {"name": "Water", "color": [0.0, 0.0, 1.0], "visible": True},
            10: {"name": "Rail", "color": [1.0, 1.0, 0.0], "visible": True},
            11: {"name": "Road Surface", "color": [0.4, 0.4, 0.4], "visible": True},
            12: {"name": "Reserved", "color": [0.3, 0.3, 0.3], "visible": True},
            13: {"name": "Wire - Guard", "color": [0.9, 0.9, 0.0], "visible": True},
            14: {"name": "Wire - Conductor", "color": [0.8, 0.8, 0.0], "visible": True},
            15: {"name": "Transmission Tower", "color": [0.7, 0.7, 0.0], "visible": True},
            16: {"name": "Wire - Connector", "color": [0.6, 0.6, 0.0], "visible": True},
            17: {"name": "Bridge Deck", "color": [0.5, 0.3, 0.1], "visible": True},
            18: {"name": "High Noise", "color": [1.0, 0.0, 0.5], "visible": True}
        }
    
    def load_metadata(self, metadata_path: Path) -> Dict[str, Any]:
        """Load PotreeConverter metadata.json file."""
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metadata from {metadata_path}: {e}")
            sys.exit(1)
    
    def calculate_camera_position(self, bounds: Dict[str, List[float]], offset_multiplier: float = 1.5) -> Tuple[List[float], List[float]]:
        """Calculate optimal camera position and target from bounding box."""
        if isinstance(bounds, dict):
            min_coords = bounds.get("min", [0, 0, 0])
            max_coords = bounds.get("max", [1000, 1000, 100])
            min_x, min_y, min_z = min_coords
            max_x, max_y, max_z = max_coords
        else:
            # Legacy format: bounds as array [min_x, min_y, min_z, max_x, max_y, max_z]
            min_x, min_y, min_z = bounds[:3]
            max_x, max_y, max_z = bounds[3:]
        
        # Calculate center and size
        center = [(min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2]
        size_x = max_x - min_x
        size_y = max_y - min_y
        size_z = max_z - min_z
        max_dimension = max(size_x, size_y, size_z)
        
        # Position camera at distance for good overview
        distance = max_dimension * offset_multiplier
        camera_position = [
            center[0] + distance * 0.7,  # Slightly offset for better angle
            center[1] + distance * 0.7,
            center[2] + max_dimension * 0.3  # Elevated view
        ]
        
        return camera_position, center
    
    def generate_scene(self, metadata: Dict[str, Any], scene_name: str, **options) -> str:
        """Generate JSON5 scene configuration."""
        
        # Extract metadata information  
        bounds = metadata.get("boundingBox", {"min": [0, 0, 0], "max": [1000, 1000, 100]})
        total_points = metadata.get("points", 0)
        
        # Calculate camera settings
        camera_pos, camera_target = self.calculate_camera_position(bounds)
        
        # Override with user settings if provided
        if options.get("camera_position"):
            camera_pos = options["camera_position"]
        if options.get("camera_target"):
            camera_target = options["camera_target"]
        
        # Determine point cloud URL
        base_url = options.get("base_url", "")
        if base_url:
            # If base URL is provided, use it as the full URL
            pointcloud_url = base_url
        else:
            # Default to relative path
            pointcloud_url = "./metadata.json"
        
        # Scene configuration following Potree format
        scene_config = {
            "type": "Potree",
            "version": 1.7,
            "settings": {
                "pointBudget": options.get("point_budget", self._calculate_point_budget(total_points)),
                "fov": options.get("fov", 60),
                "edlEnabled": options.get("edl_enabled", True),
                "edlRadius": 1.4,
                "edlStrength": 0.4,
                "background": options.get("background", "gradient"),
                "minNodeSize": 30,
                "showBoundingBoxes": False
            },
            "view": {
                "position": camera_pos,
                "target": camera_target
            },
            "classification": self._format_classifications(),
            "pointclouds": [
                {
                    "name": scene_name,
                    "url": pointcloud_url,
                    "position": metadata.get("offset", [0.0, 0.0, 0.0]),
                    "rotation": [0, 0, 0, "XYZ"],
                    "scale": [1, 1, 1],
                    "material": {
                        "activeAttributeName": "rgba",
                        "size": 1,
                        "minSize": 2,
                        "pointSizeType": "ADAPTIVE"
                    }
                }
            ],
            "measurements": [],
            "volumes": [],
            "cameraAnimations": [],
            "profiles": [],
            "annotations": [],
            "orientedImages": [],
            "geopackages": []
        }
        
        return self._format_json5(scene_config)
    
    def _format_classifications(self) -> Dict[str, Dict[str, Any]]:
        """Format classifications in Potree scene format."""
        formatted = {}
        for key, value in self.default_classifications.items():
            formatted[str(key)] = {
                "visible": value["visible"],
                "name": value["name"].lower(),
                "color": value["color"] + [1]  # Add alpha channel
            }
        
        # Add DEFAULT classification
        formatted["DEFAULT"] = {
            "visible": True,
            "name": "default",
            "color": [0.3, 0.6, 0.6, 0.5]
        }
        
        return formatted
    
    def _calculate_point_budget(self, total_points: int) -> int:
        """Calculate appropriate point budget based on total points."""
        if total_points > 50_000_000:
            return 5_000_000
        elif total_points > 10_000_000:
            return 2_000_000
        elif total_points > 1_000_000:
            return 1_000_000
        else:
            return min(500_000, total_points)
    
    def _format_json5(self, data: Dict[str, Any]) -> str:
        """Format dictionary as JSON5 with tabs like Potree format."""
        json_str = json.dumps(data, indent='\t')
        
        # Convert to JSON5 format (remove quotes from keys where possible)
        lines = json_str.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Remove quotes from simple keys
            line = re.sub(r'\"([a-zA-Z_$][a-zA-Z0-9_$]*)\"\s*:', r'\1:', line)
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def generate_enhanced_html(self, html_template_path: Path, scene_name: str, output_path: Path):
        """Generate enhanced HTML template with JSON5 scene loading."""
        try:
            with open(html_template_path, 'r') as f:
                template = f.read()
        except FileNotFoundError:
            print(f"Warning: HTML template not found at {html_template_path}")
            return
        
        # Enhanced viewer initialization with scene loading
        scene_loading_code = f'''
        // Load JSON5 scene file if available
        fetch('./{scene_name}.json5')
            .then(response => response.text())
            .then(sceneData => {{
                // Parse JSON5 content (remove comments for basic JSON parsing)
                const jsonData = sceneData.replace(/\/\\*[\\s\\S]*?\\*\/|\\/\\/.*$/gm, '').replace(/,(\\s*[}}\\]])/g, '$1');
                const scene = JSON.parse(jsonData);
                
                console.log('Loaded scene configuration:', scene.name);
                
                // Apply viewer settings from scene
                if (scene.view) {{
                    if (scene.view.fov) viewer.setFOV(scene.view.fov);
                    if (scene.view.pointBudget) viewer.setPointBudget(scene.view.pointBudget);
                    if (scene.view.edlEnabled !== undefined) viewer.setEDLEnabled(scene.view.edlEnabled);
                    if (scene.view.background) viewer.setBackground(scene.view.background);
                }}
                
                // Load point clouds from scene configuration
                if (scene.pointclouds && scene.pointclouds.length > 0) {{
                    const pc = scene.pointclouds[0];
                    Potree.loadPointCloud(pc.url, pc.name, e => {{
                        let pointcloud = e.pointcloud;
                        
                        // Apply material settings from scene
                        if (pc.materialSettings) {{
                            let material = pointcloud.material;
                            if (pc.materialSettings.size) material.size = pc.materialSettings.size;
                            if (pc.materialSettings.pointSizeType) material.pointSizeType = Potree.PointSizeType[pc.materialSettings.pointSizeType];
                            if (pc.materialSettings.shape) material.shape = Potree.PointShape[pc.materialSettings.shape];
                            if (pc.materialSettings.activeAttributeName) material.activeAttributeName = pc.materialSettings.activeAttributeName;
                        }}
                        
                        viewer.scene.addPointCloud(pointcloud);
                        
                        // Set camera position from scene configuration
                        if (scene.view && scene.view.position && scene.view.target) {{
                            viewer.scene.view.position.set(...scene.view.position);
                            viewer.scene.view.lookAt(new THREE.Vector3(...scene.view.target));
                        }} else {{
                            viewer.fitToScreen();
                        }}
                    }});
                }}
            }})
            .catch(error => {{
                console.log('Scene file not found, using default point cloud loading');
                // Fallback to default behavior
                <!-- INCLUDE POINTCLOUD -->
            }});
        '''
        
        # Replace the pointcloud loading section
        if '<!-- INCLUDE POINTCLOUD -->' in template:
            template = template.replace('<!-- INCLUDE POINTCLOUD -->', scene_loading_code)
        
        # Write enhanced template
        with open(output_path, 'w') as f:
            f.write(template)
        
        print(f"Enhanced HTML template generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate JSON5 scene files from PotreeConverter output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python potree_scene_generator.py output/metadata.json --scene-name my_scene
  python potree_scene_generator.py output/metadata.json --scene-name my_scene --camera-position 1000,1000,300
  python potree_scene_generator.py output/metadata.json --scene-name my_scene --fov 45 --point-budget 3000000
        """
    )
    
    parser.add_argument("metadata", type=Path, help="Path to PotreeConverter metadata.json file")
    parser.add_argument("--scene-name", "-n", default="scene", help="Name for the generated scene")
    parser.add_argument("--output", "-o", type=Path, help="Output directory (default: same as metadata)")
    parser.add_argument("--base-url", "-u", help="Base URL for point cloud data (e.g., https://example.com/path/to/metadata.json)")
    parser.add_argument("--camera-position", help="Camera position as x,y,z")
    parser.add_argument("--camera-target", help="Camera target as x,y,z")
    parser.add_argument("--fov", type=float, default=60, help="Field of view in degrees")
    parser.add_argument("--point-budget", type=int, help="Point rendering budget")
    parser.add_argument("--background", choices=["gradient", "skybox", "solid"], default="gradient", help="Background type")
    parser.add_argument("--edl-enabled", type=bool, default=True, help="Enable eye-dome lighting")
    parser.add_argument("--generate-html", action="store_true", help="Generate enhanced HTML template")
    parser.add_argument("--html-template", type=Path, help="Path to HTML template file")
    
    args = parser.parse_args()
    
    # Validate metadata file
    if not args.metadata.exists():
        print(f"Error: Metadata file not found: {args.metadata}")
        sys.exit(1)
    
    # Set output directory
    output_dir = args.output if args.output else args.metadata.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse camera settings
    options = {
        "fov": args.fov,
        "background": args.background,
        "edl_enabled": args.edl_enabled
    }
    
    if args.camera_position:
        try:
            options["camera_position"] = [float(x.strip()) for x in args.camera_position.split(',')]
        except ValueError:
            print("Error: Camera position must be in format 'x,y,z'")
            sys.exit(1)
    
    if args.camera_target:
        try:
            options["camera_target"] = [float(x.strip()) for x in args.camera_target.split(',')]
        except ValueError:
            print("Error: Camera target must be in format 'x,y,z'")
            sys.exit(1)
    
    if args.point_budget:
        options["point_budget"] = args.point_budget
    
    if args.base_url:
        options["base_url"] = args.base_url
    
    # Generate scene
    generator = PotreeSceneGenerator()
    metadata = generator.load_metadata(args.metadata)
    
    print(f"Generating JSON5 scene from: {args.metadata}")
    print(f"Scene name: {args.scene_name}")
    
    scene_content = generator.generate_scene(metadata, args.scene_name, **options)
    
    # Write scene file
    scene_file = output_dir / f"{args.scene_name}.json5"
    with open(scene_file, 'w') as f:
        f.write(scene_content)
    
    print(f"✅ JSON5 scene file generated: {scene_file}")
    
    # Generate enhanced HTML if requested
    if args.generate_html:
        if args.html_template:
            html_template = args.html_template
        else:
            # Look for template in common locations
            possible_templates = [
                output_dir / "viewer_template.html",
                output_dir.parent / "viewer_template.html",
                Path(__file__).parent.parent / "resources/page_template/viewer_template.html"
            ]
            html_template = None
            for template_path in possible_templates:
                if template_path.exists():
                    html_template = template_path
                    break
        
        if html_template:
            html_output = output_dir / f"{args.scene_name}.html"
            generator.generate_enhanced_html(html_template, args.scene_name, html_output)
        else:
            print("Warning: HTML template not found. Specify --html-template or place viewer_template.html in output directory")
    
    print(f"\n🎉 Scene generation complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Scene file: {scene_file.name}")
    
    if args.generate_html and html_template:
        print(f"🌐 HTML file: {args.scene_name}.html")


if __name__ == "__main__":
    main()