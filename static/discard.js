$(function() {
    var socket = io.connect();

    function animateFlip(card) {
        if($(card).hasClass("backfacing")){
            $(card).transition({queue: false, rotateY: "180deg"});
        } else {
            $(card).transition({queue: false, rotateY: "0deg"});
        }
    }

    function flipCard(card) {
        $(this).toggleClass("backfacing");
        socket.emit("backfacing", $(this).hasClass("backfacing"));
        animateFlip(this);
    }

    function createCard(suit, value) {
        var card = $('<div class="card"><div class="frontface"></div><div class="backface"></div></div>').draggable();

        card.find(".frontface").css("background-position", (-(value-1) * 167.538) + "px " + (-suit * 243.2) + "px");

        card.on("drag", function(ev, ui) {
            socket.emit("move", [ui.position.top, ui.position.left]);
        });

        card.on("dblclick", flipCard);

        return card;
    }

    $("body").append(createCard(0, 7));
    
    socket.emit("request_cards", 2);    	// to be replaced by registration
    
    socket.on("request_cards", function(cards) {
		console.log(cards[0][0]);	
		console.log(cards[1]);	
		var card_list = new Array();
		card_list.push(createCard(cards[0][0], cards[0][1]));
		card_list.push(createCard(cards[1][0], cards[1][1]));		
		$("body").append(card_list);
	});    

    socket.on("move", function(position) {
        $(".card").transition({queue: false, x: position[1], y: position[0]});
    });

    socket.on("backfacing", function(backfacing) {
        console.log("Backfacing", backfacing);
        $(".card").toggleClass("backfacing", backfacing);
        animateFlip($(".card"));
    });
});
