from datetime import datetime
import pulumi
from pulumi import Config, Output
import pulumi_azure_native as azure_native
from pulumi_azure_native import resources, network, web
from pulumi_random import random_string
import pulumi_azure_native.consumption as consumption

# Configuration variables
config = Config()
azure_location = config.get("azure-native:location") or "uksouth"

# Repositories for the Flask web apps
repo_urls = [
    config.get("my:repoUrl1") or "https://github.com/huhubi/clco_project/tree/main/Roulette/evenuneven",
    config.get("my:repoUrl2") or "https://github.com/huhubi/clco_project/tree/main/Roulette/numbers",
    config.get("my:repoUrl3") or "https://github.com/huhubi/clco_project/tree/main/Roulette/redblack"
]
branches = [
    config.get("my:branch1") or "main",
    config.get("my:branch2") or "main",
    config.get("my:branch3") or "main"
]

start = datetime(2024, 12, 1).strftime('%Y-%m-%dT%H:%M:%SZ')  # Start date: 1. December 2024
end = datetime(2025, 2, 28).strftime('%Y-%m-%dT%H:%M:%SZ')
mail_matthias = "wi22b112@technikum-wien.at"
mail_gregoire = "wi22b060@technikum-wien.at"
subscription_id = "5bb64e70-0225-40e2-b87c-ede62684f322"

# Resource Group
resource_group = resources.ResourceGroup('PaaSResourceGroup',
    resource_group_name='PaaSResourceGroup',
    location=azure_location
)

# Webapp Names
webapp_names = ["flaskroulettewebapp1", "flaskroulettewebapp2", "flaskroulettewebapp3"]

# Use random strings to give the Webapp unique DNS names
webapp_name_labels = [
    random_string.RandomString(
        f"{webapp_name}-",  # Prefix for the random string
        length=8,  # Length of the random string
        upper=False,  # Use lowercase letters
        special=False,  # Do not use special characters
    ).result.apply(lambda result: f"{webapp_name}-{result}")
    for webapp_name in webapp_names
]

# Virtual Network
virtual_network = network.VirtualNetwork('virtualNetwork',
    resource_group_name=resource_group.name,  # Name of the resource group
    location=azure_location,  # Location of the virtual network
    address_space=network.AddressSpaceArgs(
        address_prefixes=['10.0.0.0/16']  # Address space for the virtual network
    ),
    virtual_network_name='PaaSVNet'  # Name of the virtual network
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

# App Service Plan
app_service_plan = web.AppServicePlan('appServicePlan',
    resource_group_name=resource_group.name,
    name='myWebApp-plan',
    location=azure_location,
    sku=web.SkuDescriptionArgs(
        name='B1',
        tier='Basic',
        capacity=3  # Set the capacity to 3
    ),
    kind='linux',
    reserved=True
)

# Web Apps
web_apps = [
    web.WebApp(f'webApp{i}',
        resource_group_name=resource_group.name,
        name=webapp_name,
        location=azure_location,
        server_farm_id=app_service_plan.id,
        https_only=True,
        kind='app,linux',
        site_config=web.SiteConfigArgs(
            linux_fx_version='PYTHON|3.9',
            app_settings=[
                web.NameValuePairArgs(
                    name='WEBSITE_RUN_FROM_PACKAGE',
                    value='0'
                ),
            ],
            always_on=True,  # Keep the web app always on
            ftps_state='Disabled'  # Disable FTPS
        )
    )
    for i, webapp_name in enumerate(webapp_names)
]

# VNet Integration for all Web Apps
vnet_integrations = [
    web.WebAppSwiftVirtualNetworkConnection(f'vnetIntegration{i}',
        name=web_apps[i].name,
        resource_group_name=resource_group.name,
        subnet_resource_id=app_subnet.id
    )
    for i in range(len(webapp_names))
]

# Source Controls for all Web Apps
source_controls = [
    azure_native.web.WebAppSourceControl(f"sourceControl{i}",
        name=web_apps[i].name,
        resource_group_name=resource_group.name,
        repo_url=repo_urls[i],
        branch=branches[i],
        is_manual_integration=True,
        deployment_rollback_enabled=False
    )
    for i in range(len(webapp_names))
]

# Create a budget for the specified resource group
budget = resource_group.name.apply(lambda rg_name: consumption.Budget(
    resource_name="PaaS-Budget",  # Name of the budget resource
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

# Export the Web App hostnames as Markdown links
for i, web_app in enumerate(web_apps):
    pulumi.export(f"hostname_{i+1}", pulumi.Output.concat(f"[Web App {i+1}](http://", web_app.default_host_name, ")"))
