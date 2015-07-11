var board;
var server_on = true;
var msgbox_on = false;

function ping() {
	$.ajax({url: "/api/ping",
	        type: "HEAD",
	        timeout:1000,
	        statusCode: {
	            200: function (response) {
	                server_on = true;
					$("#connectionsymbol").html("&#10003;");
					$("#connectionsymbol").css({"color": "#0F0"});

	            },
	            400: function (response) {
	                server_on = false;
					$("#connectionsymbol").html("&#x2717;");
					$("#connectionsymbol").css({"color": "#F00"});
	            },
	            0: function (response) {
	                server_on = false;
					$("#connectionsymbol").html("&#x2717;");
					$("#connectionsymbol").css({"color": "#F00"});
	            }
	        }
	});
}
function update() {
	if (server_on) {
		$.get("/api/game", function (data) {
			var arr = data.split("\n");
			if (arr[0]=="waiting") {
				$("#msgbox").html("Waiting for next game...");
				$("#msgbox").show("slow");
			}
			else if (arr[0]=="running") {
				$("#msgbox").hide();
				$("#whitename").html(arr[1]);
				$("#blackname").html(arr[2]);
				board.position(arr[3]);
				arr[5].split(";").forEach(function(x) {if (x.length > 0){console.log(x)}});
			}
		});
	}
}

$(document).ready(function() {
	board = new ChessBoard("board", "start");
	setInterval(ping, 500);
	setInterval(update, 1000);
});
