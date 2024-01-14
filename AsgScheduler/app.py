import os
import boto3

client = boto3.client('autoscaling')
MIN_SIZE = 0
MAX_SIZE = 0
DESIRED_CAPACITY = 0


class AutoScalingGroupConfig:
    def __init__(self):
        self.auto_scaling_groups = get_env_variable('NAMES').split()
        self.min_size = int(get_env_variable('MIN_SIZE', default=str(MIN_SIZE)))
        self.max_size = int(get_env_variable('MAX_SIZE', default=str(MAX_SIZE)))
        self.desired_capacity = int(get_env_variable('DESIRED_CAPACITY', default=str(DESIRED_CAPACITY)))


def get_env_variable(var_name, default=None):
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        raise Exception(f'Set the {var_name} environment variable')


def handle_errors(action):
    try:
        return action()
    except Exception as e:
        print(f'Error: {e}')
        raise


def lambda_handler(event, context):
    handle_errors(lambda: update_asg(event))


def update_asg(event):
    config = AutoScalingGroupConfig()
    for group in config.auto_scaling_groups:
        if servers_need_to_be_started(group):
            min_size = config.min_size
            max_size = config.max_size
            desired_capacity = config.desired_capacity
        else:
            min_size = MIN_SIZE
            max_size = MAX_SIZE
            desired_capacity = DESIRED_CAPACITY
        client.update_auto_scaling_group(
            AutoScalingGroupName=group,
            MinSize=min_size,
            MaxSize=max_size,
            DesiredCapacity=desired_capacity,
        )


def servers_need_to_be_started(group_name):
    min_group_size = get_current_min_group_size(group_name)
    return min_group_size == 0


def get_current_min_group_size(group_name):
    response = client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[group_name],
    )
    return response["AutoScalingGroups"][0]["MinSize"]
