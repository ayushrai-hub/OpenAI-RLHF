# ideal_completion.py

import os
import ast
import uuid
import base64
import logging
import http.client
import json
import boto3
from datetime import datetime


def execute_query(secret_identifier, area, database_connection, query, params=None):
    # Placeholder for executing a database query
    return []

def perform_query(secret_identifier, area, database_connection, query):
    # Placeholder for executing a query that modifies data
    pass

def get_process_executions(secret_identifier, area, database_connection, table):
    # Placeholder for fetching process executions
    
    return True, ["exec1"], ["id1"], "20240101"

# Initialize logger
log_instance = logging.getLogger()
log_instance.setLevel(level=logging.INFO)

# Retrieve environment configurations
environment = os.environ.get('ENVIRONMENT', 'dev')
area = os.environ.get('AREA_NAME', 'default_area')
area_code = os.environ.get('AREA_CODE', '000')
target_env = os.environ.get('TARGET_ENV', 'default')
database_connection = os.environ.get('DATABASE_CONNECTION', 'default_connection')
site = os.environ.get('SITE', 'default_site')
structure = os.environ.get('STRUCTURE', 'default_structure')

# Setup resources
secret_identifier = f'project-{area_code}-{site}-{environment}-service-{target_env}-cloud_secretsmanager_secret-link_database'
airflow_env = f'project-{area_code}-{site}-{environment}-service-{target_env}-env-pipeline_execution'
storage_bucket = f'project-{area_code}-{site}-{environment}-service-{target_env}-cloud-storage-bucket-data'
alert_service = f'project-{area_code}-{site}-{environment}-service-{target_env}-event-notification'

# Table mapping
table_mapping = {
    "table1": "prefix_table1",
    "table2": "prefix_table2"
}

def initiate_airflow_process(process_name, configuration, airflow_env, airflow_client):
    """
    Initiates an Airflow process and returns the result.

    :param process_name: The process to initiate.
    :param configuration: JSON with configuration details.
    :param airflow_env: Environment to use.
    :param airflow_client: MWAA client to initiate the process.
    :return: Output from the process initiation response.
    """
    # Generate MWAA token
    airflow_token = airflow_client.create_cli_token(Name=airflow_env)
    connection = http.client.HTTPSConnection(airflow_token['WebServerHostname'])

    # Payload to initiate the process
    payload = f"processes initiate {process_name} --configuration '{json.dumps(configuration)}'"
    log_instance.info(f'Payload: {payload}')

    headers = {
        'Authorization': 'Bearer ' + airflow_token['CliToken'],
        'Content-Type': 'text/plain'
    }

    # Make request to initiate the process
    connection.request("POST", "/aws_mwaa/cli", payload, headers)

    # Fetch the response
    response = connection.getresponse()
    response_data = response.read()

    # Decode and return the output
    data_string = response_data.decode("UTF-8")
    output = base64.b64decode(ast.literal_eval(data_string)['stdout'])
    return output

def lambda_processor(event, context):
    log_instance.info(f' Event: {event}')

    # Initialize the Airflow client once
    airflow_client = boto3.client('mwaa')

    # Get the statuses of all main tables
    all_table_status_query = "SELECT * FROM table_status"  
    table_status_tuple = execute_query(secret_identifier, area, database_connection, all_table_status_query)
    table_status_dict = dict(map(lambda kv: (kv[0], kv[1]), table_status_tuple))
    log_instance.info(f' Main tables and their processing statuses: {table_status_dict}')

    table_status_check = all(value == 1 for value in table_status_dict.values())
    log_instance.info(f' Main table(s) status check flag: {table_status_check}')

    # Reset all main tables' status if they are already processed
    if table_status_check:
        change_table_status_query = "UPDATE table_status SET status = 0"  
        perform_query(secret_identifier, area, database_connection, change_table_status_query)
        log_instance.info(' Completed updating all main table statuses!')

        update_ungo_status_query = "UPDATE ungo_events SET status = 0" 
        perform_query(secret_identifier, area, database_connection, update_ungo_status_query)
        log_instance.info(' Completed updating UNGO status!')

        # Initiate the validation process after updating table statuses
        log_instance.info('Initiating process_validation...')
        validation_conf = {'validation_process': 'process_validation'}
        output = initiate_airflow_process('process_validation', validation_conf, airflow_env, airflow_client)

    # Get the unprocessed main tables
    pending_table_query = "SELECT * FROM unprocessed_tables"  # Replace with actual query
    unprocessed_table_tuple = execute_query(secret_identifier, area, database_connection, pending_table_query)
    unprocessed_tables = list(map(lambda table: table[0], unprocessed_table_tuple))
    log_instance.info(f' Unprocessed main table(s): {unprocessed_tables}')

    # Iterate tables to initiate processing pipelines
    for table in unprocessed_tables:
        # Get the main table processing status
        table_status_query = "SELECT status FROM table_status WHERE table_name = %s"  
        table_status_res = execute_query(secret_identifier, area, database_connection, table_status_query, (table,))
        table_status = table_status_res[0][0] if table_status_res else None
        log_instance.info(f' Last execution status of the table {table}: {table_status}')

        if table_status in ('IN_PROGRESS', 'UNSUCCESSFUL'):
            log_instance.info(f' Skip processing {table} due to status: {table_status}!')
            continue

        # Fetch parent table statuses
        parent_status_query = "SELECT parent_table, status FROM parent_table_status WHERE table_name = %s" 
        parent_status_tuple = execute_query(secret_identifier, area, database_connection, parent_status_query, (table,))
        parent_status_dict = dict(map(lambda kv: (kv[0], kv[1]), parent_status_tuple))
        log_instance.info(f' Parent tables status of the table {table}: {parent_status_dict}')

        parent_status_check = all(value == 1 for value in parent_status_dict.values())
        if not parent_status_check:
            log_instance.info(f' Skip processing {table} as its parent tables are still pending!')
            continue

        uid = str(uuid.uuid4())
        process_initiation_time = datetime.now().strftime('%Y%m%d%H%M%S')

        trigger, executions, identifiers, batch_timestamp = get_process_executions(secret_identifier, area, database_connection, table)

        if trigger:
            table_schema_query = "SELECT schema_name FROM table_schema WHERE table_name = %s" 
            table_schema_tuple = execute_query(secret_identifier, area, database_connection, table_schema_query, (table,))
            table_schema = table_schema_tuple[0][0] if table_schema_tuple else structure

            table_prefix = table_mapping.get(table, table)

            configuration = {
                'main_table': table,
                'executions': executions,
                'identifiers': identifiers,
                'uid': uid,
                'secret_identifier': secret_identifier,
                'database_connection': database_connection,
                'structure': table_schema,
                'environment': environment,
                'area': area,
                'area_code': area_code,
                'batch_timestamp': batch_timestamp,
                'site': site,
                'target_env': target_env,
                'storage_bucket': storage_bucket,
                'table_prefix': table_prefix,
                'alert_service': alert_service,
                'process_initiation_time': process_initiation_time
            }

            output = initiate_airflow_process(table, configuration, airflow_env, airflow_client)
        else:
            log_instance.info(f' Skip processing {table} due to DAG initiation status: {trigger}')

    return "Lambda process completed."