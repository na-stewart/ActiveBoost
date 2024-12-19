<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center">ActiveBoost</h3>

  <p align="center">
    Get in shape, together.
  </p>
  <p align="center">
    Nicholas Stewart, Jenayah Shearn, Emma Degenhardt, Vidhee Patel, Ziru Xia
  </p>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Configuration](#configuration)

<!-- ABOUT THE PROJECT -->
## About The Project

Submission for CSCI_380, Introduction to Software Engineering.

**API Documentation**: https://documenter.getpostman.com/view/26504282/2sAY55ZxRC

The ActiveBoost API is a web service that enables secure communication between users and their data. 
In RESTful design, resources (such as users, groups, or challenges) are represented by URLs, and each request performs an action on the resource. 
Parameters are passed to the requests via url arguments or form data.

There are several request types including GET, POST, PUT, and DELETE. 
API responses are formatted in JSON, making the data easy to parse and use across various applications. 
This design provides a scalable, modular, and secure foundation for interacting with user-related resources in the ActiveBoost platform.

### Demo

[Watch the video.](https://www.youtube.com/watch?v=iu8YumIYoS8)

[![Watch the video](https://img.youtube.com/vi/iu8YumIYoS8/0.jpg)](https://www.youtube.com/watch?v=iu8YumIYoS8)

### Screenshots

<div>
  <img src="https://github.com/na-stewart/Activeboost-Mobile/blob/master/preview2.PNG" alt="Image 2" width="250" height="550">
  <img src="https://github.com/na-stewart/Activeboost-Mobile/blob/master/preview.PNG" alt="Image 1" width="250" height="550">
  <img src="https://github.com/na-stewart/Activeboost-Mobile/blob/master/preview3.PNG" alt="Image 3" width="250" height="550">
</div>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

Download Python.

* [https://developer.android.com/studio](https://www.python.org/)

Download your IDE of choice, I prefer PyCharm. An alternative to JetBrains is [VSCode](https://code.visualstudio.com/).

* [https://www.jetbrains.com/pycharm/download](https://www.jetbrains.com/pycharm/download)

Ensure PyPi is installed, keep in mind that this is usually pre-packaged with Python or your IDE of choice

* https://pypi.org

### Installation

* Clone the repo
  
```shell
git clone https://github.com/na-stewart/Activeboost-Mobile
```

* Open the project in your IDE of choice, then install dependencies with the command below.

```shell
pip3 install -r requirements.txt
```

### Configuration

Database schemas are automatically created when the server is initiated. You can customize the API configuration in order to utilize your own Fitbit API keys and database server within `util.py`

| Key               | Value                            | Description                                                                                                        |
|-------------------|----------------------------------|--------------------------------------------------------------------------------------------------------------------|
| **SECRET**        | This is a big secret. Shhhhh     | The secret used for generating and signing JWTs. This should be a string unique to your application. Keep it safe. |
| **DATABASE_URL**  | sqlite://db.sqlite3              | URL of your instance's database.                                                                                   |
| **FITBIT_SECRET** | 58e2c6749ba6cb49d4900debf47798b7 | Fitbit API token.                                                                                                  |
| **FITBIT_CLIENT** | 23PR33                           | Fitbit client ID.           



