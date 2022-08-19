import pandas as pd

def _format_and_convert_to_float(x: pd.Series) -> pd.Series:
  x = x.astype(str).str.replace(',','.')
  x = _tratar_espaco_vazio_como_zero(x)
  return x.astype(float)

def _tratar_espaco_vazio_como_nan(x: pd.Series) -> pd.Series:
  return x.replace(' ', 'nan')

def _tratar_espaco_vazio_como_zero(x: pd.Series) -> pd.Series:
  return x.replace(' ', 0).astype(float)

def _tratar_nan_como_zero(x: pd.Series) -> pd.Series:
  return x.fillna(0)

def _tratar_valorsugerido_nan_como_igual_solicitado(
    sugerido: pd.Series, solicitado: pd.Series) -> pd.Series:
  tempdf = pd.concat([sugerido, solicitado], axis=1)
  tempdf['VALORSUGERIDO'].fillna(tempdf['VALORSOLICITADO'], inplace=True)
  return tempdf['VALORSUGERIDO']
  
def _padronizar_prazo(prazo: pd.Series, uni: pd.Series) -> pd.Series:
  dict_conversao = {
      'D': 1,
      'M': 30,
      'S': 180,
      'A': 365
  }
  tempdf = pd.concat([prazo, uni], axis=1)
  tempdf['unidade_em_dias'] = tempdf['UNIDADEPRAZO'].map(dict_conversao)
  tempdf['PRAZODIAS'] = tempdf['PRAZOSOLICITADO'] * tempdf['unidade_em_dias']
  return tempdf['PRAZODIAS']

def _categorizar(x: pd.Series) -> pd.Series:
  return x.astype('category').cat.codes

def preprocess_bwa_cli_prod_proposta(
    bwa_cli_prod_proposta:pd.DataFrame) -> pd.DataFrame:

    colunas_valor = [col for col in bwa_cli_prod_proposta.columns
                     if col.startswith(("VALOR", "VLR"))]

    for coluna in colunas_valor:
      bwa_cli_prod_proposta[coluna] = _format_and_convert_to_float(
          bwa_cli_prod_proposta[coluna]
          )
        
    bwa_cli_prod_proposta['TAXASOLICITADA'] = _format_and_convert_to_float(
        bwa_cli_prod_proposta['TAXASOLICITADA']
    )
    
    # bwa_cli_prod_proposta['VALORSUGERIDO'] =\
    #  _tratar_valorsugerido_nan_como_igual_solicitado(
    #     bwa_cli_prod_proposta['VALORSUGERIDO'],
    #     bwa_cli_prod_proposta['VALORSOLICITADO']
    # )

    bwa_cli_prod_proposta['VALORCONTRATADO'] = _tratar_nan_como_zero(
        bwa_cli_prod_proposta['VALORCONTRATADO']
        )
        
    bwa_cli_prod_proposta['PRAZOSOLICITADO'] = _tratar_espaco_vazio_como_zero(
        bwa_cli_prod_proposta['PRAZOSOLICITADO']
        )
    
    for coluna in ['TIPOPRODUTO',
                   'CODPRODUTO',
                   'AGENCIA',
                   'CODREGIONAL',
                   ]:
      bwa_cli_prod_proposta[coluna] = _categorizar(bwa_cli_prod_proposta[coluna])
      
    # criacao de coluna
    bwa_cli_prod_proposta['PRAZODIAS'] = _padronizar_prazo(
        bwa_cli_prod_proposta['PRAZOSOLICITADO'],
        bwa_cli_prod_proposta['UNIDADEPRAZO']
        )
    
    # criacao de coluna
    bwa_cli_prod_proposta['DIF_CONTRATADO_SOLICITADO'] =\
     bwa_cli_prod_proposta['VALORCONTRATADO'] -\
     bwa_cli_prod_proposta['VALORSOLICITADO']
    
    # criacao de coluna
    bwa_cli_prod_proposta['DIF_SUGERIDO_SOLICITADO'] =\
     bwa_cli_prod_proposta['VALORSUGERIDO'] -\
     bwa_cli_prod_proposta['VALORSOLICITADO']

    # criacao de coluna
    bwa_cli_prod_proposta['PROPOSTA_MULT'] =\
     bwa_cli_prod_proposta['IDPROPOSTA'].duplicated(keep=False)
    
    # criacao de coluna
    bwa_cli_prod_proposta['CATCONTRATADO'] = 'P'

    bwa_cli_prod_proposta.loc[
        bwa_cli_prod_proposta['VALORCONTRATADO']==0,
        'CATCONTRATADO'] = 'N'

    bwa_cli_prod_proposta.loc[
        bwa_cli_prod_proposta['VALORCONTRATADO']==\
        bwa_cli_prod_proposta['VALORSOLICITADO'],
        'CATCONTRATADO'] = 'F'

    return bwa_cli_prod_proposta

def create_model_input_table(
    bwa_cli_prod_proposta:pd.DataFrame) -> pd.DataFrame:

    bwa_cli_prod_proposta =\
      bwa_cli_prod_proposta[[
          'CATCONTRATADO',
          'TIPOPRODUTO',
          'CODPRODUTO',
          'AGENCIA',
          'CODREGIONAL',
          'PROPOSTA_MULT',
          'VALORSOLICITADO',
          'VALORSUGERIDO',
          'VALORDEFERIDO',
          'VALORCONTRATADO',
          'TAXASOLICITADA',
          'PRAZODIAS'
          ]]

    return bwa_cli_prod_proposta