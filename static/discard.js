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
        var card = $('<div class="card" id="'+suit+'.'+value+'"><div class="frontface"></div><div class="backface"></div></div>').draggable();

        card.find(".frontface").css("background-position", (-(value-1) * 167.538) + "px " + (-suit * 243.2) + "px");
	

        card.on("drag", function(ev, ui) {
            socket.emit("move", [ui.position.top, ui.position.left]);
        });

        card.on("dblclick", flipCard);

        return card;
    }

	function shuffleArray(array) {
		for (var i = array.length - 1; i > 0; i--) {
		    var j = Math.floor(Math.random() * (i + 1));
		    var temp = array[i];
		    array[i] = array[j];
		    array[j] = temp;
		}
		return array;
	}

	function createPack() {
		var cards = new Array();
		for (var i = 0; i < 4; i++){
			for (var j=1; j < 14; j++){
			    cards.push(createCard(i,j));
			}
		}
		cards = shuffleArray(cards);
	
		for (var i=0; i < cards.length; i++) {
			$("body").append(cards[i]);
		}
		console.log(cards);
	}

	createPack();

    socket.on("move", function(position) {
        $(".card").transition({queue: false, x: position[1], y: position[0]});
    });

    socket.on("backfacing", function(backfacing) {
        console.log("Backfacing", backfacing);
        $(".card").toggleClass("backfacing", backfacing);
        animateFlip($(".card"));
    });
});
