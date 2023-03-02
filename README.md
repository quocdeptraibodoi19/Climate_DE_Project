# Data Engineer Project - Climate Project

## **Problem:**

Currently, the climate problem is emerging as a super serious issue affecting every country from developed countries to developing countries.

In this project, I will investigate this problem in terms of global temperature. I want to know:

Which are the top/major cities or countries with the highest average temperature over a period (top 5)?
Which periods in history had a peak in terms of temperature?
What is the global temperature trend?
The above questions are simulated questions of a specific analysis process.

## The architecture for the application:

![Untitled](Visualization/Untitled.png)

The Staging Area has two layers implemented with S3:

Data Zone (Landing Zone): This layer is used to store raw data and preprocess data (such as adding a date column). The Data Zone incrementally loads data from sources according to a specific schedule. This layer acts as a centralized data repository.

Processing Stage: This layer is used to store processed data before moving it into a data warehouse.

What I've done so far is to create 3 AWS EC2 machines. The first one is used to house a docker containers setting up apache airflow application consisting of a postgres SQL to store metadata, an airflow scheduler and an airflow webserver. The apache airflow uses local executors to handle tasks. The others play a roles respectively as a master node and a worker node in the Spark Cluster. The Spark Cluster is deployed in a standalone mode.
About the data sources, first of all, they are just csv files. Then from the local machine, I detach them and then move them into 3 AWS RDS MySQL Databases.
About the AWS RedShift, I create a cluster of node node (free tier). This node store our processed data. 

## Project Initialization and Setup Guide

This guide outlines the necessary steps to initialize and set up the project on AWS.

### Prerequisites

- Github account
- Git installed
- AWS account
- AWS CLI installed and configured
- A development environment (such as Ubuntu or another Linux-based OS) installed on your system. If you are using Windows, please ensure that you have access to a Linux-based terminal such as Git Bash or Windows Subsystem for Linux (WSL).

### Installation

1. Clone the project from Github to your local machine.
2. Use make init command to download and install the required packages to initialize the project.
3. Use make up command to set up the infrastructure on AWS. Note that this process may take some time, so please be patient.
4. Use make init-resource command to populate the RDS databases with raw data to simulate the data sources. Please note that this step requires all RDS databases to be fully created before execution. If you encounter any errors during this step, wait for a few minutes and try again.

### Data Pipeline Operations

Once you have completed the above steps, you can now operate the data pipeline.

1. Access the Airflow website using the public IP or public DNS of the "airflow machine" with port 8081. Alternatively, you can map it to localhost using the command make cloud-airflow. The port will now be 8082, and you can access it via localhost:8082.
2. To inspect the Spark cluster, use the URL generated from the combination of the public DNS or public IP of the "master airflow machine" with port 8080. You can also use the command make cloud-spark to make it easier. The port will now be 8083.
3. Run your data pipeline.

### Destruction

If you want to destroy the infrastructure, use the make down command.

## Data Sources’ schemas:

There are 3 MySQL databases stored in AWS RDD. Those schemas are shown below:

![Untitled](Visualization/Untitled%201.png)

## The Star Schema in the Data Warehouse:

I use AWS Redshift as a data warehouse storing processed data for analytics.

The star schema for the data is shown below:

![Untitled](Visualization/Untitled%202.png)

## Solutions to the problem (Data visualization):

### 1. What are the top/major cities countries having the highest average temperature over the period?

To answer this questions, I will present the line chart of top 5 cities having the highest average temperature over the period

![chart.png](Visualization/chart.png)

They are respectively Bankok,  Jiddah, Umm Durman, Ho Chi Minh City, and Madras. 

We can clearly see in the chart that, the temperature has tended to increases over the period. 

Similarly, with countries:

![chart (1).png](Visualization/chart_(1).png)

5 countries having the highest average temperature over the period are Aruba, Burkina, Mali, Djibouti, and Senegal. 
Again their temperature have the tendency to increase.

### 2. What are periods in the history being a peak in terms of temperature?

I will limit the scope of the problem down to the temperature on the land since Homo Sapiens is a kind of terrestrial animal right?

![Untitled](Visualization/Untitled%203.png)

As shown in the table, 2013 is the period with the highest average temperature value over the period.

In  a more detail view, this is the chart presenting the detail temperature value of each month in the year 2013:

![chart (4).png](Visualization/chart_(4).png)

### 3. What is the tendency of the temperature globally?

![chart (5).png](Visualization/chart_(5).png)

This is the area chart caring about the “Land and Ocean Average Temperature” and “Land Average Temperature” on the global basis. Both of them show the tendency to increase.
