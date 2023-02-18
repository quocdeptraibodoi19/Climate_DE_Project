# Data Engineer Project - Climate Project

## **Problem:**

Currently climate problem is emerging as a super serious issue affecting every countries from developed countries to developing countries.

In this project, I will investigate into this problem in terms of the Global Temperature. I want to know that:

- What are the top/major cities countries having the highest average temperature over the period (top 5)?
- What are periods in the history being a peak in terms of temperature?
- what is the tendency of the temperature globally?

The above questions are simulated questions of a particular analysis process. 

## The architecture for the application:

![Untitled](Visualization/Untitled.png)

There are 2 layers in the Staging Area implemented with S3: 

- Data Zone (Landing Zone): Used to store raw data and preprocess data (add the date column). This layer will incrementally load data from sources according to a specific schedule. This layer acts as a centralized data repository.
- Processing Stage: Used to store the processed data prior to moving it into a data warehouse.

### Why?

The reason why having the staging area in the architecture?

Having staging area in the data pipeline brings back many benefits:

- Playing as a centralized data repository storing raw data from many sources. which makes it easier to manage and monitor the data for the system. Additionally, since sources stem from many other different systems (API, Web Scrapping, DBMS, OLTP,…), having something as a common interface will be easier to implement downstream tasks.
- Helping the make the system more consistent and reliable since we do not rely on the external sources, which limits affecting downstream tasks.
- Having staging area in the system can help us easily backfill the data (in the event that we wrongly process data and we want to fix that). The staging area can help us with that
- RDS or external sources just record the current state of the data. Having the staging area in the system can act like the log system helping us to trace back the logic error in the processing tasks for example. Without staging area, we can easily lost the data since we don’t have any historical snapshot of data.

⇒ Those are the reasons why we use staging area in the data pipeline.

The reason why we decouple the staging area into 2 parts: data zone and processing zone?

That we decouple the staging area into 2 parts can help to better the managing and monitoring process of data, bring back the high possibility to troubleshoot the errors, make it much easier to track the data lineage to see whether or not data is appropriately processed and if not, we can easily trace back the root of the cause and fix that. That we decouple the staging area is a fine-grained approach to have a higher control over our data and make it much easier to troubleshoot the errors when they arise, which ends up a better quality of the data. 

The trade-off of this approach is that:

- It requires much more infrastructure for the implementation and deployment.
- It requires much more compute power
- It increases the complexity of the system
- That data have to move to different places can downgrade the performance of the system, and increase the risk of errors, security issues,…

### Setting up and Configuration:
What I've done so far is to create 3 AWS EC2 machines. The first one is used to host the apache airflow application which is used to orchestrate the whole data pipeline. The apache airflow uses sequential executors to handle tasks. The others play a roles respectively as a master node and a worker node in the Spark Cluster. The Spark Cluster is deployed in a standalone mode.
About the data sources, first of all, they are just csv files. Then from the local machine, I detach them and then move them into 3 AWS RDS MySQL Databases.
About the AWS RedShift, I create a cluster of node node (free tier). This node store our processed data. 

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

## Future Work:
What I have done so far is too manual and unprofessional. Thus, this project is not so similar to what is in the reality. I want to use Terraform to automate the process of setting up the infrastructure and use Docker for the ease of system deployment. I also want to apply CI/CD in my project in the future.
