import random
import string

def generate_random_string(len: int):
  """
  Genera una stringa casuale di una data lunghezza.

  Args:
    len: La lunghezza desiderata della stringa.

  Returns:
    Una stringa casuale.
  """
  caratteri = string.ascii_letters + string.digits  
  return ''.join(random.choice(caratteri) for i in range(len))