#  Copyright 2024 vCommunity Content MP
#  Author: Onur Yuzseven

import logging
import yaml
import os

NULL_STATUS = "null"
logger = logging.getLogger(__name__)
current_directory = os.path.dirname(os.path.abspath(__file__))
clusterConfigs = os.path.join(current_directory, "../../constants/cluster/clusterConfigs.yaml")


def collect_drs_properties(cluster_obj, drs_config):
    with open(clusterConfigs, "r") as file:
        data = yaml.safe_load(file)

    for group_name, group_content in data.items():
        if group_name and group_name == "DRS" and "properties" in group_content:
            for item in group_content["properties"]:
                propertyName = item["name"]
                if drs_config.configuration.drsConfig.enabled == False:
                    cluster_obj.with_property(propertyName, NULL_STATUS)
                else:
                    configPath = item["configPath"]
                    keys = configPath.split('.')
                    propertyValue = drs_config
                    for key in keys:
                        propertyValue = getattr(propertyValue, key)
                    cluster_obj.with_property(propertyName, str(propertyValue))