# File path and imports remain unchanged

@dag(schedule_interval='0 3 * * *', catchup=True, max_active_runs=3, tags=["prisma_cloud"], default_args=default_args)
def historical_prisma_dag():

    def load_config_from_yaml(yaml_file):
        current_dir = os.path.dirname(__file__)
        yaml_file_path = os.path.join(current_dir, yaml_file)
        
        with open(yaml_file_path, 'r') as f:
            config = yaml.safe_load(f)
        return config

    config = load_config_from_yaml(yaml_file='src/prisma_cloud/config/config.yaml')

    @task
    def prepare_database():
        prisma_task = Prisma(config['api_config'], config['storage_config'])
        prisma_task.create_raw_tables(Variable.get("PRISMA_RESET_DATABASE", default_var=False))
    
    @task_group
    def retrieve_raw_data(current_execution_date):
        prisma_task = Prisma(config['api_config'], config['storage_config'])

        @task
        def task_run(prisma_task, current_execution_date, resource_key, resource_values):
            prisma_task.run_raw_data(current_execution_date, resource_key, resource_values)
            return f"Resource Key: {resource_key}\n  - Retrieved Count: {len(resource_values)}"

        resources = config['resources']
        return [task_run.override(task_id=resource_key)(prisma_task, current_execution_date, resource_key, resources[resource_key])
                for resource_key in resources.keys()]

    @task_group
    def save_raw_data(current_execution_date):
        prisma_task = Prisma(config['api_config'], config['storage_config'])

        @task
        def task_run(prisma_task, current_execution_date, resource_key, resource_values):
            prisma_task.save_database_raw_data(current_execution_date, resource_key, resource_values)

        resources = config['resources']
        return [task_run.override(task_id=resource_key)(prisma_task, current_execution_date, resource_key, resources[resource_key])
                for resource_key in resources.keys()]

    def setup_dbt_variables():
        connection = BaseHook.get_connection(config['api_config']['connection_database'])
        os.environ['DBT_HOST'] = connection.host
        os.environ['DBT_USER'] = connection.login
        os.environ['DBT_PASSWORD'] = connection.password
        os.environ['DBT_DBNAME'] = connection.schema
        os.environ['DBT_PORT'] = str(connection.port)
        os.environ['DBT_LOG_PATH'] =
