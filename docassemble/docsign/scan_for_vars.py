from docassemble.base.pandoc import word_to_markdown
from docassemble.base.util import DAFileList, Individual, Address
from docassemble.base.functions import value
from docassemble.base.parse import docx_variable_fix
import re
 
__all__ = ['get_fields','gather_fields']

def gather_fields(field_list, exclude=[]):
  """Trigger the gathering of a list of fields (strings) in Docassemble"""
  for field in field_list:
    if not field in exclude:
      if isinstance(value(field),Individual):
        value(field + '.name.first')
      elif isinstance(value(field),Address):
        value(field + '.address')
      else:
        value(field) # use Docassemble function to require the definition of the field

def get_fields(the_file, include_attributes=False):
  """ Get the list of fields needed inside a template file (PDF or Docx Jinja tags)"""
  if isinstance(the_file,DAFileList):
    is_pdf = the_file[0].mimetype == 'application/pdf'
  else:
    is_pdf = the_file.mimetype == 'application/pdf'
  if is_pdf:
    return [field[0] for field in the_file[0].get_pdf_fields()]
  else:
    result_file = word_to_markdown(the_file.path(), 'docx')
    if result_file is None:
      # fields = word("Error: no fields could be found in the file")
      return []
    else:
      with open(result_file.name, 'rU', encoding='utf-8') as fp:
        result = fp.read()
        fields = set()
        methods = r"(.*)(\..*\(\))"
        for variable in re.findall(r'{{ *([^\} ]+) *}}', result):
          variable = variable.replace("\\","")
          matches = re.match(methods, variable)
          if matches:
            fields.add(matches.groups()[0])
          else:           
            fields.add(variable)
      for variable in re.findall(r'{%[a-z]* for [A-Za-z\_][A-Za-z0-9\_]* in *([^\} ]+) *%}', result): # look for all Jinja2 tags with fields, including attributes
        variable = variable.replace("\\","")
        matches = re.match(methods, variable)
        if matches:
          fields.add(matches.groups()[0])
        else:           
          fields.add(variable)
        del matches         
      del fp
    del result_file
    fields = [x for x in fields if not '(' in x] # strip out functions/method calls
    return fields