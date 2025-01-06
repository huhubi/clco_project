

# CLCO roulette project at FHTW - Deployment notes / procedure

**Authors:** Gregoire Bartek / Matthias Huber  
**Date:** January 6, 2025  
**Contact:** wi22b112@technikum-wien.at / wi22b060@technikum-wien.at

## 1. Deploy with Pulumi
Run the following command in the Pulumi folder to deploy the infrastructure:

```bash
pulumi up -y
```
![image](https://github.com/user-attachments/assets/9841360e-1e6b-49c6-9de3-d986fd7a2b58)


## 2. Manual Deployment of Roulette Repository
Since deploying web apps via Pulumi lead to errors, the deployment of the Roulette Repository will be done manually for each web app. After deployment, the application can be accessed at:

- [Roulette table selector](http://roulettetableselector.uksouth.cloudapp.azure.com/)

## 3.Deployment procedure of one webapp (repeat for each one):

- [rouletteflaskwebapp1.azurewebsites.net](https://rouletteflaskwebapp1.azurewebsites.net) this one hosts the color roulette game:
- Navigate to Deployment Center in the WebApp View:
![image](https://github.com/user-attachments/assets/2c38f818-d330-4340-b492-07c40ccb1e06)

- Select external git as deployment method and add repository link:
  ![image](https://github.com/user-attachments/assets/b6d55741-c266-48bd-8571-7ac71b1c61c2)

- Click on save once filled out and the deployment procedure starts automatically
  ![image](https://github.com/user-attachments/assets/70e212ab-f2f9-490c-a95f-2a38950a2483)

- After some minutes, the webapp is deployed (for progress one can check the deployment logs):
![image](https://github.com/user-attachments/assets/7020b578-2fcc-4c9a-b931-541d03c1ed38)

## 4. Check functionality:

- Access [Roulette table selector](http://roulettetableselector.uksouth.cloudapp.azure.com/) in browser
- Click on [Rot/Schwarz](https://rouletteflaskwebapp1.azurewebsites.net/)
  ![image](https://github.com/user-attachments/assets/1a0bd45d-3438-4ce8-92e4-5be3a60928a0)

Repeat for second and third repository with the following Repository Links
- [Numbers](https://github.com/huhubi/roulettenumbers)
- [Thirds](https://github.com/huhubi/roulettethirdsbet)



