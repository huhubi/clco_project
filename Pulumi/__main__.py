#CLCO Project
from datetime import datetime

import pulumi
from pulumi import Config, Output
from pulumi_azure_native import resources, network, cognitiveservices, web
import pulumi_azure_native as azure_native
from pulumi_random import random_string
import pulumi_azure_native.consumption as consumption
import pulumi_azure as azure

# Configuration variables
config = Config()
azure_location = config.get("azure-native:location") or "uksouth"


defined_repo_url = "https://github.com/huhubi/roulettethirdsbet"
defined_repo_url_2 = "https://github.com/huhubi/rouletteredblack"
defined_repo_url_3 = "https://github.com/huhubi/roulettenumbers"
defined_branch = config.get("my:branch") or "main"
start = datetime(2025, 1, 1).strftime('%Y-%m-%dT%H:%M:%SZ')  # Startdatum: 1. November 2024
end = datetime(2025, 2, 28).strftime('%Y-%m-%dT%H:%M:%SZ')
mail_matthias ="wi22b112@technikum-wien.at"
mail_gregoire ="wi22b060@technikum-wien.at"
subscription_id = "5bb64e70-0225-40e2-b87c-ede62684f322"
#azure_native.config.subscription_id = subscription_id

# Resource Group
resource_group = resources.ResourceGroup('ProjectResourceGroup',
    resource_group_name='ProjectResourceGroup',
    location=azure_location
)

# Use random strings to give the Webapp unique DNS names
webapp_name_label1 = random_string.RandomString(
    "flaskwebapp-",  # Prefix for the random string
    length=8,  # Length of the random string
    upper=False,  # Use lowercase letters
    special=False,  # Do not use special characters
).result.apply(lambda result: f"{web_app_1}-{result}")  # Format the result with the web app name

# Virtual Network
virtual_network = network.VirtualNetwork('virtualNetwork',
    resource_group_name=resource_group.name,  # Name of the resource group
    location=azure_location,  # Location of the virtual network
    address_space=network.AddressSpaceArgs(
        address_prefixes=['10.0.0.0/16']  # Address space for the virtual network
    ),
    virtual_network_name='ProjectVNet'  # Name of the virtual network
)

# App Subnet
app_subnet = network.Subnet('applicationSubnet',
    resource_group_name=resource_group.name,  # Name of the resource group
    virtual_network_name=virtual_network.name,  # Name of the virtual network
    subnet_name='applicationSubnet',  # Name of the subnet
    address_prefix='10.0.0.0/24',  # Address prefix for the subnet
    delegations=[
        network.DelegationArgs(
            name='delegation',  # Name of the delegation
            service_name='Microsoft.Web/serverfarms',  # Service name for the delegation
        )
    ],
    private_endpoint_network_policies='Enabled'  # Enable network policies for private endpoints
)

# Endpoint Subnet
endpoint_subnet = network.Subnet('endpointSubnet',
    resource_group_name=resource_group.name,  # Name of the resource group
    virtual_network_name=virtual_network.name,  # Name of the virtual network
    subnet_name='endpointSubnet',  # Name of the subnet
    address_prefix='10.0.1.0/24',  # Address prefix for the subnet
    private_endpoint_network_policies='Disabled'  # Disable network policies for private endpoints
)

# App Service Plan
app_service_plan = web.AppServicePlan('appServicePlan',
    resource_group_name=resource_group.name,
    name='myWebApp-plan',
    location=azure_location,
    sku=web.SkuDescriptionArgs(
        name='B1',
        tier='Basic',
        capacity=3 # Set the capacity to 3
        #Verify command: az webapp list-instances --resource-group ProjectResourceGroup --name Projectflaskwebapp
    ),
    kind='linux',
    reserved=True
)

# Web App
web_app_1 = web.WebApp('webApp1',
    resource_group_name=resource_group.name,  # Name of the resource group
    name="rouletteflaskwebapp1",  # Name of the web app
    location=azure_location,  # Location of the web app
    server_farm_id=app_service_plan.id,  # ID of the associated App Service Plan
    https_only=True,  # Enforce HTTPS-only traffic
    kind='app,linux',  # Type of the web app
    site_config=web.SiteConfigArgs(
        linux_fx_version='PYTHON|3.12',  # Runtime stack for the web app
        always_on=True,  # Keep the web app always on
        ftps_state='Disabled',  # Disable FTPS
        app_command_line='pip install flask_socketio && FLASK_APP=app.py python -m flask run --host=0.0.0.0 --port=8000'
    )
)


# VNet Integration and Source Control for the first web app
vnet_integration_1 = azure_native.web.WebAppVnetConnection("vnetIntegration1",
    name=web_app_1.name,
    resource_group_name=resource_group.name,
    vnet_resource_id=app_subnet.id)

source_control_1 = azure_native.web.WebAppSourceControl("sourceControl1",
    name=web_app_1.name,
    resource_group_name=resource_group.name,
    repo_url=defined_repo_url,
    branch=defined_branch,
    is_manual_integration=True,
    deployment_rollback_enabled=False)

