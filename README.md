# Fire up the vagrant 

    vagrant up
    vagrant ssh
    sudo apt-get update
    sudo apt-get install libffi-dev libssl-dev python-dev python-virtualenv python-pip redis-server fish
    virtualenv crossbarstuff
    . crossbarstuff/bin/activate.fish 
    pip install -r requirements.txt

# Start crossbar

    cd /vagrant/helloworld/
    crossbar start

Now open a browser outside the vagrant box to http://localhost:8080 . It will behave as your first device. Open more tabs for more devices.

The simulated device has an autogenerated ID, displayed at the top, plus 99 pins. After generating an ID, the device will connect to the crossbar server and receive pin updates (marked in tasteful yellow). You can also click a pin to send a pin update (marked in even more tasteful green).

# Start a worker (or many)

Crossbar will publish every pin change into redis, so we have 0...n workers to fetch and process the updates.

    cd /vagrant/helloworld/hello/
    python worker.py

The worker will idle until at least one pin update has been pushed into the queue, then process that pin (by printing a very helpful message to the console).

Try starting multiple workers.