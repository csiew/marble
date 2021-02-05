import os
import sys
import numpy
import json


DEPENDENCIES = {
  'jq': {
    'linux': '/usr/bin/jq'
  },
  'yarn': {
    'linux': '/usr/bin/yarnpkg'
  }
}

CONFIG_PATH = os.getenv('HOME') + '/.config/marble.config.json'
FRAMEWORKS = ['express', 'react', 'vue']

'''
Flag code:
-1  Expecting indefinite number of values
0   Not expecting value
>0  Expecting fixed number of values
'''
FLAGS = {
  'general': {
    '--ping': 0,    # Test flag that skips directory generation
    '--debug': 0,
    '--install-packages': -1
  },
  'frameworks': {
    'express': {
      '--use-nodemon': 0,
      '--use-express-session': 0
    }
  }
}


class Generator:
  def __init__(self, id, properties, flags: {}):
    self.id = id
    self.properties = properties
    self.flags = flags


class ExpressGenerator(Generator):
  def __init__(self, config, properties, flags):
    Generator.__init__(self, 'express', properties, flags)
    self.config = config
    self.project_path = ''
  
  def main(self) -> int:
    if '--ping' in self.flags:
      print("Debug mode exits before project directory creation")
      exit(0)

    # Validate project properties
    if len(self.properties['name']) == 0:
      print("Project name is empty")
      exit(1)
    try:
      self.project_path = self.config['properties']['projects_directory'] + '/' + self.properties['name']
      if os.path.exists(self.project_path):
        print("Project directory already exists")
        exit(1)
    except:
      print("Project configuration or properties unreadable")
      exit(1)

    # Build project
    if os.path.exists(self.config['properties']['projects_directory']):
      try:
        os.mkdir(self.project_path)
      except:
        print("Unable to create project directory")
        exit(1)
      os.chdir(self.project_path)
      os.system("touch hello_world.txt")
      os.system("echo 'Hello world!' > hello_world.txt")
    else:
      print("Unable to find projects directory")
      exit(1)
    
    exit(0)


class App:
  def __init__(self):
    self.config = {}
    self.framework = ''
    self.properties = {
      'name': ''
    }
    self.flags = {}
  
  def check_dependencies(self):
    #TODO: Remove platform check when implementing support for other platforms
    if sys.platform != "linux":
      print("Support for macOS and Windows is coming soon")
      exit(1)
    
    for dep_name, dep_path in DEPENDENCIES.items():
      try:
        if not os.path.exists(dep_path[sys.platform]):
          print("Dependency not met: " + dep_name)
          exit(1)
      except:
        print("Could not determine system platform")
        exit(1)
  
  def check_config_path(self):
    if os.path.exists(CONFIG_PATH):
      with open(CONFIG_PATH, "r") as user_prefs:
        self.config = json.load(user_prefs)
        projects_directory_props = self.config['properties']['projects_directory']
        if (projects_directory_props.startswith('$HOME', 0)):
          self.config['properties']['projects_directory'] = os.getenv('HOME') + projects_directory_props[len('$HOME'):]
          print("New project directory will be generated in: " + self.config['properties']['projects_directory'])
      user_prefs.close()
    else:
      print("Config file not found at: " + CONFIG_PATH)
      exit(1)
  
  def print_usage(self):
    print("Usage: /usr/bin/python3 marble.py [framework] [project name] [...flags]")
  
  def is_valid_framework(self, framework_arg) -> int:
    if (FRAMEWORKS.__contains__(framework_arg)):
      return 0
    return 1
  
  def process_flags(self, flag_args) -> int:
    if len(flag_args) > 0:
      last_flag = ''
      for arg in flag_args:
        if (arg.startswith('--', 0)):
          self.flags[arg] = ''
          if (arg in FLAGS['general'] and FLAGS['general'][arg] != 0) or (arg in FLAGS['frameworks'][self.framework] and FLAGS['frameworks'][self.framework][arg] != 0):
            last_flag = arg
        else:
          if len(last_flag) > 0 and last_flag in self.flags:
            self.flags[last_flag] = arg
            last_flag = ''
          else:
            pass
    return 0

  def main(self) -> int:
    self.check_dependencies()
    self.check_config_path()
    if len(sys.argv) >= 3:

      # Get framework option
      if self.is_valid_framework(sys.argv[1]) == 0:
        self.framework = sys.argv[1]
      else:
        print("Framework not supported: " + sys.argv[1])
        print("Supported frameworks:")
        for framework in FRAMEWORKS:
          print(" - " + framework)
        self.print_usage()
        exit(1)
      
      # Get project name
      if sys.argv[2].startswith('--', 0):
        print("Invalid project name: do not start with dashes")
        exit(1)
      self.properties['name'] = sys.argv[2]

      # Get project build options via flags
      flag_args = numpy.array(sys.argv[1:])
      if self.process_flags(flag_args) == 0:
        if self.framework == 'express':
          exit(ExpressGenerator(self.config, self.properties, self.flags).main())
    else:
      if self.process_flags(numpy.array(sys.argv[1:])) == 1:
        self.print_usage()
        exit(1)
    exit(0)


if __name__ == '__main__':
  exit(App().main())