# Second Web App Configuration, starting after the first one completes
web_app_2 = web.WebApp('webApp2',
    resource_group_name=resource_group.name,  # Name of the resource group
    name="rouletteflaskwebapp2",  # Name of the web app
    location=azure_location,  # Location of the web app
    server_farm_id=app_service_plan.id,  # ID of the associated App Service Plan
    https_only=True,  # Enforce HTTPS-only traffic
    kind='app,linux',  # Type of the web app
    opts=pulumi.ResourceOptions(depends_on=[web_app_1]),
    site_config=web.SiteConfigArgs(
        linux_fx_version='PYTHON|3.12',  # Runtime stack for the web app
        always_on=True,  # Keep the web app always on
        ftps_state='Disabled',  # Disable FTPS
        app_command_line='pip install flask_socketio && FLASK_APP=app.py python -m flask run --host=0.0.0.0 --port=8000'
    )

)


# VNet Integration and Source Control for the second web app, after the app creation
vnet_integration_2 = web_app_2.name.apply(lambda name: azure_native.web.WebAppVnetConnection("vnetIntegration2",
    name=name,
    resource_group_name=resource_group.name,
    vnet_resource_id=app_subnet.id,
    opts=pulumi.ResourceOptions(depends_on=[web_app_1])))


source_control_2 = web_app_2.name.apply(lambda name: azure_native.web.WebAppSourceControl("sourceControl2",
    name=name,
    resource_group_name=resource_group.name,
    repo_url=defined_repo_url_2,
    branch=defined_branch,
    is_manual_integration=True,
    deployment_rollback_enabled=False,
    opts=pulumi.ResourceOptions(depends_on=[web_app_1])))

# Third Web App Configuration, starting after the second one completes
web_app_3 = web.WebApp('webApp3',
    resource_group_name=resource_group.name,  # Name of the resource group
    name="rouletteflaskwebapp3",  # Name of the web app
    location=azure_location,  # Location of the web app
    server_farm_id=app_service_plan.id,  # ID of the associated App Service Plan
    https_only=True,  # Enforce HTTPS-only traffic
    kind='app,linux',  # Type of the web app
    opts=pulumi.ResourceOptions(depends_on=[web_app_2]),
    site_config=web.SiteConfigArgs(
        linux_fx_version='PYTHON|3.12',  # Runtime stack for the web app
        always_on=True,  # Keep the web app always on
        ftps_state='Disabled',  # Disable FTPS
        app_command_line='pip install flask_socketio && FLASK_APP=app.py python -m flask run --host=0.0.0.0 --port=8000'
    )
)


# VNet Integration and Source Control for the third web app, after the app creation
vnet_integration_3 = web_app_3.name.apply(lambda name: azure_native.web.WebAppVnetConnection("vnetIntegration3",
    name=name,
    resource_group_name=resource_group.name,
    vnet_resource_id=app_subnet.id,
    opts=pulumi.ResourceOptions(depends_on=[web_app_2]))
                                        )

source_control_3 = web_app_3.name.apply(lambda name: azure_native.web.WebAppSourceControl("sourceControl3",
    name=name,
    resource_group_name=resource_group.name,
    repo_url=defined_repo_url_3,
    branch=defined_branch,
    is_manual_integration=True,
    deployment_rollback_enabled=False,
opts=pulumi.ResourceOptions(depends_on=[web_app_2])
                                        ))

# Create a budget for the specified resource group
budget = resource_group.name.apply(lambda rg_name: consumption.Budget(
    resource_name="Project-Budget",  # Name of the budget resource
    scope=f"/subscriptions/{subscription_id}/resourceGroups/{rg_name}",  # Scope limited to the resource group
    amount=50,  # Budget amount
    time_grain="Monthly",  # Budget reset interval
    time_period={
        "startDate": start,  # Start date of the budget
        "endDate": end,  # End date of the budget
    },
    notifications={
        "Actual2Percent": {  # Notification when 2% of the budget is reached
            "enabled": True,
            "operator": "GreaterThan",  # Condition: Budget exceeded
            "threshold": 2,  # 2% of the budget
            "contact_emails": [mail_matthias, mail_gregoire],  # Email addresses for notifications
            "contact_roles": [],  # No specific roles
            "notification_language": "en-US",  # Notification language
        },
        "Actual50Percent": {  # Notification when 50% of the budget is reached
            "enabled": True,
            "operator": "GreaterThan",
            "threshold": 50,  # 50% of the budget
            "contact_emails": [mail_matthias, mail_gregoire],
            "contact_roles": [],
            "notification_language": "en-US",
        },
    },
    category="Cost",  # Budget category for cost monitoring
))


# Export the Web App hostname as a Markdown link
pulumi.export("hostname", pulumi.Output.concat("[Web App](http://", web_app_1.default_host_name, ")"))
pulumi.export("hostname", pulumi.Output.concat("[Web App](http://", web_app_2.default_host_name, ")"))
pulumi.export("hostname", pulumi.Output.concat("[Web App](http://", web_app_3.default_host_name, ")"))