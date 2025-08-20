from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any
import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from some_module import data_partitioning, load_models, forecast_single_article
import pyspark.sql.functions as F

def forecast_all_items(
    client_config: Dict[str, Any],
    model_builder_config: Dict[str, Any]
) -> DataFrame:
    """
    Forecast all items based on the given client configuration and model builder configuration.

    Args:
        client_config (dict): The client configuration.
        model_builder_config (dict): The model builder configuration.
    """

    back_test = client_config["forecaster"]["back_test"]
    article_level = client_config["article_level"]
    location_level = client_config["location_level"]

    transaction, simulation = data_partitioning(
        client_config, model_builder_config
    )

    target_article_locations = (
        transaction
        .select(article_level, location_level)
        .distinct()
        .collect()
    )

    target_article_locations = [
        [row[article_level], row[location_level]]
        for row in target_article_locations
    ]

    meta_info, model_lookup = load_models(client_config)
    forecasts = pd.DataFrame()

    df_logger_03.info("Starting forecasts ...")

    def forecast_task(target_article, target_location):
        df_logger_03.info(f"Forecasting for {target_article} in {target_location} ...")

        target_transaction = (
            transaction
            .filter(
                (F.col(article_level) == target_article) &
                (F.col(location_level) == target_location)
            )
        )

        target_simulation = (
            simulation
            .filter(
                (F.col(article_level) == target_article) &
                (F.col(location_level) == target_location)
            )
        )

        forecasts_single = forecast_single_article(
            client_config,
            target_article,
            target_location,
            target_transaction,
            target_simulation,
            meta_info,
            model_lookup,
        )

        return forecasts_single

    # Parallel execution using ProcessPoolExecutor
    num_workers = min(32, len(target_article_locations))  # Adjust based on your system's capacity
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_location = {
            executor.submit(forecast_task, i[0], i[1]): i for i in target_article_locations
        }

        for future in as_completed(future_to_location):
            result = future.result()
            forecasts = pd.concat([forecasts, result], axis=0)

    spark = SparkSession.builder.getOrCreate()
    return spark.createDataFrame(forecasts)
