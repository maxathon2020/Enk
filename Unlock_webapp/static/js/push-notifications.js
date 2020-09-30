function displayNotification() {
  if (Notification.permission === 'granted') {  
    navigator.serviceWorker.getRegistration()
    .then(function(reg){
      var options = {
			body: 'Recati al centro ospedaliero entro le ore xx:xx per ritirarla',
			icon: 'static/img/900x900.png',
			image: 'static/img/logo.png',
			badge: 'static/img/96x96.png',
			vibrate: [100, 50, 100],
			data: { primaryKey: 1 },
			actions: [
				{action: 'explore', title: 'Apri la pagina di ritiro', icon: 'static/img/boxwithpin.svg'},
				{action: 'close', title: 'Ignora', icon: 'static/img/close.svg'},
			]
		};
		reg.showNotification('Hai 1 terapia da ritirare oggi', options);
    });
  }
}

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

$(window).on('load', function() {
	displayNotification();
	$("#loader").show()
	cookie_value = getCookie("userid");
	if (cookie_value !== "") {
	    username = cookie_value.split("|")[0];
	    password = cookie_value.split("|")[1];
		navigator.serviceWorker.ready.then(function(reg) {
			reg.pushManager.getSubscription().then(function(sub) {
				if (sub == undefined) {
					// ask user to register for Push
					console.log("YAHOOOOOOOO");
					navigator.serviceWorker.getRegistration()
					.then(function(reg) {
						reg.pushManager.subscribe({
							applicationServerKey: urlB64ToUint8Array('BDJ2BUaPL7xPxajfTVe6eNbC8OdzdUrFfW5XA3R1bo3keufq5sTeH0MQNaPUYQK3BVt5FLtTlVcOoeTDsEsvQGY'),
							userVisibleOnly: true
						}).then(function(sub) {
							// send sub.toJSON() to the server
							subData = sub.toJSON();
							console.log("SWOOSHHHHHHHHHHH");
							$.ajax({
		                        url: '/subscribetopush',
		                        dataType: 'json',
		                        method: 'POST',
		                        data: {endpoint: subData['endpoint'], p256dh: subData['keys']['p256dh'], auth: subData['keys']['auth'], username: username, password: password},
		                        success: function(res) {
		                            $("#loader").hide();
		                        }
		                    });
						});
					}).catch(function(err) {
						console.log(err);
					});
			    } else {
			    	// You have subscription, update the database on your server
			    	subData = sub.toJSON();
			    	$.ajax({
		                url: '/subscribetopush',
		                dataType: 'json',
		                method: 'POST',
		                data: {endpoint: subData['endpoint'], p256dh: subData['keys']['p256dh'], auth: subData['keys']['auth'], username: username, password: password},
		                success: function(res) {
		                    $("#loader").hide();
		                }
		            });
			    }
			});
		});
	} else {
        $("#loader").hide();
        location.hash = "#login";
    }
});

self.addEventListener('push', function(e) {
  var title = e.data.text();
  e.waitUntil(
    self.registration.showNotification(title)
  );
});

self.addEventListener('notificationclick', function(event) {
	console.log("CLICKED");
	var notification = event.notification;
	var action = event.action;
	if (action === 'close') {
		console.log("CLOSED");
		notification.close();
	} else {
		console.log("OPEN_PAGE");
		clients.openWindow('https://www.unlock490.com/');
	}
});