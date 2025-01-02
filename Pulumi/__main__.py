import pulumi
from pulumi import Config, Output, ResourceOptions
import pulumi_azure_native as azure_native
from pulumi_azure_native import resources, network, web
from pulumi_random import RandomString
import pulumi_azure_native.consumption as consumption
from datetime import datetime

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

start = datetime(2025, 1, 1).strftime('%Y-%m-%dT%H:%M:%SZ')
end = datetime(2026, 2, 28).strftime('%Y-%m-%dT%H:%M:%SZ')
mail_matthias = "wi22b112@technikum-wien.at"
mail_gregoire = "wi22b060@technikum-wien.at"
subscription_id = "5bb64e70-0225-40e2-b87c-ede62684f322"

# Resource Group
resource_group = resources.ResourceGroup('ProjectResourceGroup',
    resource_group_name='ProjectResourceGroup',
    location=azure_location
)

# Webapp Names
webapp_names = ["flaskroulettewebapp1", "flaskroulettewebapp2", "flaskroulettewebapp3"]

# Use random strings to give the web apps unique DNS names
webapp_name_labels = [
    RandomString(
        f"{webapp_name}-",
        length=8,
        upper=False,
        special=False,
    ).result.apply(lambda result: f"{webapp_name}-{result}")
    for webapp_name in webapp_names
]

# Virtual Network
virtual_network = network.VirtualNetwork('virtualNetwork',
    resource_group_name=resource_group.name,
    location=azure_location,
    address_space=network.AddressSpaceArgs(
        address_prefixes=['10.0.0.0/16']
    ),
    virtual_network_name='ProjectVNet'
)

# App Subnet
app_subnet = network.Subnet('applicationSubnet',
    resource_group_name=resource_group.name,
    virtual_network_name=virtual_network.name,
    subnet_name='applicationSubnet',
    address_prefix='10.0.0.0/24',
    delegations=[
        network.DelegationArgs(
            name='delegation',
            service_name='Microsoft.Web/serverfarms',
        )
    ],
    private_endpoint_network_policies='Enabled'
)

# App Service Plan
app_service_plan = web.AppServicePlan('appServicePlan',
    resource_group_name=resource_group.name,
    name='myWebApp-plan',
    location=azure_location,
    sku=web.SkuDescriptionArgs(
        name='B1',
        tier='Basic',
        capacity=3
    ),
    kind='linux',
    reserved=True
)

######################################
# Create Web Apps in sequence
######################################

# First Web App
web_app1 = web.WebApp(
    'webApp1',
    resource_group_name=resource_group.name,
    name=webapp_names[0],
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
        always_on=True,
        ftps_state='Disabled'
    )
)

# Second Web App - depends on the first Web App
web_app2 = web.WebApp(
    'webApp2',
    resource_group_name=resource_group.name,
    name=webapp_names[1],
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
        always_on=True,
        ftps_state='Disabled'
    ),
    # This is the critical part to ensure the second WebApp waits for the first
    opts=ResourceOptions(depends_on=[web_app1])
)

# Third Web App (this one deploys in parallel by default,
# but you could also specify depends_on=[web_app2] if you want it strictly sequential)
web_app3 = web.WebApp(
    'webApp3',
    resource_group_name=resource_group.name,
    name=webapp_names[2],
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
        always_on=True,
        ftps_state='Disabled'
    ),
    opts=ResourceOptions(depends_on=[web_app2])
)

# Collect them in a list for convenience
web_apps = [web_app1, web_app2, web_app3]

######################################
# VNet Integration for all Web Apps
######################################
vnet_integrations = [
    web.WebAppSwiftVirtualNetworkConnection(
        f'vnetIntegration{i}',
        name=web_apps[i].name,
        resource_group_name=resource_group.name,
        subnet_resource_id=app_subnet.id
    )
    for i in range(len(web_apps))
]

######################################
# Source Controls for all Web Apps
######################################
source_controls = [
    web.WebAppSourceControl(
        f"sourceControl{i}",
        name=web_apps[i].name,
        resource_group_name=resource_group.name,
        repo_url=repo_urls[i],
        branch=branches[i],
        is_manual_integration=True,
        deployment_rollback_enabled=False
    )
    for i in range(len(web_apps))
]

######################################
# Create a Budget for the Resource Group
######################################
budget = resource_group.name.apply(lambda rg_name: consumption.Budget(
    resource_name="Project-Budget",
    scope=f"/subscriptions/{subscription_id}/resourceGroups/{rg_name}",
    amount=50,
    time_grain="Monthly",
    time_period=consumption.BudgetTimePeriodArgs(
        start_date=start,
        end_date=end
    ),
    notifications={
        "Actual2Percent": consumption.NotificationArgs(
            enabled=True,
            operator="GreaterThan",
            threshold=2,
            contact_emails=[mail_matthias, mail_gregoire],
            contact_roles=[]
        ),
        "Actual50Percent": consumption.NotificationArgs(
            enabled=True,
            operator="GreaterThan",
            threshold=50,
            contact_emails=[mail_matthias, mail_gregoire],
            contact_roles=[]
        ),
    },
    category="Cost"
))

######################################
# Export the Web App hostnames
######################################
for i, web_app in enumerate(web_apps):
    pulumi.export(f"hostname_{i+1}", 
        Output.concat(f"[Web App {i+1}](http://", web_app.default_host_name, ")")
    )
