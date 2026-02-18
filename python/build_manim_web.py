import os
import sys
import shutil
import subprocess
import argparse
import json
import logging

# Configure logging
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "research_agent.log")

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file, encoding='utf-8'),
                        logging.StreamHandler(sys.stdout)
                    ])
logger = logging.getLogger(__name__)

TEMPLATE = """import 'dart:html';
import 'dart:async';
import 'package:manim_web/manim.dart';
import 'package:manim_web/display/abstract_html_display.dart';

// --- USER GENERATED SCENE ---
{user_code}
// ----------------------------

void main() {
  var container = document.querySelector('#canvas-container');
  if (container == null) {
    print('Container #canvas-container not found!');
    return;
  }
  
  // Initialize Display
  var display = Canvas2DDisplay(container);
  
  // Initialize Scene
  // Note: TemplateScene must be defined in the user_code
  var scene = TemplateScene();
  
  // Bind Display to Scene and Run
  scene.bindDisplay(display);
  runScene(scene);
}
"""

def build_manim_web(code_path, project_dir="manim_project", output_name="visual", subfolder="manim_dist"):
    """
    Builds the Manim Web project with the provided Dart code.
    Streams output to stdout for real-time progress.
    """
    try:
        # 1. Read User Code  
        with open(code_path, 'r', encoding='utf-8') as f:
            user_code = f.read()

        # 2. Clean User Code (Remove imports as they must be at top)
        # We'll split lines, filter out imports, and keep the rest
        lines = user_code.split('\n')
        cleaned_lines = []
        extra_imports = []
        
        for line in lines:
            if line.strip().startswith("import "):
                # Check if it's a known package we already import or a standard dart lib
                if "package:manim_web" in line or "dart:html" in line or "dart:async" in line:
                    continue # Already in template
                else:
                    extra_imports.append(line)
            else:
                cleaned_lines.append(line)
                
        user_code_body = "\n".join(cleaned_lines)
        
        # Inject extra imports at top of template
        final_imports = "\n".join(extra_imports)
        
        # 3. Inject into Template
        if "class TemplateScene" not in user_code:
             logger.warning("User code does not contain TemplateScene class. Wrapping might fail.")

        # Insert extra imports after the standard ones
        template_with_imports = TEMPLATE.replace("import 'package:manim_web/display/abstract_html_display.dart';", 
                                                 "import 'package:manim_web/display/abstract_html_display.dart';\n" + final_imports)

        full_code = template_with_imports.replace("{user_code}", user_code_body)

        # 3. Write to manim_project/web/main.dart
        main_dart_path = os.path.join(project_dir, "web", "main.dart")
        os.makedirs(os.path.dirname(main_dart_path), exist_ok=True)
        
        with open(main_dart_path, 'w', encoding='utf-8') as f:
            f.write(full_code)
        
        print(f"-> Wrote generated code to {main_dart_path}")
        sys.stdout.flush()

        # 4. Run webdev build
        env = os.environ.copy()
        cmd = ["webdev", "build"]
        is_windows = (os.name == 'nt')
        
        print(f"-> Starting webdev build in {project_dir}...")
        sys.stdout.flush()

        process = subprocess.Popen(
            cmd,
            cwd=project_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=is_windows,
            bufsize=1
        )

        # Stream output line by line
        full_output = []
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                clean_line = line.strip()
                if clean_line:
                    print(f"      [webdev] {clean_line}")
                    sys.stdout.flush()
                    full_output.append(clean_line)
            process.stdout.close()

        return_code = process.wait()

        if return_code != 0:
            error_msg = "\n".join(full_output[-10:])
            print(f"-> [ERROR] Build failed with code {return_code}")
            return {"success": False, "error": f"Build failed: {error_msg}"}

        print("-> Build succeeded!")
        sys.stdout.flush()

        # 5. Copy Output to Public Directory
        build_output_dir = os.path.join(project_dir, "build")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Use a specific subfolder if provided
        target_dir = os.path.join(project_root, "research-agent-web", "public", subfolder)
        
        print(f"-> Deploying artifacts to {target_dir}...")
        sys.stdout.flush()
        
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        shutil.copytree(build_output_dir, target_dir)
        
        # Rename index.html to viz.html to avoid "index" routing magic/issues
        index_path = os.path.join(target_dir, "index.html")
        viz_path = os.path.join(target_dir, "viz.html")
        if os.path.exists(index_path):
            if os.path.exists(viz_path):
                os.remove(viz_path)
            os.rename(index_path, viz_path)
            print(f"-> Renamed index.html to viz.html")

        # Verify deployment
        if os.path.exists(viz_path):
            print(f"-> Artifacts deployed successfully. Size: {os.path.getsize(viz_path)} bytes")
        else:
            print(f"-> [ERROR] viz.html missing after deployment!")
            return {"success": False, "error": "Deployment verification failed"}

        return {"success": True, "url": f"/{subfolder}/viz.html"}

    except Exception as e:
        print(f"-> [EXCEPTION] {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Manim Web Project")
    parser.add_argument("--code-file", required=True, help="Path to file containing Dart code")
    parser.add_argument("--project-dir", default="manim_project", help="Path to Manim Web project")
    
    args = parser.parse_args()
    
    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    project_dir = os.path.join(base_dir, args.project_dir)
    
    result = build_manim_web(args.code_file, project_dir=project_dir)
    print(json.dumps(result))

