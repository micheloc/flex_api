import pyodbc 

class conn :
  # Certifique-se de que os detalhes da string de conexão estão corretos
  context = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=MICRO-06\MICRO6;DATABASE=Mundo_Importados;UID=sa;PWD=Tenho1acessodatabase.')