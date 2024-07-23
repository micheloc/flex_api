from server.instance import conn

def generatesalesgraph(dt_inicial, dt_final, idstatus, idcategoria, idusuario) : 
  cursor = conn.context.cursor()
  cursor.execute(f"SELECT * FROM fGetSalesGraph('{dt_inicial}', '{dt_final}', '{idstatus}', '{idcategoria}', '{idusuario}')")

  # Obtenha o nome das colunas
  columns = [column[0] for column in cursor.description]

  # Obtenha os resultados da consulta
  results = cursor.fetchall()

  # Combine o nome das colunas com os resultados
  results_with_header = [dict(zip(columns, row)) for row in results]

  return results_with_header



