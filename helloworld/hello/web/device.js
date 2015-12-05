for (var i = 0; i < 100; i++) {
    document.getElementById('pins')
        .insertAdjacentHTML('beforeend', '<div id="pincontainer-' + i + '" class="bg-info" onclick="updatePin(' + i + ', 42, \'bg-success\');" style="float: left; display: block; width: 140px; margin: 5px; padding: 10px;"><h4><small>Pin&nbsp;' + i + '</small> <span id="pin-' + i + '">&mdash;</span></h4></div>')
}

var deviceID = Math.floor(Math.random()*99999);
deviceIDElement = document.getElementById('deviceID');
deviceIDElement.innerHTML = deviceID;

var connectionSession = 0

function updatePinDisplay(pin, value, cssClass) {
    document.getElementById('pin-' + pin).innerHTML = value
    document.getElementById('pincontainer-' + pin).className = cssClass
}


function updatePin(pin, value, cssClass) {
    connectionSession.call('com.example.pinUpdated', [deviceID, pin, value]).then(
        function (res) {
            console.log("pinUpdated() result:", res);
            updatePinDisplay(pin, value, cssClass)
        },
        function (err) {
            console.log("pinUpdated() error:", err);
        }
    );
}

 // the URL of the WAMP Router (Crossbar.io)
 //
 var wsuri;
 if (document.location.origin == "file://") {
    wsuri = "ws://127.0.0.1:8080/ws";

 } else {
    wsuri = (document.location.protocol === "http:" ? "ws:" : "wss:") + "//" +
                document.location.host + "/ws";
 }


 // the WAMP connection to the Router
 //
 var connection = new autobahn.Connection({
    url: wsuri,
    realm: "realm1"
 });


 // timers
 //
 var t1, t2;


 // fired when connection is established and session attached
 //
 connection.onopen = function (session, details) {

    console.log("Connected");
    connectionSession = session

    // Register for notifications
    session.call('com.example.registerNewDevice', [deviceID]).then(
          function (res) {
             console.log("registerNewDevice() result:", res);
          },
          function (err) {
             console.log("registerNewDevice() error:", err);
          }
    );

    // Subscribe to new notifications channel
    function on_pin_change (args) {
       var pin = args[0];
       var value = args[1];
       console.log("Received push notification: Pin " + pin + " set to "  + value);
       updatePinDisplay(pin, value, "bg-warning")
    }
    session.subscribe('com.example.' + deviceID, on_pin_change).then(
       function (sub) {
          console.log('subscribed to notifications');
       },
       function (err) {
          console.log('failed to subscribe to notifications', err);
       }
    );


    // SUBSCRIBE to a topic and receive events
    //
    function on_counter (args) {
       var counter = args[0];
       console.log("on_counter() event received with counter " + counter);
    }
    session.subscribe('com.example.oncounter', on_counter).then(
       function (sub) {
          console.log('subscribed to topic');
       },
       function (err) {
          console.log('failed to subscribe to topic', err);
       }
    );


    // PUBLISH an event every second
    //
    t1 = setInterval(function () {

       session.publish('com.example.onhello', ['Publish! Hello from JavaScript (browser)']);
       console.log("published to topic 'com.example.onhello'");
    }, 100000);


    // REGISTER a procedure for remote calling
    //
    function mul2 (args) {
       var x = args[0];
       var y = args[1];
       console.log("mul2() called with " + x + " and " + y);
       return x * y;
    }
    session.register('com.example.mul2', mul2).then(
       function (reg) {
          console.log('procedure registered');
       },
       function (err) {
          console.log('failed to register procedure', err);
       }
    );

    // call remote procedure to inform it of a change
    t3 = setInterval(function () {
        var pin = Math.floor(Math.random() * 99);
        var value = Math.floor(Math.random() * 256);
        updatePin(pin, value)
    }, Math.random() * 500 + 5000000000);

 };


 // fired when connection was lost (or could not be established)
 //
 connection.onclose = function (reason, details) {
    console.log("Connection lost: " + reason);
    if (t1) {
       clearInterval(t1);
       t1 = null;
    }
    if (t2) {
       clearInterval(t2);
       t2 = null;
    }
 }


 // now actually open the connection
 //
 connection.open();