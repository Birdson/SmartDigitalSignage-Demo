# SmartDigitalSignage

## Requirements
1. Install Pip with apt-get
sudo apt-get update
sudo apt-get -y install python-pip

2. The demo server requires Python with some dependencies.
To make sure you have the dependencies, please run `sudo pip install -r requirements.txt`, and also make sure that you've compiled the Python Caffe interface and that it is on your `PYTHONPATH` (see [installation instructions](/installation.html)).

## Run

Running `python app.py` will bring up the demo server, accessible at `http://<your-ip>:9000`.
You can enable debug mode of the web server, or switch to a different port:
