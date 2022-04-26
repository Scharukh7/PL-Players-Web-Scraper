# PL-Players-Web-Scraper
Note: uploading to S3 has been commented out to avoid the usage of the S3 everytime the code is   run. Also use your credentials for aws inside the terminal and for your Postgresql credentials use the credentials.yml file inside config file and update.


## Milestone 1: Decide the website

- chose alot of websites containing table data and experimented through the progress as this was not the main concern.

## Milestone 2: Prototype finding the individual page for each entry

- created a scraper class using selenium webdriver
- bypassing the cookies on the website method was created
- the first page contained basic name,  rank, nationality etc and all that data was scraped from the first page inside the table
- to get the hyperlinks for each player on the web table, a container was created and used xpath to get each players link by iterating through the table and stored in a list of dictionary
- the dictionary data was then converted to pandas dataframe in order to convert to .json format

## Milestone 3: Retrieve data from details page
- unique id was generated from the hyperlinks using uuid for each player
- another method was created to gather extra information from each players profile as well as their images
- again were converted to dataframe in order to save as .json format
- all the data was stored as raw data inside raw_data folder

## Milestone 4: Documentation and testing
- the code created so far was optimised and docstrings were added for each method
- testing was done for the methods created using unittest 

## Milestone 5: Scalaby store the data
- raw data collected was then uploaded to AWS S3 along with the images
- Tabular data was upload to RDS

## Milestone 6: Getting more data
- additional testing for additional methods were done
- unique id for image links was also created to avoid duplication of data

## Milestone 7: Make the scraping scalable
- the code was optimised once again
- all the tests passed
- a way to check the differences method was created by comparing the names from each scraping method to avoid duplication as well and for the tabular data to check if the data already exists or not
- Docker image was created by building a new image
- scraper ran in headless mode using options
- docker image was then pushed to the docker hub account
- EC2 instance was enabled using AWS and download docker inside the EC2 terminal and then the docker image ran successfully

## Milestone 8: Monitoring and alerting
- Prometheus.yml file was created in order to create a docker container running Prometheus and was ran in detach mode
- port settings were adjusted inside the EC2 security settings in order to run locally
- Metrics were monitored by looking at the graphs for EC2 and Docker container
- Grafana account was created and a new dashboard created for Prometheus in order to monitor 
the metrics there. CPU Usage, memory and container metrics were observed 


## Milestone 9: Set up a CI/CD pipeline for your Docker Image
- Github secrets were added by using Docker hub's account username and secret key
- a workflow was created called main.yml in order to build the docker image and push to docker

## Docker Image 
- access the docker image from here: https://hub.docker.com/repository/docker/scharukh7/player_scraper

## Conclusion:

This project helped me understand how to make use selenium in order to scrape any website, helped me understand on how to bypass login page, cookies or any captcha or ads present on the website. Helped me gather any kind of data. 
Able to understand how to use AWS services such as IAM, RDS, EC2, S3 even though not a huge fan of RDS as there were some complication updating the table everytime in MYSQL.
Able to understand the concept behind Docker and creating docker images for a user-free work for everyone and using EC2 to avoid any memory issue.
Overall, this helped me understand alot better how data is gathered and worked on.
