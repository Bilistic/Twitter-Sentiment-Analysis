# System Architecture:

![Alt text](resources/arch1.PNG?raw=true "Title")

The above diagram gives a brief description of the services expected to complete the application.
When creating this I had to design it to handle increases in load on the communication services. As
such the system is design so that deployment of X number of servers will dissipate (Balance) the
incoming data within the RabbitMQ queue. Equally if one wishes to have multiple search terms it is
as simple as starting another Twitter streamer with an alternative search term.

# Server:

![Alt text](resources/arch2.PNG?raw=true "Title")

The Server consists of a server a, messenger, and a database. The server handles call back functions required for RPC objects (in our case primarily coming from the Flask Web App). The Messenger handles communication via RabbitMQ, the database is interfaced by a data access object that is held on the server this object gives us read and write permission to the database. Messenger receives client messages containing an action and body. The server will decipher the action and do with the body as it sees fit. When Running a server, you can supply it with arguments rabbit_host and mongo_host. Since these services are design for running inside a docker container I opted to keep the default ports, however if required these can be overwritten.

# Twitter Streamer:

![Alt text](resources/arch3.PNG?raw=true "Title")

The twitter service consists of a Data Analyser, Listener, Messenger and a Twitter Client. Although I considered using RPC to have the Data Analyser run on the server side (Sentiment score) I concluded this process was so small it had little to no impact running within the twitter Listener. Like previously the Twitter Steamer is equipped with a Messenger to connect to RabbitMQ, in this case we use the messenger for simply sending byte messages to the server. When running the twitter stream, it is supplied with an argument to override the default RabbitMQ host “localhost”. Like the server I have kept the default port however it is possible to be overwritten.

# Web-App:

![Alt text](resources/arch4.PNG?raw=true "Title")

The web app consists of a flask server and timer client. The flask server creates an interface to view statistics on the data for a set amount of time (Hard coded variable “time” change if required) The generated web page shows the top ten most positive tweets of the last X minutes and equally the top ten negative, it also displays the average sentiment score for the last X amount of minutes. These variables are re-calculated on page load. As such if a page is already open please reload to update the data ({machine-ip}:5000/index). The timer client extends the Messenger object. This inherits the role of the messenger however acts as a RPC client as such messages sent via this client are interpreted by the server causing the server to respond with a returning object. In this case a list of tweets.

# Running:

The overall system can be run by moving your docker-QuickStart terminal into the relevant directory and issuing the command “docker-compose up”. This will build and initiate all the above services. The python flask web app will be exposed to port 5000 as such you can connect via the following url: http://192.168.99.100:5000/index.

# Information of Architecture:

The scalability of the system should allow for use of the paid twitter services which do not throttle the number of tweets you have access to. As mentioned extendibility is available by simply deploying another server instance or if you want more data then another streaming instance. Re usability of each service can easily be accomplished by simply deploying the service in an environment of your choice knowing you can change the ports and hosts required. Each service is design to be used with any other project none are reliant on other services provided. Tweepy a module used in the twitter streaming service has a open error in its code. Currently in the way a broken connection is being handled (on Tweepies side) will cause an error making it unable to reconnect this is a Tweepy error unfortunately and has an open ticket, https://github.com/tweepy/tweepy/issues/650. However, it must be said due to twitter handling being its own service it is possible to change the module used to an alternative twitter module in the future with very little work needed as such is a great example to how having a loosely coupled system does not commit us to one certain technology.
