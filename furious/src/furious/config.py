"""
Functions for parsing and saving configuration files for the
L{furious.driver.FuriousDriver} class.

@author: Ian Phillips
"""

import os

class FuriousConfigError(Exception):
  """
  This exception is raised when L{parse_config()} below finds problems 
  in a config file.
  """
  def __init__(self, filename, line, message):
    """
    Constructor.
    @param filename: the name of the config file in which the error was found
    @type filename: string
    @param line: the line number on which the error was found
    @type line: int
    @param message: a message describing the error
    @type message: string
    """
    self.file = filename
    self.line = line
    self.msg = message

  def __str__(self):
    return "File %s is invalid at line %i: %" (self.file, self.line, self.msg)

###  end FuriousConfigError  ###




def parse_config(filename):
  """
  Reads the given configuration file and returns a dictionary
  of its values.
  @param filename: the name of the config file to be parsed
  @type filename: string
  @return: a dictionary of the parsed, cleaned-up config settings
  """
  config = {}
  file = open(filename)
  line_num = 0
  for line in file:
    line_num += 1
    # Remove comments
    comment_begin = line.find("#")
    if comment_begin > -1:  # There's a comment
      line = line[:comment_begin]  # slice it out

    # Skip empty lines
    line = line.strip()
    if len(line) == 0:
      continue

    # Split line into parts and clean them up
    parts = line.split("=")
    if len(parts) < 2:
      raise FuriousConfigError(filename, line_num, 
          "Format should be: key=val[,val...]" )
    key = parts[0].strip().lower()  # key names should always be lowercase
    vals = parts[1].split(",")

    for i in range(len(vals)):
      vals[i] = vals[i].strip()

    # Take the appropriate action depending on the first value in
    # the line.
    if key == "servo":
      if key not in config:
        config[key] = {}
      # format: servo=name, id, min, center, max
      # eg:     servo=throttle, 6, 220, 280, 320
      if len(vals) < 5:
        raise FuriousConfigError(filename, line_num,
          "Servo format is: servo=name,id,min,center,max" )
      name = vals[0]
      config[key][name] = [ int(x) for x in vals[1:] ]

    elif key == "odometer":
      # format: odometer=meters-per-tick
      # eg:     odometer=0.33
      config[key] = float(vals[0])

    # TODO: Add battery level customization here

  file.close()
  return config

###  end parse_config()  ###



def save_config(config, filename):
  """
  Takes a dictionary of configuration settings and a filename and saves 
  the configuration to that file.
  @param config: a dictionary of configuration settings in the same format
    as is generated by parse_config()
  @type config: dict
  @param filename: the name of the file to which the given configuration
    will be saved
  @type filename: string
  """
  file = open(filename)
  lines = []
  for line in file:
    # Default behaviour is to keep the line intact -- it might be a
    # comment or useful blank.
    updated_line = line
    if "=" in line:
      parts = line.split("=")
      key = parts[0].strip()
      val = parts[1].strip()
      if key == "servo":
        vals = val.split(",")
        sname = vals[0].strip()
        svals = ",".join( [ str(x) for x in config['servo'][sname] ] )
        updated_line = "%s=%s,%s" % (key, sname, svals)
      elif key == "odometer":
        updated_line = "%s=%.2f" % (key, config['odometer'])

    if not updated_line.endswith(os.linesep):
      updated_line = updated_line + os.linesep
    lines.append(updated_line)

  file.close()
  file = open(filename, "w")
  file.writelines(lines)
  file.close()

###  end save_config()  ###

