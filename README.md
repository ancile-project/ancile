# Ancile - Use-Based Privacy for applications


Make documentation: `cd docs && make html`

Ancile is a framework that enables control over application's
data usage with privacy policies. We currently support Python and 
work with any OAuth service. Essentially, our system is a middleware 
between the data source (e.g. mail server, location data server, etc)
and some application created by the third-party.  

![system logo](docs/source/system.png)

**Use-based privacy** ([Birrell et al.](https://www.cs.cornell.edu/fbs/publications/UBP.avanance.pdf))
focuses on preventing harmful uses (**[NYTimes](https://www.nytimes.com/interactive/2018/12/10/business/location-data-privacy-apps.html)**)
rather than restricting 
access to data. The application gets to use all necessary data for non-harmful
purposes. Each datapoint in Ancile has a policy that specifies what uses 
are permitted. Furthermore, this framework utilizes **reactive** approach meaning 
that after performing transformations on data policy will change. 

## Use Case
  
Let's consider an application that tracks a professor and notifies
students of professor's location during dedicated office hours.
The location service collects fine-grained information on 
user's whereabouts. Unrestricted release of raw data can lead
to malicious uses where the professors location is accessed after hours 
or outside of the campus. Ancile can address this problem by defining a policy
on professor's location data that allows data only at specific hours.



## Installation

Here are the installation [Instructions](docs/source/installation.md).

We have a development environment running at https://dev.ancile.smalldata.io 
so please free to explore it. 


