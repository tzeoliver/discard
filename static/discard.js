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

    socket.on("move", function(position) {
        $(".card").transition({queue: false, x: position[1], y: position[0]});
    });

    socket.on("backfacing", function(backfacing) {
        console.log("Backfacing", backfacing);
        $(".card").toggleClass("backfacing", backfacing);
        animateFlip($(".card"));
    });
});
