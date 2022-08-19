from cProfile import label
import logging
from typing import Dict, Tuple, List

import pandas as pd
import numpy as np

from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

import lightgbm as lgb

import shap

def encode_and_split_data(model_input_table: pd.DataFrame,
                          parameters: Dict) -> Tuple:
  
  label_col = 'CATCONTRATADO'

  label_encode = LabelEncoder()
  model_input_table[label_col] = label_encode.fit_transform(
      model_input_table[label_col])
  
  labels = label_encode.inverse_transform([0, 1, 2])
  labels_dictionary = pd.DataFrame(zip(labels, [0, 1, 2]),
                                   columns=['sigla', 'classe'])
  
  y = model_input_table[label_col].values
  data = model_input_table.drop(label_col, axis=1)

  X = data[parameters["features"]]

  df_train, df_test, y_train, y_test = train_test_split(
      X, y, test_size=parameters["test_size"],
      stratify=y)

  df_train = df_train.reset_index(drop=True)
  df_test = df_test.reset_index(drop=True)
  
  return df_train, df_test, y_train, y_test, X, labels_dictionary

def train_model(df_train: pd.DataFrame,
                y_train: np.array,
                parameters: Dict):

  cat_cols = [
    'TIPOPRODUTO',
    'CODPRODUTO',
    'AGENCIA',
    'CODREGIONAL',
    'PROPOSTA_MULT'
    ]
  
  cat_cols = [c for c in cat_cols if c in df_train.columns.tolist()]

  d_train=lgb.Dataset(df_train, label=y_train,
                      categorical_feature=cat_cols)

  # parametros para modelo LightGMB
  params={}
  params['learning_rate'] = parameters["learning_rate"]
  params['boosting_type'] = parameters["boosting_type"]
  params['objective'] = parameters["objective"]
  params['metric'] = parameters["metric"]
  params['max_depth'] = parameters["max_depth"]
  params['num_leaves'] = parameters["num_leaves"]
  params['num_class'] = parameters["num_class"]
  
  # training 
  model = lgb.train(params, d_train, 30)

  return model

def evaluate_model(
    model, df_test: pd.DataFrame, y_test: np.array):

    y_pred = model.predict(df_test)
    argmax_y_pred = np.argmax(y_pred, axis=1)
    
    lgb_acc = accuracy_score(y_test, argmax_y_pred)

    logger = logging.getLogger(__name__)
    logger.info('acc score: %f.3', lgb_acc)

def shap_plot(model, X: pd.DataFrame):
  return 0
  model.params["objective"] = "multiclass"
  
  explainer = shap.TreeExplainer(model)
  shap_values = explainer.shap_values(X)
  
  shap.summary_plot(shap_values, X)

  # for name in X_one_hot.columns:
  #   shap.dependence_plot(name,
  #                        shap_values[1],
  #                        X_one_hot,
  #                       #  display_features=X
  #                        )
