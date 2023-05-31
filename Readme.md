# Grow Simplee IIT Ropar

This is the repository contains our code for the [Inter IIT Tech Fest](https://interiit-tech.org/). We are working on HIGH PREP problem - [Grow Simplee](https://interiit-tech.org/images/ps/High_GS.pdf). This website is built using [django](https://www.djangoproject.com/).


## Our Team
1. Parth Jain
2. Jaglike Makkar
3. Anant Prakash
4. Yashasav Prajapati
5. Subham Sahoo
6. Vasu Bansal
7. Anubhav Kataria
8. Sagalpreet Singh
9. Samarth Singhal
10. Sneha Sahu
11. murru sai yaswanth 
12. Kavyansh Dhakad
13. Varun Kashyap
14. Jigisha Arora
15. Sanat Gupta
16. Dhruv Gupta

## Installation

1. Clone the repository
2. Install the requirements using `pip install -r requirements.txt`
3. Run the server using `python manage.py runserver`



## Objectives
1. Capture the dead weight of the item along with the volumetric weight of the bounding box for that object.
2. To develop a comprehensive and efficient solution that addresses all these points, resulting in an optimal outcome for the multi/dynamic pickup routing problem.




## Advantages of using:
- The model uses the shadow, which will be the same no matter where the object is placed on the glass plate.
- Very large objects will also cast their shadows which is not the case if a camera was placed on the top to capture the image as the angle coverage becomes a barrier.
- This method is independent of the orientation of the boxes
- There is minimum computation involved which makes it fit for the real-time application on the conveyor belt.


### Scopes of error:
If there is some other light source interfering with the setup, then there are high chance multiple or skewed shadows are obtained, and in that case, the output produced will be wrong


## Improvements at the industry level:
Instead of using a camera at the bottom if a photosensitive screen can be used for eg. CCD screen or CMOS based screens then the accuracy levels will be quite high. 


## Working:
The depth sensor calculates the height of the object and the camera captures the top view of the image. The image is preprocessed and the green pixels are removed from the image leaving out just the object pixels. The image is then converted to a binary image.From here the complete procedure is similar to the original idea. A minimum area bounding box is created around the object pixels and the length and breadth obtained in pixels are converted into the cm values which are multiplied with the height to obtain the volume.


## Tools used:
To generate delivery routes, we first read longitude and latitude locations from an input text file. This is achieved by utilizing the Google Maps API in Python to obtain the geo-locations. A cost matrix is then created for each pair of destinations, with the cost being the distance between the two points by road. The distance and duration between pairs of points are calculated using a custom function, with an assumed driver speed of 50 km/hr. Next, we process other inputs such as expected delivery time, names, and AWB. For rider capacity and bag creation, we have implemented a custom bag creation strategy. All inputs are then passed to the OR Algorithm, where we select the appropriate route construction strategy and metaheuristic based on user input. The generated routes are sent to the frontend, where they are displayed using the Leaflet Routing Machine. The frontend is built using React.js, while the backend uses Django.


## Brief description of the algorithms and methods involved:
Our algorithm for solving the problem aims to find approximate solutions, as the problem is known to be NP-hard. We intend to test various methods and approaches to this problem by dividing it into two parts:


## Final Implementation:
Bag Allocation Strategy: Initially, we determine the optimal routes for each driver such that each driver carries a maximum of 30 SKUs (considering the algorithm for finding the optimal routes as a black box for now, we will explain it later). Note that we ignore the actual volume of the items in this process. After finding the routes, we allocate bags to each driver in a way that the bag capacity is equal to or slightly greater than the volume of items to be delivered. Additionally, we impose an upper limit on the bag capacity that a driver can carry. In this problem, the upper limit is set to (2 * total_bag_capacity)/(number_of_drivers).
Reason for not allocating equal bag capacity to each driver: While equal bag allocation per driver may seem equitable, it is not necessarily optimal as the volume of delivered items can vary greatly (ranging from 3 * 3 * 3 cm^3 to 40 * 40 * 20 cm^3). In scenarios where there are multiple drop points in close proximity, it can be more efficient to increase the bag capacity of a rider to cover all drop points in a cluster.
