"""
This is a boilerplate pipeline 'data_science'
generated using Kedro 0.18.2
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import encode_and_split_data, evaluate_model, shap_plot, train_model


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=encode_and_split_data,
                inputs=["model_input_table", "params:split_data_options"],
                outputs=["df_train", "df_test", "y_train", "y_test", "X", "labels_dictionary"],
                name="encode_and_split_data_node",
            ),
            node(
                func=train_model,
                inputs=["df_train", "y_train", "params:model_options"],
                outputs="model",
                name="train_model_node",
            ),
            node(
                func=evaluate_model,
                inputs=["model", "df_test", "y_test"],
                outputs=None,
                name="evaluate_model_node",
            ),
            
            node(
                func=shap_plot,
                inputs=["model", "X"],
                outputs=None,
                name="shap_plot_node",
            ),
        ]
    )