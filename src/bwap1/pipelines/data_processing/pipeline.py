"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.2
"""

from kedro.pipeline import Pipeline, node, pipeline

from bwap1.pipelines.data_processing.nodes import create_model_input_table, preprocess_bwa_cli_prod_proposta


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=preprocess_bwa_cli_prod_proposta,
                inputs="bwa_cli_prod_proposta",
                outputs="preprocessed_bwa_cli_prod_proposta",
                name="preprocessed_bwa_cli_prod_proposta_node",
            ),

            node(
                func=create_model_input_table,
                inputs="preprocessed_bwa_cli_prod_proposta",
                outputs="model_input_table",
                name="create_model_input_table_node",
            ),
        ]
    )
